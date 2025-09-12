#!/usr/bin/env python3
"""
Simple script to create basic extension icons
"""
from PIL import Image, ImageDraw, ImageFont
import os

def create_icon(size, filename):
    # Create a new image with a gradient background
    img = Image.new('RGBA', (size, size), (102, 126, 234, 255))
    draw = ImageDraw.Draw(img)
    
    # Add a simple "T" for TabSense
    try:
        # Try to use a system font
        font_size = max(size // 2, 12)
        font = ImageFont.truetype("/System/Library/Fonts/Arial.ttf", font_size)
    except:
        # Fallback to default font
        font = ImageFont.load_default()
    
    # Draw "T" in the center
    text = "T"
    bbox = draw.textbbox((0, 0), text, font=font)
    text_width = bbox[2] - bbox[0]
    text_height = bbox[3] - bbox[1]
    
    x = (size - text_width) // 2
    y = (size - text_height) // 2
    
    draw.text((x, y), text, fill=(255, 255, 255, 255), font=font)
    
    # Add a subtle border
    draw.rectangle([0, 0, size-1, size-1], outline=(76, 75, 162, 255), width=2)
    
    # Save the image
    img.save(filename, 'PNG')
    print(f"Created {filename} ({size}x{size})")

if __name__ == "__main__":
    # Create icons directory if it doesn't exist
    icons_dir = "chrome-extension/icons"
    os.makedirs(icons_dir, exist_ok=True)
    
    # Create the three required icon sizes
    create_icon(16, f"{icons_dir}/icon16.png")
    create_icon(48, f"{icons_dir}/icon48.png")
    create_icon(128, f"{icons_dir}/icon128.png")
    
    print("✅ All extension icons created successfully!")