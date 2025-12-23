import numpy as np
from PIL import Image, ImageEnhance, ImageColor

def adjust_colors(img):
    # 1. Enhance global saturation (Make colors pop)
    enhancer = ImageEnhance.Color(img)
    img = enhancer.enhance(1.8)  # Increase saturation by 80%
    
    # 2. Lighten dark blue background
    # Convert to HSV for better color targeting
    img_hsv = img.convert('HSV')
    data_hsv = np.array(img_hsv)
    
    # H: 0-255, S: 0-255, V: 0-255
    # Blue is roughly H=160-180 in PIL's 0-255 scale (Blue is 240 deg -> 240/360*255 = 170)
    # Dark: V is low
    h, s, v = data_hsv[:,:,0], data_hsv[:,:,1], data_hsv[:,:,2]
    
    # Mask for dark blue
    # Hue around 160-180 (Blue)
    # Saturation > 50 (Not grey)
    # Value < 100 (Dark)
    blue_mask = (h > 150) & (h < 190) & (s > 40) & (v < 120)
    
    # Increase Value (Brightness) for these pixels
    # Add 60 to brightness, cap at 255
    # using np.add to allow broadcasting if needed, but here simple addition works with casting
    v_new = v.copy()
    v_new[blue_mask] = np.clip(v[blue_mask] + 80, 0, 255)
    
    # Update V channel
    data_hsv[:,:,2] = v_new
    
    # Convert back to RGBA
    img_adjusted = Image.fromarray(data_hsv, mode='HSV').convert('RGBA')
    
    # Restore Alpha from original if needed (HSV conversion drops Alpha)
    if img.mode == 'RGBA':
        alpha = img.split()[3]
        img_adjusted.putalpha(alpha)
        
    return img_adjusted

def magnify_center(img, zoom_factor=1.2):
    """
    Magnifies the center of the image.
    Assumes the main subject (220kV station) is in the center.
    """
    width, height = img.size
    
    # Define crop size (inverse of zoom)
    crop_w = int(width / zoom_factor)
    crop_h = int(height / zoom_factor)
    
    left = (width - crop_w) // 2
    top = (height - crop_h) // 2
    right = left + crop_w
    bottom = top + crop_h
    
    # Crop the center
    crop = img.crop((left, top, right, bottom))
    
    # Resize back to original size? 
    # The user said "make the icon bigger".
    # Usually this means scaling up the object. 
    # If we scale up the WHOLE center, we lose the edges.
    # But maybe that's what is expected?
    # Or does the user mean "scale up the icon inplace"? That requires segmentation.
    # Let's try to just scale up the center region and overlay it? 
    # No, that looks bad (rectangular cut).
    
    # Best approach for "make icon bigger" without segmentation is to just Crop-in (Zoom).
    # This makes everything bigger, including the icon.
    img_zoomed = crop.resize((width, height), Image.Resampling.LANCZOS)
    return img_zoomed

def process_image(input_path, output_path):
    print(f"Processing {input_path}...")
    try:
        img = Image.open(input_path).convert('RGBA')
        
        # Color adjustment
        img = adjust_colors(img)
        
        # Magnify (Zoom in slightly to make central objects bigger)
        # Assuming the 220kV station is the main subject in the center
        img = magnify_center(img, zoom_factor=1.15)
        
        img.save(output_path)
        print(f"Saved processed image to {output_path}")
        
    except Exception as e:
        print(f"Error processing image: {e}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    process_image('docs/images/image1.png', 'docs/images/image1_processed_v2.png')
