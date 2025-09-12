from flask import Flask, jsonify, request
from flask_cors import CORS
import firebase_admin
from firebase_admin import credentials, firestore
from tab_classifier import analyze_tabs
import os

app = Flask(__name__)
CORS(app)

# Initialize Firebase
cred = credentials.Certificate("serviceAccountKey.json")
firebase_admin.initialize_app(cred)
db = firestore.client()

print("TabSense Declutter Server ready")

@app.route('/analyze', methods=['POST'])
def analyze_tab_data():
    """
    Analyze tab data and return declutter suggestions
    """
    try:
        data = request.json
        tabs = data.get('tabs', [])
        email = data.get('email', '')
        
        if not tabs:
            return jsonify({'error': 'No tabs provided'}), 400
        
        # Analyze tabs using ML classifier
        results = analyze_tabs(tabs)
        
        # Store analysis results for user
        if email:
            user_doc_ref = db.collection('TabAnalysis').document(email)
            user_doc_ref.set({
                'last_analysis': results,
                'timestamp': firestore.SERVER_TIMESTAMP
            })
        
        return jsonify(results)
        
    except Exception as e:
        print(f"Error analyzing tabs: {str(e)}")
        return jsonify({'error': str(e)}), 500

@app.route('/stats/<email>/')
def get_user_stats(email):
    """Get user's tab statistics"""
    try:
        user_doc_ref = db.collection('TabActivity').document(email)
        user_doc = user_doc_ref.get()
        
        if not user_doc.exists:
            return jsonify({
                'totalTabs': 0,
                'healthScore': 100,
                'patterns': {}
            })
        
        data = user_doc.to_dict()
        tabs = data.get('tabs', {})
        
        # Calculate statistics
        stats = {
            'totalTabs': len(tabs),
            'activeTabs': sum(1 for t in tabs.values() if t.get('isActive')),
            'pinnedTabs': sum(1 for t in tabs.values() if t.get('isPinned')),
            'forgottenTabs': sum(1 for t in tabs.values() if t.get('status') == 'forgotten'),
            'unusedTabs': sum(1 for t in tabs.values() if t.get('status') == 'unused'),
        }
        
        return jsonify(stats)
        
    except Exception as e:
        print(f"Error getting stats: {str(e)}")
        return jsonify({'error': str(e)}), 500

@app.route('/health')
def health_check():
    """Health check endpoint"""
    return jsonify({
        'status': 'healthy',
        'service': 'TabSense Declutter Server'
    })

if __name__ == '__main__':
    port = int(os.environ.get('PORT', 5001))
    app.run(host='0.0.0.0', port=port, debug=True)