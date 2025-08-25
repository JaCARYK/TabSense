import pandas as pd
import numpy as np
from datetime import datetime, timedelta
from sklearn.model_selection import cross_val_score
from sklearn.ensemble import RandomForestClassifier
from sklearn.svm import SVC
from sklearn.linear_model import PassiveAggressiveClassifier
from sklearn.preprocessing import LabelEncoder
from imblearn.over_sampling import SMOTE
from collections import Counter
import warnings
warnings.filterwarnings('ignore')

class TabSensePredictor:
    def __init__(self):
        self.input_encoder = LabelEncoder()
        self.output_encoder = LabelEncoder()
        self.model = RandomForestClassifier(
            n_estimators=100,
            max_depth=10,
            random_state=42
        )
        self.smote = SMOTE(random_state=42)
        
    def prepare_data(self, user_data, time_window_minutes=2):
        """
        Prepare training data from user's browsing history
        time_window_minutes: time interval to consider for next URL prediction
        """
        input_data = []
        output_data = []
        
        sorted_timestamps = sorted(user_data.keys())
        
        for i in range(len(sorted_timestamps) - 1):
            current_time = datetime.strptime(sorted_timestamps[i], "%Y-%m-%d %H:%M:%S")
            next_time = datetime.strptime(sorted_timestamps[i + 1], "%Y-%m-%d %H:%M:%S")
            
            time_diff = (next_time - current_time).total_seconds() / 60
            
            if time_diff <= time_window_minutes:
                current_url = user_data[sorted_timestamps[i]]
                next_url = user_data[sorted_timestamps[i + 1]]
                
                features = [
                    current_time.month,
                    current_time.day,
                    current_time.hour,
                    current_time.minute,
                    current_time.second,
                    self.encode_url(current_url)
                ]
                
                input_data.append(features)
                output_data.append(next_url)
        
        return np.array(input_data), np.array(output_data)
    
    def encode_url(self, url):
        """Convert URL to numeric encoding"""
        try:
            url_hash = hash(url) % 10000
            return url_hash
        except:
            return 0
    
    def train(self, user_data):
        """Train the model on user's browsing history"""
        X, y = self.prepare_data(user_data)
        
        if len(X) < 2:
            return False
        
        self.output_encoder.fit(y)
        y_encoded = self.output_encoder.transform(y)
        
        try:
            X_resampled, y_resampled = self.smote.fit_resample(X, y_encoded)
        except:
            X_resampled, y_resampled = X, y_encoded
        
        self.model.fit(X_resampled, y_resampled)
        
        score = cross_val_score(self.model, X_resampled, y_resampled, cv=3)
        print(f"Model accuracy: {np.mean(score):.2f}")
        
        return True
    
    def predict(self, month, day, hour, minute, current_url):
        """Predict the next URL based on current context"""
        features = [[
            month,
            day,
            hour,
            minute,
            0,
            self.encode_url(current_url)
        ]]
        
        try:
            prediction_encoded = self.model.predict(features)[0]
            prediction = self.output_encoder.inverse_transform([prediction_encoded])[0]
            return prediction
        except:
            return None
    
    def get_feature_importance(self):
        """Get feature importance scores"""
        if hasattr(self.model, 'feature_importances_'):
            feature_names = ['Month', 'Day', 'Hour', 'Minute', 'Second', 'Current URL']
            importances = self.model.feature_importances_
            return dict(zip(feature_names, importances))
        return None

def compare_models(user_data):
    """
    Compare performance of different ML models
    Returns accuracy scores for Random Forest, SVM, and Passive Aggressive
    """
    predictor = TabSensePredictor()
    X, y = predictor.prepare_data(user_data)
    
    if len(X) < 10:
        return None
    
    predictor.output_encoder.fit(y)
    y_encoded = predictor.output_encoder.transform(y)
    
    try:
        X_resampled, y_resampled = predictor.smote.fit_resample(X, y_encoded)
    except:
        X_resampled, y_resampled = X, y_encoded
    
    models = {
        'Random Forest': RandomForestClassifier(n_estimators=100, random_state=42),
        'SVM': SVC(kernel='rbf', random_state=42),
        'Passive Aggressive': PassiveAggressiveClassifier(random_state=42)
    }
    
    results = {}
    for name, model in models.items():
        scores = cross_val_score(model, X_resampled, y_resampled, cv=5)
        results[name] = {
            'mean_accuracy': np.mean(scores),
            'std_accuracy': np.std(scores),
            'scores': scores.tolist()
        }
    
    return results

def predict_next_url(user_data, month, day, hour, minute, current_url):
    """
    Main prediction function called by the Flask API
    """
    predictor = TabSensePredictor()
    
    if predictor.train(user_data):
        prediction = predictor.predict(month, day, hour, minute, current_url)
        
        importance = predictor.get_feature_importance()
        if importance:
            print(f"Feature importance: {importance}")
        
        return prediction
    
    return None

def analyze_browsing_patterns(user_data):
    """
    Analyze user's browsing patterns for insights
    """
    if not user_data:
        return None
    
    urls = list(user_data.values())
    timestamps = list(user_data.keys())
    
    url_counts = Counter(urls)
    
    datetimes = [datetime.strptime(ts, "%Y-%m-%d %H:%M:%S") for ts in timestamps]
    
    hour_distribution = Counter([dt.hour for dt in datetimes])
    day_distribution = Counter([dt.weekday() for dt in datetimes])
    
    patterns = {
        'most_visited_sites': url_counts.most_common(5),
        'total_sites': len(set(urls)),
        'total_visits': len(urls),
        'peak_hours': hour_distribution.most_common(3),
        'peak_days': day_distribution.most_common(3),
        'unique_domains': len(set(urls))
    }
    
    return patterns