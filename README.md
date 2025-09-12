# TabSense Declutter - Smart Tab Manager 🐕

Chrome browser extension with an adorable animated dog mascot that helps you declutter and organize your browser tabs using AI-powered analysis.

## 🎯 Download & Install

**📦 [Install from Chrome Web Store](#)** *(Coming Soon!)*

*Or install manually following the setup instructions below*

## ✨ Features

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

## 🏗️ Architecture

```
Chrome Extension (Manifest V3) → Firebase (Optional) → Local AI Analysis
```

## 📱 How to Use

1. Install the extension from Chrome Web Store (link above)
2. Click the TabSense icon in your toolbar
3. Create an optional account for cross-device sync
4. Let your new dog friend analyze your tabs
5. Follow the smart suggestions to declutter
6. Enjoy a faster, more organized browsing experience!

## 🛠️ Development Setup

Want to contribute or run locally? Follow these steps:

### Prerequisites

- Chrome browser
- Firebase account (optional, for sync features)

### 1. Firebase Setup

1. Create a new Firebase project at [Firebase Console](https://console.firebase.google.com)
2. Enable Authentication with Email/Password provider
3. Create a Firestore Database
4. Get your Firebase configuration:
   - Go to Project Settings > General
   - Create a new web app
   - Copy the configuration object

5. Create a service account key:
   - Go to Project Settings > Service Accounts
   - Generate a new private key
   - Save it as `serviceAccountKey.json` in the `flask-server` folder

### 2. Configure the Extension

1. Update `chrome-extension/firebase-config.js` with your Firebase config:
```javascript
const firebaseConfig = {
    apiKey: "YOUR_API_KEY",
    authDomain: "YOUR_AUTH_DOMAIN",
    projectId: "YOUR_PROJECT_ID",
    storageBucket: "YOUR_STORAGE_BUCKET",
    messagingSenderId: "YOUR_MESSAGING_SENDER_ID",
    appId: "YOUR_APP_ID"
};
```

2. Update `chrome-extension/background.js` with the same config (lines 15-22)

3. Add icon files to `chrome-extension/icons/`:
   - icon16.png (16x16 pixels)
   - icon48.png (48x48 pixels)
   - icon128.png (128x128 pixels)

### 3. Install the Chrome Extension

1. Open Chrome and navigate to `chrome://extensions/`
2. Enable "Developer mode" (top right)
3. Click "Load unpacked"
4. Select the `chrome-extension` folder
5. The TabSense Declutter extension should now appear in your extensions list
6. Start decluttering your tabs with your new dog companion!

## 🔧 Technical Details

- **Manifest V3** compliant for latest Chrome standards
- **Local Processing** - all tab analysis happens in your browser
- **Firebase Integration** - optional cloud sync for preferences
- **Performance Optimized** - lightweight and fast
- **Cross-Platform** - works on all operating systems with Chrome

## 🐛 Troubleshooting

### Extension not loading properly
- Try reloading the extension in `chrome://extensions/`
- Check browser console for errors (F12)
- Ensure you're using a recent version of Chrome

### Dog mascot not appearing
- The extension may still be initializing - wait a moment
- Check that the extension has proper permissions
- Try refreshing the popup

### Sync not working
- Verify you're logged into your account
- Check your internet connection
- Firebase sync is optional - local features work without it

## 🔒 Privacy & Security

- **Local First** - All tab analysis happens in your browser
- **Optional Sync** - Cloud features are completely optional
- **Secure Auth** - Firebase handles password security
- **No Tracking** - We don't track your browsing or sell data
- **Open Source** - Full transparency in how your data is handled

## 🎨 Why You'll Love It

TabSense Declutter isn't just another tab manager - it's a delightful companion that makes tab organization fun! Watch your dog jump for joy when you maintain good tab hygiene, or see it get sad when tabs pile up. The beautiful animations and personality-filled interactions make mundane tab management an enjoyable experience.

## 🔮 Future Improvements

- More dog expressions and animations
- Additional mascot options (cats, other pets)
- Advanced tab categorization
- Team/workspace sharing features
- Browser performance insights
- Custom themes and backgrounds

## Contributing

1. Fork the repository
2. Create a feature branch
3. Make your changes
4. Submit a pull request

## License

MIT License - See LICENSE file for details

## 🏷️ About

**TabSense Declutter** - Smart Tab Manager with Adorable Dog Mascot

Built by Jacob

---

**Need help?** Check the troubleshooting section above.

**Love the extension?** Give it a ⭐ on GitHub and share it with your friends!