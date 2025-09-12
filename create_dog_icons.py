#!/usr/bin/env python3
"""
Create cute dog-themed icons for TabSense extension
"""

from PIL import Image, ImageDraw
import os

def create_dog_icon(size):
    """Create a cute pixel-art style dog face icon"""
    # Create a new image with transparent background
    img = Image.new('RGBA', (size, size), (0, 0, 0, 0))
    draw = ImageDraw.Draw(img)
    
    # Calculate scaling factor
    scale = size / 128
    
    # Define colors
    bg_color = (135, 206, 235, 255)  # Sky blue background
    dog_color = (210, 105, 30, 255)  # Chocolate brown
    ear_color = (139, 69, 19, 255)   # Saddle brown
    eye_color = (0, 0, 0, 255)       # Black
    nose_color = (0, 0, 0, 255)      # Black
    tongue_color = (255, 105, 180, 255)  # Pink
    
    # Draw circular background
    draw.ellipse([0, 0, size-1, size-1], fill=bg_color)
    
    # Draw dog face (main circle)
    face_margin = int(15 * scale)
    face_size = size - (face_margin * 2)
    draw.ellipse([face_margin, face_margin + int(5 * scale), 
                  face_margin + face_size, face_margin + face_size + int(5 * scale)], 
                 fill=dog_color)
    
    # Draw ears (two circles on sides)
    ear_size = int(30 * scale)
    ear_y = int(20 * scale)
    # Left ear
    draw.ellipse([int(10 * scale), ear_y, 
                  int(10 * scale) + ear_size, ear_y + int(ear_size * 1.2)], 
                 fill=ear_color)
    # Right ear
    draw.ellipse([size - int(10 * scale) - ear_size, ear_y, 
                  size - int(10 * scale), ear_y + int(ear_size * 1.2)], 
                 fill=ear_color)
    
    # Draw eyes
    eye_size = int(8 * scale)
    eye_y = int(45 * scale)
    eye_spacing = int(35 * scale)
    # Left eye
    draw.ellipse([size//2 - eye_spacing//2 - eye_size//2, eye_y,
                  size//2 - eye_spacing//2 + eye_size//2, eye_y + eye_size],
                 fill=eye_color)
    # Right eye
    draw.ellipse([size//2 + eye_spacing//2 - eye_size//2, eye_y,
                  size//2 + eye_spacing//2 + eye_size//2, eye_y + eye_size],
                 fill=eye_color)
    
    # Draw nose (small triangle)
    nose_size = int(10 * scale)
    nose_y = int(65 * scale)
    nose_points = [
        (size//2, nose_y + nose_size),  # Bottom point
        (size//2 - nose_size//2, nose_y),  # Top left
        (size//2 + nose_size//2, nose_y)   # Top right
    ]
    draw.polygon(nose_points, fill=nose_color)
    
    # Draw mouth (curved line - actually a very flat ellipse)
    mouth_y = int(70 * scale)
    mouth_width = int(20 * scale)
    draw.arc([size//2 - mouth_width, mouth_y,
              size//2 + mouth_width, mouth_y + int(15 * scale)],
             start=0, end=180, fill=nose_color, width=int(3 * scale))
    
    # Draw tongue (small pink ellipse)
    tongue_y = int(75 * scale)
    tongue_size = int(12 * scale)
    draw.ellipse([size//2 - tongue_size//2, tongue_y,
                  size//2 + tongue_size//2, tongue_y + int(tongue_size * 0.7)],
                 fill=tongue_color)
    
    # Add a subtle white highlight on the face for depth
    highlight_size = int(15 * scale)
    highlight_pos = (int(40 * scale), int(35 * scale))
    highlight_color = (255, 255, 255, 80)  # Semi-transparent white
    draw.ellipse([highlight_pos[0], highlight_pos[1],
                  highlight_pos[0] + highlight_size, highlight_pos[1] + highlight_size],
                 fill=highlight_color)
    
    return img

def main():
    # Create icons directory if it doesn't exist
    icon_dir = 'chrome-extension/icons'
    if not os.path.exists(icon_dir):
        os.makedirs(icon_dir)
    
    # Generate icons in different sizes
    sizes = [16, 48, 128]
    
    for size in sizes:
        icon = create_dog_icon(size)
        icon_path = os.path.join(icon_dir, f'icon{size}.png')
        icon.save(icon_path, 'PNG')
        print(f"Created {icon_path}")

if __name__ == '__main__':
    main()