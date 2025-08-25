# TabSense - Smart Tab Predictor

Chrome browser extension that uses Machine Learning to predict the next URL to open based on user browsing patterns and time.

## Features

- **Smart URL Prediction**: Uses Random Forest classifier to predict your next tab based on browsing history
- **User Authentication**: Secure login/signup system with Firebase
- **Real-time Tracking**: Automatically tracks browsing patterns
- **SMOTE Balancing**: Handles imbalanced datasets for better predictions
- **Feature Importance Analysis**: Understands which factors matter most for predictions
- **Privacy-Focused**: Data segregated per user with secure authentication

## Architecture

```
Chrome Extension (JavaScript) → Firebase Firestore → Flask API → ML Model (Python/scikit-learn)
```

## Setup Instructions

### Prerequisites

- Python 3.8+
- Node.js (for Firebase)
- Chrome browser
- Firebase account

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
5. The TabSense extension should now appear in your extensions list

### 4. Set up the Flask Server

1. Navigate to the flask-server directory:
```bash
cd flask-server
```

2. Create a virtual environment:
```bash
python -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate
```

3. Install dependencies:
```bash
pip install -r requirements.txt
```

4. Ensure your `serviceAccountKey.json` is in place with correct Firebase credentials

5. Run the server:
```bash
python app.py
```

The server will start on `http://localhost:5000`

### 5. Using TabSense

1. Click on the TabSense extension icon in Chrome
2. Sign up for a new account or login
3. Browse normally - the extension will track your tab patterns
4. After collecting enough data (5+ URLs), you'll start seeing predictions
5. Click on predicted URLs to open them in new tabs

## ML Models Comparison

The system compares three classifiers:
- **Random Forest** (default): Best overall performance
- **SVM**: Good for linear patterns
- **Passive Aggressive**: Fast online learning

## Time Intervals

The system analyzes different time windows:
- 30 seconds
- 1 minute
- 2 minutes (default)
- 5 minutes
- 10 minutes

## Feature Importance

The model considers:
1. **Second**: Most important (immediate context)
2. **Minute**: High importance
3. **Hour**: Medium importance
4. **Day**: Low importance
5. **Month**: Minimal importance
6. **Current URL**: Context-dependent

## API Endpoints

- `GET /predict/<month>/<day>/<hour>/<minute>/<url>/<email>/` - Get URL prediction
- `GET /stats/<email>/` - Get user statistics
- `GET /health` - Health check

## Testing the ML Model

Run feature analysis:
```python
from feature_analysis import generate_feature_report
# Load user data from Firebase
generate_feature_report(user_data)
```

## Troubleshooting

### Extension not tracking tabs
- Check that you're logged in
- Verify Firebase configuration is correct
- Check browser console for errors (F12)

### No predictions showing
- Ensure you have at least 5 URLs in history
- Check that Flask server is running
- Verify CORS is enabled

### Firebase connection issues
- Double-check Firebase configuration
- Ensure Firestore is initialized
- Verify service account key is valid

## Privacy & Security

- User passwords are handled by Firebase Auth
- Each user's data is segregated
- No cross-user data access
- URLs are stored as hostnames only
- Consider adding encryption for sensitive deployments

## Future Improvements

- Add more ML models (LSTM for sequences)
- Implement user feedback loop
- Add time-series analysis
- Create visualization dashboard
- Implement caching for faster predictions
- Add group/workspace features

## Contributing

1. Fork the repository
2. Create a feature branch
3. Make your changes
4. Submit a pull request

## License

MIT License - See LICENSE file for details

## Authors

TabSense - Smart Tab Prediction System

## Acknowledgments

- scikit-learn for ML algorithms
- Firebase for backend infrastructure
- SMOTE for handling imbalanced datasets