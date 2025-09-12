#!/usr/bin/env python3
"""
Create promotional assets for Chrome Web Store
Required sizes:
- Small tile: 440x280
- Large tile: 920x680  
- Marquee: 1400x560
- Store icon: 128x128 (already have)
"""

from PIL import Image, ImageDraw, ImageFont
import os

def create_background_scene(width, height):
    """Create the scenic background matching the extension"""
    img = Image.new('RGBA', (width, height), (0, 0, 0, 0))
    draw = ImageDraw.Draw(img)
    
    # Sky gradient
    for y in range(height):
        blend = y / height
        sky_color = (
            int(135 * (1-blend) + 224 * blend),  # Blue to light blue
            int(206 * (1-blend) + 240 * blend),  # 
            int(235 * (1-blend) + 255 * blend)   #
        )
        draw.line([(0, y), (width, y)], fill=sky_color)
    
    # Sun
    sun_size = int(width * 0.05)
    sun_x = width - int(width * 0.15)
    sun_y = int(height * 0.15)
    draw.ellipse([sun_x - sun_size, sun_y - sun_size, 
                  sun_x + sun_size, sun_y + sun_size], 
                 fill=(255, 215, 0))
    
    # Grass at bottom
    grass_height = int(height * 0.25)
    for y in range(height - grass_height, height):
        blend = (y - (height - grass_height)) / grass_height
        grass_color = (
            int(124 * (1-blend) + 34 * blend),   # Light to dark green
            int(252 * (1-blend) + 139 * blend),  #
            int(0 * (1-blend) + 34 * blend)      #
        )
        draw.line([(0, y), (width, y)], fill=grass_color)
    
    return img

def create_cute_dog(size):
    """Create a cute dog sprite at given size"""
    img = Image.new('RGBA', (size, size), (0, 0, 0, 0))
    draw = ImageDraw.Draw(img)
    
    scale = size / 80  # Base dog is 80px
    
    # Dog body
    body_width = int(40 * scale)
    body_height = int(35 * scale)
    body_x = size // 2 - body_width // 2
    body_y = size - int(45 * scale)
    draw.ellipse([body_x, body_y, body_x + body_width, body_y + body_height], 
                 fill=(210, 105, 30))
    
    # Dog head
    head_size = int(35 * scale)
    head_x = size // 2 - head_size // 2
    head_y = size - int(70 * scale)
    draw.ellipse([head_x, head_y, head_x + head_size, head_y + head_size], 
                 fill=(210, 105, 30))
    
    # Eyes
    eye_size = int(6 * scale)
    eye_y = head_y + int(12 * scale)
    draw.ellipse([head_x + int(10 * scale), eye_y, 
                  head_x + int(10 * scale) + eye_size, eye_y + eye_size], 
                 fill=(0, 0, 0))
    draw.ellipse([head_x + head_size - int(16 * scale), eye_y, 
                  head_x + head_size - int(10 * scale), eye_y + eye_size], 
                 fill=(0, 0, 0))
    
    # Nose
    nose_size = int(4 * scale)
    nose_x = size // 2 - nose_size // 2
    nose_y = head_y + int(20 * scale)
    draw.ellipse([nose_x, nose_y, nose_x + nose_size, nose_y + nose_size], 
                 fill=(0, 0, 0))
    
    # Ears
    ear_width = int(18 * scale)
    ear_height = int(25 * scale)
    # Left ear
    draw.ellipse([head_x + int(5 * scale), head_y - int(10 * scale), 
                  head_x + int(5 * scale) + ear_width, head_y - int(10 * scale) + ear_height], 
                 fill=(139, 69, 19))
    # Right ear
    draw.ellipse([head_x + head_size - int(23 * scale), head_y - int(10 * scale), 
                  head_x + head_size - int(5 * scale), head_y - int(10 * scale) + ear_height], 
                 fill=(139, 69, 19))
    
    # Tail
    tail_width = int(15 * scale)
    tail_height = int(25 * scale)
    tail_x = body_x + body_width - int(5 * scale)
    tail_y = body_y + int(5 * scale)
    draw.ellipse([tail_x, tail_y, tail_x + tail_width, tail_y + tail_height], 
                 fill=(139, 69, 19))
    
    return img

def create_promotional_tile(width, height, title, subtitle):
    """Create a promotional tile"""
    img = create_background_scene(width, height)
    draw = ImageDraw.Draw(img)
    
    # Add dog
    dog_size = int(min(width, height) * 0.4)
    dog = create_cute_dog(dog_size)
    dog_x = int(width * 0.6) - dog_size // 2
    dog_y = height - dog_size - int(height * 0.1)
    img.paste(dog, (dog_x, dog_y), dog)
    
    # Add text
    try:
        title_font = ImageFont.truetype("/System/Library/Fonts/Helvetica.ttc", int(width * 0.08))
        subtitle_font = ImageFont.truetype("/System/Library/Fonts/Helvetica.ttc", int(width * 0.04))
    except:
        title_font = ImageFont.load_default()
        subtitle_font = ImageFont.load_default()
    
    # Title
    title_x = int(width * 0.05)
    title_y = int(height * 0.2)
    draw.text((title_x, title_y), title, fill=(255, 255, 255), font=title_font,
              stroke_width=2, stroke_fill=(0, 0, 0))
    
    # Subtitle
    subtitle_y = title_y + int(height * 0.12)
    draw.text((title_x, subtitle_y), subtitle, fill=(255, 255, 255), font=subtitle_font,
              stroke_width=1, stroke_fill=(0, 0, 0))
    
    return img

def main():
    # Create store assets directory
    assets_dir = 'chrome-extension/store-assets'
    if not os.path.exists(assets_dir):
        os.makedirs(assets_dir)
    
    # Small tile (440x280)
    small_tile = create_promotional_tile(440, 280, "TabSense", "Smart Tab Manager with\nCute Dog Mascot!")
    small_tile.save(os.path.join(assets_dir, 'small-tile-440x280.png'), 'PNG')
    print("Created small tile (440x280)")
    
    # Large tile (920x680)
    large_tile = create_promotional_tile(920, 680, "TabSense Declutter", "AI-Powered Tab Organization\nwith Adorable Dog Companion")
    large_tile.save(os.path.join(assets_dir, 'large-tile-920x680.png'), 'PNG')
    print("Created large tile (920x680)")
    
    # Marquee (1400x560)
    marquee = create_promotional_tile(1400, 560, "TabSense", "Declutter Your Tabs • Boost Productivity • Enjoy Cute Dog Animations")
    marquee.save(os.path.join(assets_dir, 'marquee-1400x560.png'), 'PNG')
    print("Created marquee (1400x560)")
    
    # Store icon (128x128) - just the dog
    store_icon = Image.new('RGBA', (128, 128), (135, 206, 235))  # Sky blue background
    draw = ImageDraw.Draw(store_icon)
    draw.ellipse([0, 0, 127, 127], fill=(135, 206, 235))
    
    dog = create_cute_dog(100)
    store_icon.paste(dog, (14, 20), dog)
    store_icon.save(os.path.join(assets_dir, 'store-icon-128x128.png'), 'PNG')
    print("Created store icon (128x128)")
    
    print(f"\nAll promotional assets created in {assets_dir}/")

if __name__ == '__main__':
    main()