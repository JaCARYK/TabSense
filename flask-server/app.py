from flask import Flask, jsonify
from flask_cors import CORS
import firebase_admin
from firebase_admin import credentials, firestore
import pandas as pd
import numpy as np
from datetime import datetime
import os

app = Flask(__name__)
CORS(app)

cred = credentials.Certificate("serviceAccountKey.json")
firebase_admin.initialize_app(cred)
db = firestore.client()

print("Flask server ready")

@app.route('/predict/<int:month>/<int:day>/<int:hour>/<int:minute>/<url>/<email>/')
def predict(month, day, hour, minute, url, email):
    """
    Main prediction endpoint that takes current time and URL, 
    returns predicted next URL based on user's browsing history
    """
    try:
        print(f"Prediction request for {email}")
        print(f"Current time: {month}/{day} {hour}:{minute}")
        print(f"Current URL: {url}")
        
        user_doc_ref = db.collection('Data').document(email)
        user_doc = user_doc_ref.get()
        
        if not user_doc.exists:
            return "Not enough data to predict."
        
        data = user_doc.to_dict()
        
        if len(data) < 5:
            return "Not enough data to predict."
        
        from ml_model import predict_next_url
        
        prediction = predict_next_url(data, month, day, hour, minute, url)
        
        if prediction:
            print(f"Predicted URL: {prediction}")
            return prediction
        else:
            return "Not enough data to predict."
            
    except Exception as e:
        print(f"Error in prediction: {str(e)}")
        return "Error occurred during prediction"

@app.route('/stats/<email>/')
def get_stats(email):
    """Get user statistics for the extension popup"""
    try:
        user_doc_ref = db.collection('Data').document(email)
        user_doc = user_doc_ref.get()
        
        if not user_doc.exists:
            return jsonify({
                'totalUrls': 0,
                'uniqueSites': 0,
                'mostVisited': None
            })
        
        data = user_doc.to_dict()
        urls = list(data.values())
        unique_sites = len(set(urls))
        
        from collections import Counter
        url_counts = Counter(urls)
        most_visited = url_counts.most_common(1)[0][0] if url_counts else None
        
        return jsonify({
            'totalUrls': len(data),
            'uniqueSites': unique_sites,
            'mostVisited': most_visited
        })
        
    except Exception as e:
        print(f"Error getting stats: {str(e)}")
        return jsonify({'error': str(e)}), 500

@app.route('/health')
def health_check():
    """Health check endpoint"""
    return jsonify({'status': 'healthy', 'service': 'TabSense ML Server'})

if __name__ == '__main__':
    port = int(os.environ.get('PORT', 5000))
    app.run(host='0.0.0.0', port=port, debug=True)