#!/usr/bin/env python3
"""
Test script for TabSense ML model
Run this to verify the ML components work correctly
"""

import numpy as np
from datetime import datetime, timedelta
from ml_model import TabSensePredictor, compare_models, analyze_browsing_patterns
from feature_analysis import FeatureAnalyzer, generate_feature_report

def generate_sample_data():
    """Generate sample browsing data for testing"""
    sample_data = {}
    base_time = datetime.now() - timedelta(days=7)
    
    # Simulate daily patterns
    urls = [
        "google.com",
        "gmail.com", 
        "calendar.google.com",
        "github.com",
        "stackoverflow.com",
        "youtube.com",
        "docs.google.com",
        "slack.com",
        "linkedin.com",
        "reddit.com"
    ]
    
    # Morning routine (8-10 AM)
    for day in range(7):
        current_day = base_time + timedelta(days=day)
        
        # Morning emails and calendar
        morning_time = current_day.replace(hour=8, minute=30, second=0)
        sample_data[morning_time.strftime("%Y-%m-%d %H:%M:%S")] = "gmail.com"
        
        morning_time = current_day.replace(hour=8, minute=32, second=0)
        sample_data[morning_time.strftime("%Y-%m-%d %H:%M:%S")] = "calendar.google.com"
        
        # Work sites (9-12 AM)
        for hour in range(9, 12):
            for minute in [0, 15, 30, 45]:
                work_time = current_day.replace(hour=hour, minute=minute, second=0)
                url = np.random.choice(["github.com", "stackoverflow.com", "docs.google.com"])
                sample_data[work_time.strftime("%Y-%m-%d %H:%M:%S")] = url
        
        # Lunch break (12-1 PM)
        lunch_time = current_day.replace(hour=12, minute=30, second=0)
        sample_data[lunch_time.strftime("%Y-%m-%d %H:%M:%S")] = "youtube.com"
        
        # Afternoon work (1-5 PM)
        for hour in range(13, 17):
            for minute in [0, 30]:
                work_time = current_day.replace(hour=hour, minute=minute, second=0)
                url = np.random.choice(["slack.com", "github.com", "docs.google.com"])
                sample_data[work_time.strftime("%Y-%m-%d %H:%M:%S")] = url
        
        # Evening browsing (6-8 PM)
        for hour in range(18, 20):
            evening_time = current_day.replace(hour=hour, minute=0, second=0)
            url = np.random.choice(["reddit.com", "youtube.com", "linkedin.com"])
            sample_data[evening_time.strftime("%Y-%m-%d %H:%M:%S")] = url
    
    return sample_data

def test_prediction():
    """Test the prediction functionality"""
    print("=" * 60)
    print("Testing TabSense ML Model")
    print("=" * 60)
    
    # Generate sample data
    print("\n1. Generating sample browsing data...")
    sample_data = generate_sample_data()
    print(f"   Generated {len(sample_data)} browsing records")
    
    # Test predictor
    print("\n2. Testing TabSensePredictor...")
    predictor = TabSensePredictor()
    
    # Train the model
    success = predictor.train(sample_data)
    if success:
        print("   ✓ Model trained successfully")
    else:
        print("   ✗ Model training failed")
        return
    
    # Test prediction
    now = datetime.now()
    test_url = "github.com"
    prediction = predictor.predict(
        now.month, 
        now.day, 
        now.hour, 
        now.minute, 
        test_url
    )
    
    if prediction:
        print(f"   ✓ Prediction successful: {test_url} -> {prediction}")
    else:
        print("   ✗ Prediction failed")
    
    # Get feature importance
    importance = predictor.get_feature_importance()
    if importance:
        print("\n3. Feature Importance:")
        for feature, score in sorted(importance.items(), key=lambda x: x[1], reverse=True):
            print(f"   {feature}: {score:.4f}")
    
    # Test model comparison
    print("\n4. Comparing ML Models...")
    comparison = compare_models(sample_data)
    if comparison:
        for model, results in comparison.items():
            print(f"   {model}: {results['mean_accuracy']:.3f} ± {results['std_accuracy']:.3f}")
    
    # Analyze browsing patterns
    print("\n5. Analyzing Browsing Patterns...")
    patterns = analyze_browsing_patterns(sample_data)
    if patterns:
        print(f"   Total visits: {patterns['total_visits']}")
        print(f"   Unique sites: {patterns['unique_domains']}")
        print(f"   Most visited: {patterns['most_visited_sites'][0] if patterns['most_visited_sites'] else 'N/A'}")
    
    # Test feature analyzer
    print("\n6. Testing Feature Analyzer...")
    analyzer = FeatureAnalyzer()
    
    importance_df = analyzer.calculate_feature_importance(sample_data)
    if importance_df is not None:
        print("   ✓ Feature importance calculated")
    
    time_importance = analyzer.analyze_time_granularity(sample_data)
    if time_importance:
        print("   ✓ Time granularity analyzed")
    
    cv_results = analyzer.cross_validation_with_smote(sample_data)
    if cv_results:
        print("   ✓ Cross-validation completed")
        print(f"      Without SMOTE: {cv_results['without_smote']['cv_3']['mean']:.3f}")
        print(f"      With SMOTE: {cv_results['with_smote']['cv_3']['mean']:.3f}")
    
    interval_results = analyzer.analyze_prediction_intervals(sample_data)
    if interval_results:
        print("   ✓ Optimal intervals analyzed")
        best_interval = max(interval_results.items(), key=lambda x: x[1]['accuracy'])
        print(f"      Best interval: {best_interval[0]} (accuracy: {best_interval[1]['accuracy']:.3f})")
    
    print("\n" + "=" * 60)
    print("All tests completed!")
    print("=" * 60)

if __name__ == "__main__":
    test_prediction()