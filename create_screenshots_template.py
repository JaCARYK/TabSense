#!/usr/bin/env python3
"""
Create template screenshots for Chrome Web Store listing
These show what the extension looks like in use
"""

from PIL import Image, ImageDraw, ImageFont
import os

def create_extension_mockup(width=1280, height=800):
    """Create a mockup of the extension in Chrome browser"""
    img = Image.new('RGB', (width, height), (255, 255, 255))
    draw = ImageDraw.Draw(img)
    
    # Chrome browser chrome (top bar)
    draw.rectangle([0, 0, width, 80], fill=(240, 240, 240))
    draw.rectangle([0, 80, width, 120], fill=(245, 245, 245))
    
    # URL bar
    draw.rounded_rectangle([200, 40, width-200, 75], radius=20, fill=(255, 255, 255))
    draw.text((220, 50), "chrome-extension://tabsense-declutter", fill=(100, 100, 100))
    
    # Tab bar
    draw.rectangle([0, 80, 200, 120], fill=(220, 220, 220))
    draw.text((10, 95), "TabSense Demo", fill=(50, 50, 50))
    
    # Extension popup area (centered)
    popup_width = 420
    popup_height = 600
    popup_x = (width - popup_width) // 2
    popup_y = 150
    
    # Extension popup background
    draw.rectangle([popup_x, popup_y, popup_x + popup_width, popup_y + popup_height], 
                   fill=(248, 249, 250), outline=(200, 200, 200), width=2)
    
    # Header with dog scene (simplified)
    header_height = 200
    draw.rectangle([popup_x, popup_y, popup_x + popup_width, popup_y + header_height], 
                   fill=(135, 206, 235))  # Sky blue
    
    # Grass at bottom of header
    grass_height = 50
    draw.rectangle([popup_x, popup_y + header_height - grass_height, 
                    popup_x + popup_width, popup_y + header_height], 
                   fill=(124, 252, 0))  # Bright green
    
    # Title
    try:
        font = ImageFont.truetype("/System/Library/Fonts/Helvetica.ttc", 20)
        small_font = ImageFont.truetype("/System/Library/Fonts/Helvetica.ttc", 14)
    except:
        font = ImageFont.load_default()
        small_font = ImageFont.load_default()
    
    draw.text((popup_x + 20, popup_y + 20), "TabSense", fill=(255, 255, 255), font=font)
    
    # Health score circle (simplified)
    circle_x = popup_x + popup_width - 80
    circle_y = popup_y + 20
    draw.ellipse([circle_x, circle_y, circle_x + 60, circle_y + 60], 
                 outline=(255, 255, 255), width=3, fill=None)
    draw.text((circle_x + 20, circle_y + 20), "85", fill=(255, 255, 255), font=font)
    draw.text((circle_x + 15, circle_y + 40), "Health", fill=(255, 255, 255), font=small_font)
    
    # Dog (very simple representation)
    dog_x = popup_x + popup_width // 2 - 15
    dog_y = popup_y + header_height - 80
    draw.ellipse([dog_x, dog_y, dog_x + 30, dog_y + 30], fill=(210, 105, 30))  # Head
    draw.ellipse([dog_x + 5, dog_y + 25, dog_x + 25, dog_y + 50], fill=(210, 105, 30))  # Body
    
    # Speech bubble
    draw.ellipse([dog_x - 60, dog_y - 40, dog_x + 20, dog_y - 10], fill=(255, 255, 255))
    draw.text((dog_x - 50, dog_y - 35), "Great job!", fill=(50, 50, 50), font=small_font)
    
    # Stats section
    stats_y = popup_y + header_height + 20
    draw.text((popup_x + 20, stats_y), "Total Tabs: 32  •  Can Close: 8  •  Duplicates: 3", 
              fill=(100, 100, 100), font=small_font)
    
    # Action buttons
    button_y = stats_y + 40
    draw.rounded_rectangle([popup_x + 20, button_y, popup_x + 140, button_y + 35], 
                          radius=8, fill=(102, 126, 234))
    draw.text((popup_x + 50, button_y + 10), "🧹 Quick Clean", fill=(255, 255, 255), font=small_font)
    
    draw.rounded_rectangle([popup_x + 160, button_y, popup_x + 280, button_y + 35], 
                          radius=8, fill=(108, 117, 125))
    draw.text((popup_x + 185, button_y + 10), "📁 Auto Group", fill=(255, 255, 255), font=small_font)
    
    # Sample tab list
    list_y = button_y + 60
    draw.text((popup_x + 20, list_y), "Suggested to Close:", fill=(50, 50, 50), font=font)
    
    tab_items = [
        "Old LinkedIn Tab - Never used",
        "Email Draft - Rarely used", 
        "Random Search - Forgotten"
    ]
    
    for i, item in enumerate(tab_items):
        item_y = list_y + 40 + (i * 40)
        draw.rectangle([popup_x + 20, item_y, popup_x + popup_width - 20, item_y + 30], 
                       fill=(248, 249, 250), outline=(220, 220, 220))
        draw.text((popup_x + 30, item_y + 8), f"☐ {item}", fill=(100, 100, 100), font=small_font)
    
    return img

def main():
    # Create screenshots directory
    screenshots_dir = 'chrome-extension/screenshots'
    if not os.path.exists(screenshots_dir):
        os.makedirs(screenshots_dir)
    
    # Main screenshot
    screenshot1 = create_extension_mockup()
    screenshot1.save(os.path.join(screenshots_dir, 'screenshot-1-main-interface.png'), 'PNG')
    print("Created main interface screenshot")
    
    # You can create more variations here
    screenshot2 = create_extension_mockup()
    # Modify for different states...
    screenshot2.save(os.path.join(screenshots_dir, 'screenshot-2-happy-dog.png'), 'PNG')
    print("Created happy dog screenshot")
    
    print(f"\nScreenshots created in {screenshots_dir}/")
    print("Note: You should also take real screenshots of your extension in action!")

if __name__ == '__main__':
    main()