#!/usr/bin/env python3
# -*- coding: utf-8 -*-

import os
import cv2
import time
import json
import argparse
import numpy as np
import onnxruntime as ort
from typing import Tuple, List, Dict, Any, Union
from pathlib import Path

# 模型配置
MODEL_PATH = r"E:\SZBJ\runs\detect\train84\weights\best.onnx"

# 模型只有一个输出类别：smoke。
CUSTOM_CLASSES = ["smoke"]
SMOKE_CLASS_ID = 0

INPUT_SIZE = (960, 960)


def preprocess_image(img_path: str,
                     input_size: Tuple[int, int] = INPUT_SIZE
                     ) -> Tuple[np.ndarray, np.ndarray,
                                Tuple[int, int], Tuple[int, int, float]]:
    """图像预处理"""
    img = cv2.imread(img_path)
    if img is None:
        raise FileNotFoundError(f"无法读取图像: {img_path}")

    h0, w0 = img.shape[:2]
    ih, iw = input_size
    ratio = min(ih / h0, iw / w0)
    nh, nw = int(h0 * ratio), int(w0 * ratio)

    resized = cv2.resize(img, (nw, nh), interpolation=cv2.INTER_LINEAR)
    canvas = np.zeros((ih, iw, 3), dtype=np.uint8)
    dx, dy = (iw - nw) // 2, (ih - nh) // 2
    canvas[dy:dy + nh, dx:dx + nw] = resized

    canvas = cv2.cvtColor(canvas, cv2.COLOR_BGR2RGB).astype(np.float32) / 255.0
    tensor = np.transpose(canvas, (2, 0, 1))[None]  # NCHW

    return tensor, img, (h0, w0), (dx, dy, ratio)


def compute_iou(b1, b2):
    """计算IoU"""
    x1, y1, x2, y2 = b1
    x3, y3, x4, y4 = b2
    inter_w = max(0, min(x2, x4) - max(x1, x3))
    inter_h = max(0, min(y2, y4) - max(y1, y3))
    inter = inter_w * inter_h
    if inter == 0:
        return 0.0
    s1 = (x2 - x1) * (y2 - y1)
    s2 = (x4 - x3) * (y4 - y3)
    return inter / (s1 + s2 - inter)


def nms(dets, thr=0.5):
    """非极大值抑制"""
    dets = sorted(dets, key=lambda d: d["conf"], reverse=True)
    keep = []
    for d in dets:
        flag = True
        for k in keep:
            if k["resultClass"] != d["resultClass"]:
                continue
            iou = compute_iou(
                [d["pos"][0]["areas"][0]["x"], d["pos"][0]["areas"][0]["y"],
                 d["pos"][0]["areas"][1]["x"], d["pos"][0]["areas"][1]["y"]],
                [k["pos"][0]["areas"][0]["x"], k["pos"][0]["areas"][0]["y"],
                 k["pos"][0]["areas"][1]["x"], k["pos"][0]["areas"][1]["y"]]
            )
            if iou > thr:
                flag = False
                break
        if flag:
            keep.append(d)
    return keep


def postprocess(preds: np.ndarray,
                size_org: Tuple[int, int],
                trans: Tuple[int, int, float],
                conf_thr: float = 0.25) -> List[Dict[str, Any]]:
    """后处理"""
    dx, dy, r = trans
    h0, w0 = size_org
    results = []

    if preds.ndim == 3:
        preds = preds[0].transpose(1, 0) if preds.shape[1] <= preds.shape[2] else preds[0]

    for p in preds:
        box, scores = p[:4], p[4:]
        if len(scores) == 0:
            continue

        # 单类别模型中，唯一的输出分数就是 smoke 的置信度。
        cid = SMOKE_CLASS_ID
        conf = float(scores[0])
        if conf < conf_thr:
            continue

        x, y, w, h = box
        x = (x - dx) / r
        y = (y - dy) / r
        w, h = w / r, h / r
        l, t = int(max(0, x - w / 2)), int(max(0, y - h / 2))
        rgt, btm = int(min(w0, x + w / 2)), int(min(h0, y + h / 2))
        if rgt - l < 3 or btm - t < 3:
            continue

        results.append({
            "resultClass": cid,
            "code": "2000",
            "value": CUSTOM_CLASSES[cid],
            "pos": [{"areas": [{"x": l, "y": t}, {"x": rgt, "y": btm}]}],
            "conf": float(f"{conf:.4f}")
        })

    return nms(results, 0.5)


def draw_and_save(image: np.ndarray, dets: List[Dict[str, Any]], save_path: str):
    """绘制检测结果并保存"""
    palette = [(255, 0, 0), (0, 255, 0), (0, 128, 255), (255, 0, 255),
               (0, 255, 255), (255, 255, 0)]
    vis = image.copy()
    for d in dets:
        cid = d["resultClass"]
        c = palette[cid % len(palette)]
        (l, t) = d["pos"][0]["areas"][0].values()
        (r, b) = d["pos"][0]["areas"][1].values()
        cv2.rectangle(vis, (l, t), (r, b), c, 2)
        label = f'{d["value"]} {d["conf"]:.2f}'
        tw, th = cv2.getTextSize(label, 0, 0.5, 1)[0]
        cv2.rectangle(vis, (l, t - th - 4), (l + tw, t), c, -1)
        cv2.putText(vis, label, (l, t - 2), 0, 0.5, (255, 255, 255), 1)

    os.makedirs(os.path.dirname(save_path), exist_ok=True)
    cv2.imwrite(save_path, vis)


def find_best_match(dets, target_area: str):
    """在指定区域内寻找最佳匹配"""
    if not (target_area and dets):
        return None

    try:
        x1, y1, x2, y2 = map(int, target_area.split(","))
    except Exception:
        print(f"目标区域格式错误: {target_area}，应为x1,y1,x2,y2")
        return None

    best, best_iou = None, -1.0
    for d in dets:
        l, t = d["pos"][0]["areas"][0].values()
        r, b = d["pos"][0]["areas"][1].values()
        iou = compute_iou([x1, y1, x2, y2], [l, t, r, b])
        if iou > best_iou:
            best_iou, best = iou, d

    return best if best_iou > 0.1 else None


def result_handle(results: Any, code: str) -> List[Dict[str, Union[str, Any]]]:
    """结果处理"""
    return [{"results": results, "code": code}]


def load_model(model_path: str = MODEL_PATH):
    """加载ONNX模型"""
    if not os.path.exists(model_path):
        print(f"模型文件不存在: {model_path}")
        return None

    try:
        providers = ['CUDAExecutionProvider', 'CPUExecutionProvider']
        model = ort.InferenceSession(model_path, providers=providers)
        print(f"模型加载成功: {model_path}")
        print(f"使用提供者: {model.get_providers()}")
        return model
    except Exception as e:
        print(f"模型加载失败: {e}")
        return None


class Detect:
    """检测器类"""

    def __init__(self):
        """初始化检测器"""
        pass

    def __call__(self,
                 model,
                 confThres: float,
                 imageNormalPath: str,
                 imagePath: str,
                 detectArea: str = "",
                 save_det: bool = False) -> List[Dict[str, Union[str, Any]]]:
        """执行检测"""
        if model is None or not os.path.exists(imagePath):
            return [{
                "value": "0",
                "resultClass": "0",
                "code": "2001",
                "pos": [],
                "conf": ""
            }]

        try:
            t, img0, size_org, trans = preprocess_image(imagePath)
            preds = model.run(None, {model.get_inputs()[0].name: t})[0]
            dets = postprocess(preds, size_org, trans, confThres)

            # 如果指定了检测区域，找到最佳匹配
            best = find_best_match(dets, detectArea)
            final = [best] if best else dets

            # 保存检测结果图像
            if save_det and final:
                save_path = imagePath.replace('.', '_det.')
                draw_and_save(img0, final, save_path)
                print(f"检测结果已保存: {save_path}")

            # 单类别检测模型：检测到任意目标即表示有人抽烟。
            has_smoke = bool(final)

            if has_smoke:
                return [{
                    "value": "1",
                    "resultClass": "1",
                    "code": "2000",
                    "pos": [],
                    "conf": ""
                }]
            else:
                return [{
                    "value": "0",
                    "resultClass": "0",
                    "code": "2000",
                    "pos": [],
                    "conf": ""
                }]

        except Exception as e:
            print(f"推理出错: {e}")
            return [{
                "value": "0",
                "resultClass": "0",
                "code": "2002",
                "pos": [],
                "conf": ""
            }]


def inference_single(model, detector: Detect,
                     image_path: str,
                     conf_threshold: float = 0.25,
                     detect_area: str = "",
                     save_det: bool = False):
    """单张图片推理"""
    print(f"\n处理图片: {image_path}")
    start_time = time.time()

    result = detector(model, conf_threshold, "", image_path, detect_area, save_det)

    end_time = time.time()
    print(f"推理时间: {end_time - start_time:.3f}s")
    print(f"检测结果: {json.dumps(result, ensure_ascii=False, indent=2)}")

    return result


def inference_batch(model, detector: Detect,
                    image_dir: str,
                    output_dir: str = "output",
                    conf_threshold: float = 0.25,
                    save_det: bool = True,
                    save_json: bool = True):
    """批量推理"""
    image_extensions = {'.jpg', '.jpeg', '.png', '.bmp', '.tiff', '.tif'}
    image_paths = []

    for ext in image_extensions:
        image_paths.extend(Path(image_dir).glob(f"*{ext}"))
        image_paths.extend(Path(image_dir).glob(f"*{ext.upper()}"))

    if not image_paths:
        print(f"在 {image_dir} 中未找到图片文件")
        return

    os.makedirs(output_dir, exist_ok=True)
    all_results = []

    print(f"开始批量推理，共 {len(image_paths)} 张图片")
    start_time = time.time()

    for i, img_path in enumerate(image_paths, 1):
        print(f"\n[{i}/{len(image_paths)}] 处理: {img_path.name}")

        # 执行推理
        result = detector(model, conf_threshold, "", str(img_path), "", save_det)

        # 保存单张图片的结果
        img_result = {
            "image_path": str(img_path),
            "image_name": img_path.name,
            "detections": result
        }
        all_results.append(img_result)

        # 打印结果摘要
        if result and result[0].get("value") == "1":
            print("  有人抽烟")
        else:
            print("  无人吸烟")

    total_time = time.time() - start_time
    print(f"\n批量推理完成!")
    print(f"总时间: {total_time:.2f}s")
    print(f"平均时间: {total_time / len(image_paths):.3f}s/张")

    # 保存JSON结果
    if save_json:
        json_path = os.path.join(output_dir, "inference_results.json")
        with open(json_path, 'w', encoding='utf-8') as f:
            json.dump(all_results, f, ensure_ascii=False, indent=2)
        print(f"结果已保存到: {json_path}")


def main():
    """主函数"""
    parser = argparse.ArgumentParser(description='YOLO模型推理脚本')
    parser.add_argument('--model', type=str, default=MODEL_PATH, help='ONNX模型路径')
    parser.add_argument('--source', type=str, required=True, help='输入图片路径或文件夹')
    parser.add_argument('--output', type=str, default='output', help='输出文件夹')
    parser.add_argument('--conf', type=float, default=0.25, help='置信度阈值')
    parser.add_argument('--detect-area', type=str, default='', help='检测区域 (x1,y1,x2,y2)')
    parser.add_argument('--save-det', action='store_true', help='保存检测结果图片')
    parser.add_argument('--save-json', action='store_true', help='保存JSON结果文件')

    args = parser.parse_args()

    # 加载模型
    model = load_model(args.model)
    if model is None:
        print("模型加载失败！")
        return

    # 初始化检测器
    detector = Detect()

    # 判断是单张图片还是文件夹
    if os.path.isfile(args.source):
        # 单张图片推理
        inference_single(model, detector, args.source, args.conf, args.detect_area, args.save_det)
    elif os.path.isdir(args.source):
        # 批量推理
        inference_batch(model, detector, args.source, args.output, args.conf, args.save_det, args.save_json)
    else:
        print(f"输入路径不存在: {args.source}")


if __name__ == "__main__":
    # 可以直接运行进行测试
    if len(os.sys.argv) == 1:
        # 测试模式
        model = load_model(MODEL_PATH)
        if model is None:
            print("模型加载失败！请检查模型路径")
        else:
            detector = Detect()

            # 单张图片测试
            test_image = r"E:\BaiduSyncdisk\SZBJ\testblq\7.png"
            if os.path.exists(test_image):
                inference_single(model, detector, test_image, save_det=True)
            else:
                print(f"测试图片不存在: {test_image}")
                print("请使用命令行参数运行:")
                print("python inference.py --source /path/to/image_or_folder --save-det --save-json")
    else:
        # 命令行模式
        main()
