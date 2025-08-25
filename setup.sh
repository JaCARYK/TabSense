#!/bin/bash

echo "======================================"
echo "TabSense Setup Script"
echo "======================================"

# Check Python version
echo "Checking Python version..."
python_version=$(python3 --version 2>&1 | grep -Po '(?<=Python )\d+\.\d+')
required_version="3.8"

if [ "$(printf '%s\n' "$required_version" "$python_version" | sort -V | head -n1)" = "$required_version" ]; then 
    echo "✓ Python $python_version is installed"
else
    echo "✗ Python 3.8+ is required. Current version: $python_version"
    exit 1
fi

# Set up Flask server
echo ""
echo "Setting up Flask server..."
cd flask-server

# Create virtual environment if it doesn't exist
if [ ! -d "venv" ]; then
    echo "Creating virtual environment..."
    python3 -m venv venv
fi

# Activate virtual environment
echo "Activating virtual environment..."
source venv/bin/activate

# Install dependencies
echo "Installing Python dependencies..."
pip install -r requirements.txt

# Check for Firebase service account key
if [ ! -f "serviceAccountKey.json" ] || grep -q "YOUR_" serviceAccountKey.json; then
    echo ""
    echo "⚠️  WARNING: serviceAccountKey.json is missing or not configured!"
    echo "   Please add your Firebase service account key to flask-server/serviceAccountKey.json"
fi

# Test the ML model
echo ""
echo "Testing ML model..."
python test_model.py

echo ""
echo "======================================"
echo "Setup Complete!"
echo "======================================"
echo ""
echo "Next steps:"
echo "1. Configure Firebase:"
echo "   - Update chrome-extension/firebase-config.js"
echo "   - Update chrome-extension/background.js (lines 15-22)"
echo "   - Add serviceAccountKey.json to flask-server/"
echo ""
echo "2. Load the Chrome extension:"
echo "   - Open chrome://extensions/"
echo "   - Enable Developer mode"
echo "   - Click 'Load unpacked'"
echo "   - Select the chrome-extension folder"
echo ""
echo "3. Start the Flask server:"
echo "   cd flask-server"
echo "   source venv/bin/activate"
echo "   python app.py"
echo ""
echo "4. Use TabSense:"
echo "   - Click the extension icon"
echo "   - Sign up/Login"
echo "   - Browse normally to train the model"
echo "   - Get smart tab predictions!"