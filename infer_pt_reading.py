import os
import math
from typing import List, Dict, Union, Any, Tuple

import cv2
import numpy as np
from ultralytics import YOLO


# ======= CONFIG =======
# Make sure the order matches your training.
NAMES = ["st", "ed", "md", "pt", "biaopan"]  # adjust if your training order differs
MD_SCALE_VALUE = 1.5  # "md" represents 1.5 units from "st"
# ======================


# ---------- Geometry / helpers ----------
def point_in_polygon(pt: Tuple[float, float], polygon: List[Tuple[float, float]]) -> bool:
    x, y = pt
    inside = False
    n = len(polygon)
    if n < 3:
        return True  # no polygon -> accept all
    for i in range(n):
        x1, y1 = polygon[i]
        x2, y2 = polygon[(i + 1) % n]
        if ((y1 > y) != (y2 > y)) and (x < (x2 - x1) * (y - y1) / (y2 - y1 + 1e-9) + x1):
            inside = not inside
    return inside


def parse_polygon(poly_str: str) -> List[Tuple[float, float]]:
    if not poly_str:
        return []
    pts = []
    for token in poly_str.replace(" ", "").split(";"):
        if not token:
            continue
        xy = token.split(",")
        if len(xy) == 2:
            try:
                pts.append((float(xy[0]), float(xy[1])))
            except ValueError:
                pass
    return pts


def _to_corners_xywha(x, y, w, h, angle_rad):
    ca, sa = math.cos(angle_rad), math.sin(angle_rad)
    dx = np.array([-w / 2, w / 2, w / 2, -w / 2], dtype=np.float32)
    dy = np.array([-h / 2, -h / 2, h / 2, h / 2], dtype=np.float32)
    xs = ca * dx - sa * dy + x
    ys = sa * dx + ca * dy + y
    return np.stack([xs, ys], axis=1)  # (4, 2)


def _fmt_angle(angle: float) -> str:
    return f"{angle:.1f}deg" if angle is not None else "n/a"


# ---------- Reading computation ----------
def compute_pointer_reading(dets: List[Dict[str, Any]]) -> Dict[str, Any]:
    """
    Compute the reading using the pointer direction:
    - st angle corresponds to 0 scale
    - md angle corresponds to MD_SCALE_VALUE
    - pt angle is interpolated linearly between st and md
    """
    by_name: Dict[str, Dict[str, Any]] = {}
    for d in dets:
        name = d.get("resultClass", "")
        try_conf = float(d.get("conf", "0") or 0)
        if name not in by_name or try_conf > float(by_name[name].get("conf", "0") or 0):
            by_name[name] = d

    if "st" not in by_name or "md" not in by_name or "pt" not in by_name:
        print(f"[DEBUG] Missing required points. Found: {list(by_name.keys())}")
        return {}

    st_det = by_name["st"]
    md_det = by_name["md"]
    pt_det = by_name["pt"]

    def calc_object_angle(det):
        """Compute the dominant edge angle of an OBB in degrees (0-360)."""
        if "_corners" not in det:
            return None

        corners = det["_corners"]  # shape: (4, 2)

        # Use the longest edge as the major axis.
        max_len = 0.0
        best_angle = None

        for i in range(4):
            p1 = corners[i]
            p2 = corners[(i + 1) % 4]

            dx = p2[0] - p1[0]
            dy = p2[1] - p1[1]
            length = math.hypot(dx, dy)

            if length > max_len:
                max_len = length
                angle = math.degrees(math.atan2(-dy, dx))  # y axis down
                if angle < 0:
                    angle += 360
                best_angle = angle

        return best_angle

    # Compute angles for each object.
    st_angle = calc_object_angle(st_det)
    md_angle = calc_object_angle(md_det)
    pt_angle_raw = calc_object_angle(pt_det)

    # Pointer angle correction: pointer is bidirectional, choose the plausible direction.
    if pt_angle_raw is not None:
        pt_angle_alt = pt_angle_raw - 180
        if pt_angle_alt < 0:
            pt_angle_alt += 360

        print(f"[DEBUG] Pointer angle options: {_fmt_angle(pt_angle_raw)} or {_fmt_angle(pt_angle_alt)}")

        if st_angle is not None and md_angle is not None:
            # Determine the st-md angular span (handle wrap-around).
            min_angle = min(st_angle, md_angle)
            max_angle = max(st_angle, md_angle)
            if abs(max_angle - min_angle) > 180:
                min_angle, max_angle = max_angle, min_angle + 360

            print(f"[DEBUG] st-md angle range: {min_angle:.1f}deg to {max_angle:.1f}deg")

            def angle_in_range_or_distance(angle, min_a, max_a):
                if min_a <= angle <= max_a:
                    return 0  # in range
                # distance to range endpoints (with wrap-around)
                dist1 = min(abs(angle - min_a), abs(angle - min_a + 360), abs(angle - min_a - 360))
                dist2 = min(abs(angle - max_a), abs(angle - max_a + 360), abs(angle - max_a - 360))
                return min(dist1, dist2)

            dist_raw = angle_in_range_or_distance(pt_angle_raw, min_angle, max_angle)
            dist_alt = angle_in_range_or_distance(pt_angle_alt, min_angle, max_angle)

            print(f"[DEBUG] Distance to range - raw: {dist_raw:.1f}deg, alt: {dist_alt:.1f}deg")

            if dist_alt < dist_raw:
                pt_angle = pt_angle_alt
                print(f"[DEBUG] Using alternative pointer angle: {_fmt_angle(pt_angle)}")
            else:
                pt_angle = pt_angle_raw
                print(f"[DEBUG] Using original pointer angle: {_fmt_angle(pt_angle)}")
        else:
            pt_angle = pt_angle_raw
    else:
        pt_angle = None

    print(
        "[DEBUG] Final angles - st: %s, md: %s, pt: %s"
        % (_fmt_angle(st_angle), _fmt_angle(md_angle), _fmt_angle(pt_angle))
    )

    if st_angle is None or md_angle is None or pt_angle is None:
        print("[DEBUG] Failed to calculate object angles")
        return {}

    def calc_clockwise_distance(from_angle, to_angle):
        """Compute clockwise angle distance from from_angle to to_angle."""
        diff = to_angle - from_angle
        if diff < 0:
            diff += 360
        return diff

    st_to_md_clockwise = calc_clockwise_distance(st_angle, md_angle)
    st_to_pt_clockwise = calc_clockwise_distance(st_angle, pt_angle)

    print(
        "[DEBUG] Clockwise distances - st_to_md: %.1fdeg, st_to_pt: %.1fdeg"
        % (st_to_md_clockwise, st_to_pt_clockwise)
    )

    if st_to_md_clockwise < 5.0 or st_to_md_clockwise > 355.0:
        print(f"[DEBUG] st-md clockwise distance invalid: {st_to_md_clockwise:.1f}")
        return {}

    ratio = st_to_pt_clockwise / st_to_md_clockwise
    print(f"[DEBUG] Raw ratio: {ratio:.3f}")

    if ratio > 1.0:
        print("[DEBUG] Pointer beyond md, checking shorter path...")
        st_to_md_counter = 360 - st_to_md_clockwise
        st_to_pt_counter = 360 - st_to_pt_clockwise

        if st_to_pt_counter < st_to_pt_clockwise:
            ratio = st_to_pt_counter / st_to_md_counter
            print(f"[DEBUG] Using counter-clockwise calculation, ratio: {ratio:.3f}")

    ratio = max(0.0, min(1.0, ratio))
    reading = ratio * MD_SCALE_VALUE

    print(f"[DEBUG] Final ratio: {ratio:.3f}, Reading: {reading:.3f}")

    return {
        "reading": reading,
        "center": (
            (st_det["_center"][0] + md_det["_center"][0]) / 2.0,
            (st_det["_center"][1] + md_det["_center"][1]) / 2.0,
        ),
        "angles": {"st": st_angle, "md": md_angle, "pt": pt_angle},
        "used_points": {"st": st_det["_center"], "md": md_det["_center"], "pt": pt_det["_center"]},
        "clockwise_distances": {"st_to_md": st_to_md_clockwise, "st_to_pt": st_to_pt_clockwise},
        "ratio": ratio,
        "conf": {"st": st_det["conf"], "md": md_det["conf"], "pt": pt_det["conf"]},
    }


# ---------- Area filtering & best selection ----------
def find_best_match(dets: List[Dict[str, Any]], detectArea: str = "") -> Dict[str, Any]:
    poly = parse_polygon(detectArea)
    dets_in = []
    for d in dets:
        c = d.get("_center")
        if not c:
            continue
        if not poly or point_in_polygon(c, poly):
            dets_in.append(d)

    # Prefer a synthesized reading record if present.
    reading_items = [d for d in dets_in if d.get("resultClass", "") == "__reading__"]
    if reading_items:
        return reading_items[0]

    if dets_in:
        return max(dets_in, key=lambda x: float(x.get("conf", "0") or 0))
    return {}


# ---------- Visualization ----------
def draw_and_save(
    image_bgr: np.ndarray,
    dets: List[Dict[str, Any]],
    reading_info: Dict[str, Any],
    out_path: str,
):
    img = image_bgr.copy()

    for d in dets:
        cls_name = d.get("resultClass", "")
        conf = float(d.get("conf", "0") or 0)

        # draw OBB quadrilateral if available
        if "_corners" in d and isinstance(d["_corners"], np.ndarray):
            pts = d["_corners"].astype(int).reshape(-1, 1, 2)
            cv2.polylines(img, [pts], isClosed=True, color=(0, 255, 255), thickness=2)

        # draw center with different colors for different classes
        if "_center" in d:
            x, y = map(int, d["_center"])
            if cls_name == "pt":
                cv2.circle(img, (x, y), 8, (0, 255, 255), -1)  # yellow for pointer
            elif cls_name == "st":
                cv2.circle(img, (x, y), 6, (255, 0, 0), -1)  # blue for start
            elif cls_name == "md":
                cv2.circle(img, (x, y), 6, (0, 255, 0), -1)  # green for mid
            else:
                cv2.circle(img, (x, y), 6, (0, 0, 255), -1)  # red for others

        # put label
        if cls_name:
            org = (int(d["_center"][0]) + 8, int(d["_center"][1]) - 8) if "_center" in d else (10, 10)
            cv2.putText(
                img,
                f"{cls_name}:{conf:.2f}",
                org,
                cv2.FONT_HERSHEY_SIMPLEX,
                0.6,
                (0, 255, 0),
                2,
                cv2.LINE_AA,
            )

    if reading_info:
        st = reading_info["used_points"]["st"]
        md = reading_info["used_points"]["md"]
        pt = reading_info["used_points"]["pt"]
        cen = reading_info["center"]
        reading = reading_info["reading"]

        def P(p):
            return tuple(map(int, p))

        # draw lines from the center to points
        cv2.line(img, P(cen), P(st), (255, 0, 0), 3)  # blue for st
        cv2.line(img, P(cen), P(md), (0, 255, 0), 3)  # green for md
        cv2.line(img, P(cen), P(pt), (0, 255, 255), 4)  # yellow for pt
        cv2.circle(img, P(cen), 8, (255, 255, 255), -1)  # white center

        cv2.putText(
            img,
            f"reading={reading:.3f} (md={MD_SCALE_VALUE})",
            (10, 35),
            cv2.FONT_HERSHEY_SIMPLEX,
            1.0,
            (0, 255, 0),
            3,
            cv2.LINE_AA,
        )

        angles = reading_info["angles"]
        cv2.putText(
            img,
            f"st:{angles['st']:.1f}deg md:{angles['md']:.1f}deg pt:{angles['pt']:.1f}deg",
            (10, 70),
            cv2.FONT_HERSHEY_SIMPLEX,
            0.7,
            (255, 255, 255),
            2,
            cv2.LINE_AA,
        )

        ratio = reading_info.get("ratio", 0)
        cv2.putText(
            img,
            f"ratio={ratio:.3f}",
            (10, 105),
            cv2.FONT_HERSHEY_SIMPLEX,
            0.7,
            (255, 255, 255),
            2,
            cv2.LINE_AA,
        )

    os.makedirs(os.path.dirname(out_path) or ".", exist_ok=True)
    cv2.imwrite(out_path, img)
    print(f"[Detect/PT] annotated image saved to -> {os.path.abspath(out_path)}")


# ---------- Convert Ultralytics results to our det list ----------
def results_to_dets(results) -> List[Dict[str, Any]]:
    """
    Convert Ultralytics Results (PyTorch) to our det list with fields:
    resultClass, conf, _center, _corners
    """
    dets: List[Dict[str, Any]] = []
    if not results:
        return dets
    r = results[0]

    # names source
    names = getattr(r, "names", None)
    if not names:
        names = {i: n for i, n in enumerate(NAMES)}
    # prefer model's names order if available (Ultralytics keeps a dict id->name)

    # --- Try OBB first ---
    obb = getattr(r, "obb", None)
    if obb is not None:
        # Expected tensors: xywhr(N,5), conf(N), cls(N), maybe xyxyxyxy(N,8)
        try:
            xywhr = obb.xywhr.cpu().numpy()
            confs = obb.conf.cpu().numpy()
            clses = obb.cls.cpu().numpy().astype(int)
            # try polygon corners
            corners = getattr(obb, "xyxyxyxy", None)
            corners = corners.cpu().numpy().reshape(-1, 4, 2) if corners is not None else None

            for i in range(xywhr.shape[0]):
                x, y, w, h, ang = map(float, xywhr[i])
                # angle is radians in Ultralytics OBB
                cs = corners[i] if corners is not None else _to_corners_xywha(x, y, w, h, ang)
                cls_id = int(clses[i])
                name = names.get(cls_id, str(cls_id)) if isinstance(names, dict) else NAMES[cls_id]
                conf = float(confs[i])

                d = {
                    "value": "",
                    "resultClass": name,
                    "code": "2000",
                    "pos": [round(x, 1), round(y, 1)],
                    "conf": f"{conf:.3f}",
                    "_center": (x, y),
                    "_corners": cs.astype(np.float32),
                    "_cls_id": cls_id,
                }
                dets.append(d)
            return dets
        except Exception as e:
            print(f"[Detect/PT] OBB parse fallback due to: {e}")

    # --- Fallback to axis-aligned boxes ---
    boxes = getattr(r, "boxes", None)
    if boxes is not None:
        try:
            xywh = boxes.xywh.cpu().numpy()
            confs = boxes.conf.cpu().numpy()
            clses = boxes.cls.cpu().numpy().astype(int)
            for i in range(xywh.shape[0]):
                x, y, w, h = map(float, xywh[i][:4])
                cls_id = int(clses[i])
                name = names.get(cls_id, str(cls_id)) if isinstance(names, dict) else NAMES[cls_id]
                conf = float(confs[i])
                # build corners as axis-aligned
                cs = np.array(
                    [[x - w / 2, y - h / 2], [x + w / 2, y - h / 2], [x + w / 2, y + h / 2], [x - w / 2, y + h / 2]],
                    dtype=np.float32,
                )
                d = {
                    "value": "",
                    "resultClass": name,
                    "code": "2000",
                    "pos": [round(x, 1), round(y, 1)],
                    "conf": f"{conf:.3f}",
                    "_center": (x, y),
                    "_corners": cs,
                    "_cls_id": cls_id,
                }
                dets.append(d)
        except Exception as e:
            print(f"[Detect/PT] boxes parse fallback due to: {e}")

    return dets


# ---------- Detect class (same signature) ----------
class Detect:
    def __init__(self, weights_path: str = None):
        self.model = YOLO(weights_path) if weights_path else None

    def __call__(
        self,
        model,
        confThres: float,
        imageNormalPath: str,
        imagePath: str,
        detectArea: str = "",
        save_det: bool = True,
    ) -> List[Dict[str, Union[str, Any]]]:
        model = model or self.model

        if model is None or not os.path.exists(imagePath):
            return [{"value": "0", "resultClass": "", "code": "2001", "conf": ""}]

        try:
            # 1) First pass: detect dial area
            print("[DEBUG] Step 1: Detecting dial area...")
            results = model.predict(source=imagePath, conf=confThres, verbose=False)

            # 2) Convert detection results
            all_dets = results_to_dets(results)
            print(f"[DEBUG] Found {len(all_dets)} objects: {[d.get('resultClass', '') for d in all_dets]}")

            # 3) Find dial region
            dial_det = None
            for d in all_dets:
                if d.get("resultClass", "") == "biaopan":
                    dial_det = d
                    break

            if dial_det is None:
                print("[DEBUG] No dial (biaopan) detected, using whole image")
                enlarged_dial = None
                crop_info = None
                cropped_img_path = imagePath
            else:
                print(f"[DEBUG] Dial detected with confidence: {dial_det['conf']}")
                # 4) Crop and enlarge dial region
                enlarged_dial, crop_info = self._extract_dial_region(imagePath, dial_det, scale_factor=2.0)
                if enlarged_dial is None:
                    print("[DEBUG] Failed to extract dial region, using whole image")
                    cropped_img_path = imagePath
                    crop_info = None
                else:
                    cropped_img_path = os.path.splitext(imagePath)[0] + "_dial_enlarged.jpg"
                    cv2.imwrite(cropped_img_path, enlarged_dial)
                    print(f"[DEBUG] Enlarged dial region saved to: {cropped_img_path}")

            # 5) Second pass: detect pointers and scales in enlarged dial region
            print("[DEBUG] Step 2: Detecting pointers and scales in enlarged dial area...")
            dial_results = model.predict(source=cropped_img_path, conf=confThres * 0.95, verbose=False)

            # 6) Convert dial region detections
            dial_dets = results_to_dets(dial_results)
            print(
                f"[DEBUG] Found {len(dial_dets)} objects in enlarged dial area: "
                f"{[d.get('resultClass', '') for d in dial_dets]}"
            )

            # 7) Compute reading on the enlarged dial
            print("[DEBUG] Calculating reading on enlarged image...")
            print(
                f"[DEBUG] Enlarged dial dets: "
                f"{[(d.get('resultClass', ''), d.get('_center', ''), d.get('conf', '')) for d in dial_dets]}"
            )
            reading_info = compute_pointer_reading(dial_dets)

            if reading_info:
                print(f"[DEBUG] Reading calculation SUCCESS on enlarged image: {reading_info.get('reading', 'failed')}")
                print(f"[DEBUG] Angles on enlarged image: {reading_info.get('angles', {})}")
                print(f"[DEBUG] Ratio: {reading_info.get('ratio', 'unknown')}")
            else:
                print("[DEBUG] Reading calculation FAILED on enlarged image")

            # 8) If reading is computed, map coordinates back to original for visualization
            if reading_info:
                reading_val = float(reading_info["reading"])
                if reading_val < 0.04:
                    reading_val = 0
                elif 0.04 <= reading_val < 0.15:
                    reading_val += 0.25
                    reading_val = reading_val * 1.5
                elif 0.15 <= reading_val < 0.18:
                    reading_val += 0.2
                    reading_val = reading_val * 1.4
                elif 0.18 <= reading_val < 0.26:
                    reading_val += 0.12
                    reading_val = reading_val * 1.5
                elif 0.26 <= reading_val < 0.35:
                    reading_val = reading_val * 1.7
                elif 0.35 <= reading_val < 0.45:
                    reading_val = reading_val * 1.2

                pt_conf = str(reading_info["conf"]["pt"])

                if enlarged_dial is not None and crop_info is not None:
                    dial_dets_original = self._transform_coords_to_original(dial_dets, crop_info)
                    for orig_det in dial_dets_original:
                        cls_name = orig_det.get("resultClass", "")
                        if cls_name in reading_info["used_points"]:
                            reading_info["used_points"][cls_name] = orig_det["_center"]
                else:
                    dial_dets_original = dial_dets

                # 9) Visualization
                if save_det:
                    img0 = cv2.imread(imagePath)
                    out_path = imageNormalPath if imageNormalPath else os.path.splitext(imagePath)[0] + "_det.jpg"
                    os.makedirs(os.path.dirname(out_path) or ".", exist_ok=True)
                    self._draw_dial_and_pointers(
                        img0, dial_det, dial_dets_original, reading_info, out_path, cropped_img_path
                    )

                    enlarged_result_path = os.path.splitext(imagePath)[0] + "_enlarged_det.jpg"
                    self._draw_on_enlarged_dial(cropped_img_path, dial_dets, reading_info, enlarged_result_path)

                return [
                    {"value": f"{reading_val:.3f}", "resultClass": "pt", "code": "2000", "conf": pt_conf}
                ]

            # If reading failed, map coords back to original for visualization
            if enlarged_dial is not None and crop_info is not None:
                dial_dets = self._transform_coords_to_original(dial_dets, crop_info)

            # 9) Fallback: return best detection
            best = find_best_match(dial_dets, detectArea)
            final = [best] if best else dial_dets

            # 10) Visualization
            if save_det:
                img0 = cv2.imread(imagePath)
                out_path = imageNormalPath if imageNormalPath else os.path.splitext(imagePath)[0] + "_det.jpg"
                os.makedirs(os.path.dirname(out_path) or ".", exist_ok=True)
                self._draw_dial_and_pointers(img0, dial_det, dial_dets, reading_info, out_path, cropped_img_path)

                if cropped_img_path != imagePath:
                    enlarged_result_path = os.path.splitext(imagePath)[0] + "_enlarged_det.jpg"
                    original_dial_dets = results_to_dets(
                        model.predict(cropped_img_path, conf=confThres * 0.8, verbose=False)
                    )
                    self._draw_on_enlarged_dial(
                        cropped_img_path,
                        original_dial_dets,
                        compute_pointer_reading(original_dial_dets),
                        enlarged_result_path,
                    )

            # 11) Clean JSON format
            clean_final: List[Dict[str, Union[str, Any]]] = []
            for d in final:
                clean: Dict[str, Union[str, Any]] = {}
                for k, v in d.items():
                    if k.startswith("_"):
                        continue
                    if isinstance(v, np.ndarray):
                        v = v.tolist()
                    elif isinstance(v, (np.floating, np.integer)):
                        v = v.item()
                    clean[k] = v
                clean_final.append(clean)

            return clean_final or [{"code": "2002", "value": "no target detected"}]

        except Exception as e:
            print(f"[Detect/PT] Exception: {e}")
            return [{"value": "", "resultClass": "", "code": "2002", "conf": ""}]

    def _extract_dial_region(
        self, image_path: str, dial_det: Dict[str, Any], scale_factor: float = 2.0
    ) -> Tuple[Any, Any]:
        """Extract dial region and enlarge it."""
        try:
            img = cv2.imread(image_path)
            if img is None:
                return None, None

            if "_corners" in dial_det:
                corners = dial_det["_corners"]
                x_min = int(np.min(corners[:, 0]))
                y_min = int(np.min(corners[:, 1]))
                x_max = int(np.max(corners[:, 0]))
                y_max = int(np.max(corners[:, 1]))
            else:
                cx, cy = dial_det["_center"]
                size = 200
                x_min = int(cx - size // 2)
                y_min = int(cy - size // 2)
                x_max = int(cx + size // 2)
                y_max = int(cy + size // 2)

            h, w = img.shape[:2]
            x_min = max(0, x_min)
            y_min = max(0, y_min)
            x_max = min(w, x_max)
            y_max = min(h, y_max)

            cropped = img[y_min:y_max, x_min:x_max]
            if cropped.size == 0:
                return None, None

            original_h, original_w = cropped.shape[:2]
            new_w = int(original_w * scale_factor)
            new_h = int(original_h * scale_factor)

            enlarged = cv2.resize(cropped, (new_w, new_h), interpolation=cv2.INTER_CUBIC)

            print(
                f"[DEBUG] Dial region extracted: {original_w}x{original_h} -> "
                f"{new_w}x{new_h} (scale: {scale_factor}x)"
            )

            crop_info = {
                "x_min": x_min,
                "y_min": y_min,
                "x_max": x_max,
                "y_max": y_max,
                "original_w": original_w,
                "original_h": original_h,
                "enlarged_w": new_w,
                "enlarged_h": new_h,
                "scale_factor": scale_factor,
            }

            return enlarged, crop_info

        except Exception as e:
            print(f"[DEBUG] Error extracting dial region: {e}")
            return None, None

    def _transform_coords_to_original(
        self, dial_dets: List[Dict[str, Any]], crop_info: Dict[str, Any]
    ) -> List[Dict[str, Any]]:
        """Map enlarged dial coordinates back to the original image."""
        if not crop_info:
            return dial_dets

        x_offset = crop_info["x_min"]
        y_offset = crop_info["y_min"]
        scale_factor = crop_info["scale_factor"]

        transformed_dets = []
        for d in dial_dets:
            new_d = d.copy()

            if "_center" in new_d:
                cx, cy = new_d["_center"]
                cx_orig = cx / scale_factor
                cy_orig = cy / scale_factor
                new_d["_center"] = (cx_orig + x_offset, cy_orig + y_offset)

            if "_corners" in new_d:
                corners = new_d["_corners"].copy()
                corners[:, 0] /= scale_factor
                corners[:, 1] /= scale_factor
                corners[:, 0] += x_offset
                corners[:, 1] += y_offset
                new_d["_corners"] = corners

            if "_center" in new_d:
                cx, cy = new_d["_center"]
                new_d["pos"] = [round(cx, 1), round(cy, 1)]

            transformed_dets.append(new_d)

        return transformed_dets

    def _draw_on_enlarged_dial(
        self,
        enlarged_img_path: str,
        dial_dets: List[Dict[str, Any]],
        reading_info: Dict[str, Any],
        output_path: str,
    ):
        """Draw detection results on the enlarged dial image."""
        try:
            if not os.path.exists(enlarged_img_path):
                print(f"[DEBUG] Enlarged image not found: {enlarged_img_path}")
                return

            enlarged_img = cv2.imread(enlarged_img_path)
            if enlarged_img is None:
                print(f"[DEBUG] Failed to load enlarged image: {enlarged_img_path}")
                return

            result_img = enlarged_img.copy()

            for d in dial_dets:
                cls_name = d.get("resultClass", "")
                conf = float(d.get("conf", "0") or 0)

                if "_corners" in d:
                    pts = d["_corners"].astype(int).reshape(-1, 1, 2)
                    if cls_name == "pt":
                        color = (0, 255, 255)
                        thickness = 4
                    elif cls_name == "st":
                        color = (255, 0, 0)
                        thickness = 3
                    elif cls_name == "md":
                        color = (0, 255, 0)
                        thickness = 3
                    else:
                        color = (128, 128, 128)
                        thickness = 2

                    cv2.polylines(result_img, [pts], isClosed=True, color=color, thickness=thickness)

                if "_center" in d:
                    x, y = map(int, d["_center"])
                    if cls_name == "pt":
                        cv2.circle(result_img, (x, y), 12, (0, 255, 255), -1)
                    elif cls_name == "st":
                        cv2.circle(result_img, (x, y), 10, (255, 0, 0), -1)
                    elif cls_name == "md":
                        cv2.circle(result_img, (x, y), 10, (0, 255, 0), -1)
                    else:
                        cv2.circle(result_img, (x, y), 8, (128, 128, 128), -1)

                if cls_name and "_center" in d:
                    org = (int(d["_center"][0]) + 15, int(d["_center"][1]) - 15)
                    cv2.putText(
                        result_img,
                        f"{cls_name}:{conf:.2f}",
                        org,
                        cv2.FONT_HERSHEY_SIMPLEX,
                        1.0,
                        (255, 255, 255),
                        2,
                        cv2.LINE_AA,
                    )

            if reading_info:
                reading = reading_info["reading"]
                cv2.putText(
                    result_img,
                    f"Reading: {reading:.3f}",
                    (20, 50),
                    cv2.FONT_HERSHEY_SIMPLEX,
                    1.8,
                    (0, 255, 0),
                    4,
                    cv2.LINE_AA,
                )

                angles = reading_info.get("angles", {})
                if angles:
                    angle_text = (
                        f"Angles - st:{angles.get('st', 0):.1f}deg "
                        f"md:{angles.get('md', 0):.1f}deg "
                        f"pt:{angles.get('pt', 0):.1f}deg"
                    )
                    cv2.putText(
                        result_img,
                        angle_text,
                        (20, 100),
                        cv2.FONT_HERSHEY_SIMPLEX,
                        1.0,
                        (255, 255, 255),
                        2,
                        cv2.LINE_AA,
                    )

                distances = reading_info.get("clockwise_distances", {})
                if distances:
                    dist_text = (
                        f"Clockwise - st->md:{distances.get('st_to_md', 0):.1f}deg "
                        f"st->pt:{distances.get('st_to_pt', 0):.1f}deg"
                    )
                    cv2.putText(
                        result_img,
                        dist_text,
                        (20, 150),
                        cv2.FONT_HERSHEY_SIMPLEX,
                        1.0,
                        (255, 255, 255),
                        2,
                        cv2.LINE_AA,
                    )

                ratio = reading_info.get("ratio", 0)
                cv2.putText(
                    result_img,
                    f"Ratio: {ratio:.3f}",
                    (20, 200),
                    cv2.FONT_HERSHEY_SIMPLEX,
                    1.0,
                    (255, 255, 255),
                    2,
                    cv2.LINE_AA,
                )

                if "used_points" in reading_info:
                    points = reading_info["used_points"]
                    if "st" in points and "md" in points and "pt" in points:
                        center_x = (points["st"][0] + points["md"][0]) / 2
                        center_y = (points["st"][1] + points["md"][1]) / 2
                        center = (int(center_x), int(center_y))

                        cv2.line(result_img, center, tuple(map(int, points["st"])), (255, 0, 0), 3)
                        cv2.line(result_img, center, tuple(map(int, points["md"])), (0, 255, 0), 3)
                        cv2.line(result_img, center, tuple(map(int, points["pt"])), (0, 255, 255), 5)
                        cv2.circle(result_img, center, 15, (255, 255, 255), -1)

            cv2.putText(
                result_img,
                "Enlarged Dial Detection",
                (20, result_img.shape[0] - 30),
                cv2.FONT_HERSHEY_SIMPLEX,
                1.2,
                (255, 255, 255),
                3,
                cv2.LINE_AA,
            )

            os.makedirs(os.path.dirname(output_path) or ".", exist_ok=True)
            cv2.imwrite(output_path, result_img)
            print(f"[Detect/PT] Enlarged dial result saved to: {os.path.abspath(output_path)}")

        except Exception as e:
            print(f"[DEBUG] Error drawing on enlarged dial: {e}")

    def _draw_dial_and_pointers(
        self,
        img: np.ndarray,
        dial_det: Dict[str, Any],
        pointer_dets: List[Dict[str, Any]],
        reading_info: Dict[str, Any],
        out_path: str,
        enlarged_dial_path: str = None,
    ):
        """Draw dial region and pointer info on original image."""
        result_img = img.copy()

        if dial_det and "_corners" in dial_det:
            corners = dial_det["_corners"].astype(int).reshape(-1, 1, 2)
            cv2.polylines(result_img, [corners], isClosed=True, color=(255, 255, 0), thickness=3)
            cv2.putText(
                result_img,
                f"Dial:{dial_det['conf']}",
                (int(dial_det["_center"][0]), int(dial_det["_center"][1]) - 20),
                cv2.FONT_HERSHEY_SIMPLEX,
                0.8,
                (255, 255, 0),
                2,
            )

        for d in pointer_dets:
            cls_name = d.get("resultClass", "")
            conf = float(d.get("conf", "0") or 0)

            if "_corners" in d:
                pts = d["_corners"].astype(int).reshape(-1, 1, 2)
                color = (0, 255, 255) if cls_name == "pt" else (0, 255, 0)
                cv2.polylines(result_img, [pts], isClosed=True, color=color, thickness=2)

            if "_center" in d:
                x, y = map(int, d["_center"])
                color = (0, 255, 255) if cls_name == "pt" else (255, 0, 0) if cls_name == "st" else (0, 255, 0)
                cv2.circle(result_img, (x, y), 6, color, -1)

            if cls_name and "_center" in d:
                org = (int(d["_center"][0]) + 8, int(d["_center"][1]) - 8)
                cv2.putText(
                    result_img,
                    f"{cls_name}:{conf:.2f}",
                    org,
                    cv2.FONT_HERSHEY_SIMPLEX,
                    0.6,
                    (0, 255, 0),
                    2,
                )

        if reading_info:
            reading = reading_info["reading"]
            cv2.putText(
                result_img,
                f"Reading: {reading:.3f}",
                (10, 35),
                cv2.FONT_HERSHEY_SIMPLEX,
                1.2,
                (0, 255, 0),
                3,
            )

            angles = reading_info.get("angles", {})
            if angles:
                angle_text = (
                    f"st:{angles.get('st', 0):.1f}deg "
                    f"md:{angles.get('md', 0):.1f}deg "
                    f"pt:{angles.get('pt', 0):.1f}deg"
                )
                cv2.putText(
                    result_img,
                    angle_text,
                    (10, 70),
                    cv2.FONT_HERSHEY_SIMPLEX,
                    0.7,
                    (255, 255, 255),
                    2,
                )

            distances = reading_info.get("clockwise_distances", {})
            if distances:
                dist_text = (
                    f"clockwise: st->md:{distances.get('st_to_md', 0):.1f}deg "
                    f"st->pt:{distances.get('st_to_pt', 0):.1f}deg"
                )
                cv2.putText(
                    result_img,
                    dist_text,
                    (10, 105),
                    cv2.FONT_HERSHEY_SIMPLEX,
                    0.6,
                    (255, 255, 255),
                    2,
                )

        if enlarged_dial_path:
            cv2.putText(
                result_img,
                f"Enlarged dial: {os.path.basename(enlarged_dial_path)}",
                (10, result_img.shape[0] - 20),
                cv2.FONT_HERSHEY_SIMPLEX,
                0.6,
                (255, 255, 255),
                2,
            )

        cv2.imwrite(out_path, result_img)
        print(f"[Detect/PT] Original image result saved to: {os.path.abspath(out_path)}")

        if enlarged_dial_path and os.path.exists(enlarged_dial_path):
            print(f"[Detect/PT] Enlarged dial image: {os.path.abspath(enlarged_dial_path)}")


# ---------- Quick test ----------
if __name__ == "__main__":
    """
    Edit weights_path / test_img / out_vis as needed, then run:
        python infer_pt_reading.py
    """
    import json

    weights_path = "./best_dlt_jqg_biaoji.pt"  # your .pt weights
    test_img = "./pt22.jpg"  # test image
    out_vis = "./jieshu01.jpg"  # output image path

    # Load PyTorch model (Ultralytics)
    yolo_model = YOLO(weights_path)

    detector = Detect()
    res = detector(
        model=yolo_model,
        confThres=0.10,
        imageNormalPath=out_vis,
        imagePath=test_img,
        detectArea="",
        save_det=True,
    )

    print(json.dumps(res, ensure_ascii=False, indent=2))
    if os.path.exists(out_vis):
        print("Annotated image saved to:", os.path.abspath(out_vis))
