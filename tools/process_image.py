import numpy as np
from PIL import Image, ImageEnhance, ImageColor

def process_image(input_path, output_path):
    print(f"Processing {input_path}...")
    try:
        img = Image.open(input_path).convert('RGBA')
        
        # 1. Boost global saturation (Red, Green, Blue pop more)
        # "充满红、绿、蓝" -> Enhance color
        enhancer = ImageEnhance.Color(img)
        img = enhancer.enhance(1.5)  # Increase saturation by 50%

        # 2. Lighten dark blue background
        # Convert to numpy for pixel-wise operation
        data = np.array(img)
        
        # Define what is "dark blue"
        # In RGB, dark blue is roughly: R low, G low, B medium-high
        # But let's use a simpler heuristic or HSV if possible.
        # Since we are using numpy on RGBA:
        r, g, b, a = data[:,:,0], data[:,:,1], data[:,:,2], data[:,:,3]

        # Mask for dark blue-ish pixels
        # Criteria: Blue is dominant, and brightness is low
        # This is a heuristic and might need tuning
        blue_mask = (b > r) & (b > g) & (b < 150) & (r < 100) & (g < 100)
        
        # Lighten these pixels
        # Increase RGB values to make it lighter (closer to white/light blue)
        # We add a constant value to R, G, B
        lighten_factor = 50
        
        data[blue_mask, 0] = np.clip(data[blue_mask, 0] + lighten_factor, 0, 255) # R
        data[blue_mask, 1] = np.clip(data[blue_mask, 1] + lighten_factor, 0, 255) # G
        data[blue_mask, 2] = np.clip(data[blue_mask, 2] + lighten_factor, 0, 255) # B

        # Reconstruct image
        img_processed = Image.fromarray(data)

        # 3. Resize specific icon (220kV station)
        # Without object detection coordinates, we cannot do this automatically accurately.
        # We will skip this step and inform the user.
        
        img_processed.save(output_path)
        print(f"Saved processed image to {output_path}")
        
    except Exception as e:
        print(f"Error processing image: {e}")

if __name__ == "__main__":
    process_image('docs/images/image1.png', 'docs/images/image1_processed.png')
