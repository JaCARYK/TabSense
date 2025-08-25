# TabSense Quick Start Guide

## 🚀 5-Minute Setup

### 1. Firebase Setup (2 min)
1. Go to [Firebase Console](https://console.firebase.google.com)
2. Create new project
3. Enable Email/Password Authentication
4. Create Firestore Database (test mode is fine for development)
5. Get your config from Project Settings

### 2. Configure Files (1 min)
Replace placeholder values in:
- `chrome-extension/firebase-config.js`
- `chrome-extension/background.js` (lines 15-22)
- `flask-server/serviceAccountKey.json` (download from Firebase Console)

### 3. Install Extension (1 min)
1. Open `chrome://extensions/`
2. Enable Developer mode
3. Load unpacked → select `chrome-extension` folder

### 4. Start Server (1 min)
```bash
cd flask-server
python3 -m venv venv
source venv/bin/activate  # Windows: venv\Scripts\activate
pip install -r requirements.txt
python app.py
```

## 📱 Using TabSense

1. Click extension icon → Sign up
2. Browse 5+ different websites
3. See predictions appear in popup!

## 🧪 Test Without Firebase

Run the ML model test:
```bash
cd flask-server
python test_model.py
```

## 🔧 Troubleshooting

| Issue | Solution |
|-------|----------|
| No predictions | Need 5+ URLs in history |
| Extension not working | Check Firebase config |
| Server errors | Verify serviceAccountKey.json |
| CORS errors | Ensure Flask server is running |

## 📊 How It Works

1. **You browse** → Extension tracks URLs + timestamps
2. **Data stored** → Firebase Firestore (per user)
3. **ML predicts** → Random Forest analyzes patterns
4. **Smart suggestions** → Next URL predicted based on current context

## 🎯 Best Use Cases

- Daily routines (email → calendar → work sites)
- School schedules (different class URLs at set times)
- Work workflows (ticket system → docs → code repo)

## Need Help?

Check the full [README.md](README.md) for detailed instructions.