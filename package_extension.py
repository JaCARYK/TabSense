#!/usr/bin/env python3
"""
Package TabSense extension for Chrome Web Store submission
"""

import os
import zipfile
import shutil
from pathlib import Path

def package_extension():
    """Package the extension files into a zip for Chrome Web Store"""
    
    # Files to include in the extension package
    extension_files = [
        'chrome-extension/manifest.json',
        'chrome-extension/background_declutter.js',
        'chrome-extension/popup_declutter.html',
        'chrome-extension/popup_declutter.css',
        'chrome-extension/popup_declutter.js',
        'chrome-extension/firebase-app.js',
        'chrome-extension/firebase-auth.js',
        'chrome-extension/firebase-firestore.js',
        'chrome-extension/firebase-config.js',
        'chrome-extension/icons/icon16.png',
        'chrome-extension/icons/icon48.png',
        'chrome-extension/icons/icon128.png',
    ]
    
    # Create package directory
    package_dir = 'chrome-extension-package'
    if os.path.exists(package_dir):
        shutil.rmtree(package_dir)
    os.makedirs(package_dir)
    
    # Copy files to package directory
    copied_files = []
    for file_path in extension_files:
        if os.path.exists(file_path):
            # Create directory structure
            dest_path = os.path.join(package_dir, os.path.basename(file_path))
            if 'icons/' in file_path:
                icons_dir = os.path.join(package_dir, 'icons')
                if not os.path.exists(icons_dir):
                    os.makedirs(icons_dir)
                dest_path = os.path.join(package_dir, 'icons', os.path.basename(file_path))
            
            shutil.copy2(file_path, dest_path)
            copied_files.append(file_path)
            print(f"✓ Copied: {file_path}")
        else:
            print(f"⚠ Missing: {file_path}")
    
    # Create ZIP file
    zip_filename = 'TabSense-Declutter-v2.0.0.zip'
    with zipfile.ZipFile(zip_filename, 'w', zipfile.ZIP_DEFLATED) as zipf:
        for root, dirs, files in os.walk(package_dir):
            for file in files:
                file_path = os.path.join(root, file)
                arcname = os.path.relpath(file_path, package_dir)
                zipf.write(file_path, arcname)
                print(f"✓ Added to ZIP: {arcname}")
    
    # Clean up temporary directory
    shutil.rmtree(package_dir)
    
    print(f"\n🎉 Extension packaged successfully!")
    print(f"📦 Package: {zip_filename}")
    print(f"📁 Files included: {len(copied_files)}")
    
    # Verify package
    with zipfile.ZipFile(zip_filename, 'r') as zipf:
        files_in_zip = zipf.namelist()
        print(f"\n📋 Contents of {zip_filename}:")
        for file in sorted(files_in_zip):
            print(f"   {file}")
    
    return zip_filename

def create_store_description():
    """Create the Chrome Web Store description"""
    description = """
🐕 **TabSense Declutter - Smart Tab Manager with Adorable Dog Mascot!**

Transform your chaotic browser tabs into an organized, delightful experience with TabSense Declutter! Our AI-powered extension features an adorable animated dog that reacts to your tab health and helps you maintain a clutter-free browsing experience.

## ✨ Key Features

**🤖 Smart Tab Analysis**
- AI-powered classification of unused, forgotten, and duplicate tabs
- Real-time tab health scoring with beautiful visual feedback
- Intelligent suggestions for tab cleanup and organization

**🐕 Animated Dog Companion**
- Cute pixel-art dog mascot with personality
- 3 emotional states based on your tab organization (happy/neutral/sad)  
- Contextual speech bubbles with helpful messages
- Wagging tail, blinking eyes, and bouncing beach ball animations

**🎯 One-Click Actions**
- Quick Clean: Instantly close rarely-used tabs
- Auto Group: Organize tabs by domain (Google, GitHub, etc.)
- Close Duplicates: Remove duplicate tabs intelligently
- Bulk Selection: Choose exactly which tabs to close

**📊 Health Dashboard**
- Beautiful animated circular progress indicator
- Real-time statistics (total tabs, duplicates, forgotten tabs)
- Scenic background with sky, clouds, sun, and grass
- Responsive design optimized for productivity

**🔒 Privacy First**
- All analysis happens locally in your browser
- Optional Firebase sync for cross-device preferences
- No tracking, no ads, no data selling
- Open source on GitHub

## 🚀 Perfect For

- Students managing research tabs
- Developers with multiple project tabs  
- Professionals juggling multiple tasks
- Anyone who loves cute dog animations!
- Users who want to boost browser performance

## 🎨 Why You'll Love It

TabSense Declutter isn't just another tab manager - it's a delightful companion that makes tab organization fun! Watch your dog jump for joy when you maintain good tab hygiene, or see it get sad when tabs pile up. The beautiful animations and personality-filled interactions make mundane tab management an enjoyable experience.

## 📱 How to Use

1. Install the extension
2. Click the TabSense icon in your toolbar
3. Create an optional account for cross-device sync
4. Let your new dog friend analyze your tabs
5. Follow the smart suggestions to declutter
6. Enjoy a faster, more organized browsing experience!

## 🔧 Technical Details

- Manifest V3 compliant
- Works with Chrome tab groups and bookmarks
- Analyzes browsing history for better suggestions
- Lightweight and fast performance
- Regular updates with new features

Ready to turn tab chaos into organized bliss? Install TabSense Declutter today and meet your new favorite browser companion! 🐕✨

---
**Need help?** Visit our GitHub: https://github.com/JaCARYK/TabSense
**Privacy Policy**: Included with extension
    """.strip()
    
    with open('chrome-web-store-description.txt', 'w') as f:
        f.write(description)
    
    print(f"✓ Created Chrome Web Store description")
    return description

def main():
    print("📦 Packaging TabSense Declutter for Chrome Web Store...\n")
    
    # Package the extension
    zip_file = package_extension()
    
    # Create store description
    create_store_description()
    
    print(f"\n🎉 Chrome Web Store package ready!")
    print(f"📦 Upload file: {zip_file}")
    print(f"📝 Description: chrome-web-store-description.txt")
    print(f"🖼️  Images: chrome-extension/store-assets/")
    print(f"📸 Screenshots: chrome-extension/screenshots/")
    print(f"🔒 Privacy Policy: PRIVACY_POLICY.md")
    
    print(f"\n📋 Next Steps:")
    print(f"1. Go to https://chrome.google.com/webstore/devconsole")
    print(f"2. Create developer account ($5 fee)")
    print(f"3. Upload {zip_file}")
    print(f"4. Add store assets and screenshots")
    print(f"5. Copy description from chrome-web-store-description.txt")
    print(f"6. Submit for review!")

if __name__ == '__main__':
    main()