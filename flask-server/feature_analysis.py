import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
from sklearn.ensemble import RandomForestClassifier
from sklearn.model_selection import cross_val_score
from sklearn.preprocessing import LabelEncoder
from imblearn.over_sampling import SMOTE
import seaborn as sns
from datetime import datetime

class FeatureAnalyzer:
    def __init__(self):
        self.feature_names = ['Month', 'Day', 'Hour', 'Minute', 'Second', 'Current URL']
        
    def calculate_feature_importance(self, user_data):
        """
        Calculate and visualize feature importance for prediction model
        """
        from ml_model import TabSensePredictor
        
        predictor = TabSensePredictor()
        X, y = predictor.prepare_data(user_data)
        
        if len(X) < 10:
            print("Not enough data for feature importance analysis")
            return None
        
        predictor.output_encoder.fit(y)
        y_encoded = predictor.output_encoder.transform(y)
        
        try:
            X_resampled, y_resampled = predictor.smote.fit_resample(X, y_encoded)
        except:
            X_resampled, y_resampled = X, y_encoded
        
        predictor.model.fit(X_resampled, y_resampled)
        
        importances = predictor.model.feature_importances_
        
        importance_df = pd.DataFrame({
            'Feature': self.feature_names,
            'Importance': importances
        }).sort_values('Importance', ascending=False)
        
        return importance_df
    
    def plot_feature_importance(self, importance_df, save_path='feature_importance.png'):
        """
        Create a bar plot of feature importance
        """
        plt.figure(figsize=(10, 6))
        plt.bar(importance_df['Feature'], importance_df['Importance'])
        plt.xlabel('Features')
        plt.ylabel('Importance Score')
        plt.title('Feature Importance for URL Prediction')
        plt.xticks(rotation=45)
        plt.tight_layout()
        plt.savefig(save_path)
        plt.close()
        
        print(f"Feature importance plot saved to {save_path}")
    
    def analyze_time_granularity(self, user_data):
        """
        Analyze importance of different time granularities
        """
        granularities = {
            'Month': [],
            'Day': [],
            'Hour': [],
            'Minute': [],
            'Second': []
        }
        
        for _ in range(10):
            from ml_model import TabSensePredictor
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
            
            predictor.model.fit(X_resampled, y_resampled)
            importances = predictor.model.feature_importances_
            
            for i, feature in enumerate(self.feature_names[:5]):
                granularities[feature].append(importances[i])
        
        avg_importance = {k: np.mean(v) for k, v in granularities.items()}
        
        return avg_importance
    
    def cross_validation_with_smote(self, user_data, cv_splits=[3, 5, 7]):
        """
        Perform cross-validation with different splits and SMOTE
        """
        from ml_model import TabSensePredictor
        
        predictor = TabSensePredictor()
        X, y = predictor.prepare_data(user_data)
        
        if len(X) < 10:
            return None
        
        predictor.output_encoder.fit(y)
        y_encoded = predictor.output_encoder.transform(y)
        
        results = {
            'without_smote': {},
            'with_smote': {}
        }
        
        for cv in cv_splits:
            scores_without = cross_val_score(predictor.model, X, y_encoded, cv=min(cv, len(X)))
            results['without_smote'][f'cv_{cv}'] = {
                'mean': np.mean(scores_without),
                'std': np.std(scores_without)
            }
            
            try:
                X_resampled, y_resampled = predictor.smote.fit_resample(X, y_encoded)
                scores_with = cross_val_score(predictor.model, X_resampled, y_resampled, cv=min(cv, len(X_resampled)))
                results['with_smote'][f'cv_{cv}'] = {
                    'mean': np.mean(scores_with),
                    'std': np.std(scores_with)
                }
            except:
                results['with_smote'][f'cv_{cv}'] = {
                    'mean': 0,
                    'std': 0
                }
        
        return results
    
    def plot_model_comparison(self, comparison_results, save_path='model_comparison.png'):
        """
        Plot comparison of different models
        """
        if not comparison_results:
            return
        
        models = list(comparison_results.keys())
        accuracies = [comparison_results[m]['mean_accuracy'] for m in models]
        stds = [comparison_results[m]['std_accuracy'] for m in models]
        
        plt.figure(figsize=(10, 6))
        x = np.arange(len(models))
        plt.bar(x, accuracies, yerr=stds, capsize=5, color=['blue', 'red', 'green'])
        plt.xlabel('Models')
        plt.ylabel('Accuracy')
        plt.title('Model Comparison with Cross-Validation')
        plt.xticks(x, models)
        plt.ylim(0, 1)
        
        for i, (acc, std) in enumerate(zip(accuracies, stds)):
            plt.text(i, acc + std + 0.02, f'{acc:.3f}', ha='center')
        
        plt.tight_layout()
        plt.savefig(save_path)
        plt.close()
        
        print(f"Model comparison plot saved to {save_path}")
    
    def analyze_prediction_intervals(self, user_data, intervals=[30, 60, 120, 300, 600]):
        """
        Analyze optimal time intervals for prediction (in seconds)
        """
        from ml_model import TabSensePredictor
        
        results = {}
        
        for interval in intervals:
            predictor = TabSensePredictor()
            X, y = predictor.prepare_data(user_data, time_window_minutes=interval/60)
            
            if len(X) < 2:
                results[f'{interval}s'] = {'accuracy': 0, 'samples': 0}
                continue
            
            predictor.output_encoder.fit(y)
            y_encoded = predictor.output_encoder.transform(y)
            
            try:
                X_resampled, y_resampled = predictor.smote.fit_resample(X, y_encoded)
                predictor.model.fit(X_resampled, y_resampled)
                scores = cross_val_score(predictor.model, X_resampled, y_resampled, cv=3)
                accuracy = np.mean(scores)
            except:
                accuracy = 0
            
            results[f'{interval}s'] = {
                'accuracy': accuracy,
                'samples': len(X)
            }
        
        return results

def generate_feature_report(user_data):
    """
    Generate a comprehensive feature importance report
    """
    analyzer = FeatureAnalyzer()
    
    print("=" * 50)
    print("TabSense Feature Importance Analysis Report")
    print("=" * 50)
    
    importance_df = analyzer.calculate_feature_importance(user_data)
    if importance_df is not None:
        print("\n1. Feature Importance Scores:")
        print(importance_df.to_string())
        analyzer.plot_feature_importance(importance_df)
    
    time_importance = analyzer.analyze_time_granularity(user_data)
    if time_importance:
        print("\n2. Average Time Granularity Importance:")
        for feature, importance in sorted(time_importance.items(), key=lambda x: x[1], reverse=True):
            print(f"   {feature}: {importance:.4f}")
    
    cv_results = analyzer.cross_validation_with_smote(user_data)
    if cv_results:
        print("\n3. Cross-Validation Results:")
        print("   Without SMOTE:")
        for cv, scores in cv_results['without_smote'].items():
            print(f"      {cv}: {scores['mean']:.3f} ± {scores['std']:.3f}")
        print("   With SMOTE:")
        for cv, scores in cv_results['with_smote'].items():
            print(f"      {cv}: {scores['mean']:.3f} ± {scores['std']:.3f}")
    
    interval_results = analyzer.analyze_prediction_intervals(user_data)
    if interval_results:
        print("\n4. Optimal Time Interval Analysis:")
        for interval, result in interval_results.items():
            print(f"   {interval}: Accuracy={result['accuracy']:.3f}, Samples={result['samples']}")
    
    from ml_model import compare_models
    model_comparison = compare_models(user_data)
    if model_comparison:
        print("\n5. Model Comparison:")
        for model, scores in model_comparison.items():
            print(f"   {model}: {scores['mean_accuracy']:.3f} ± {scores['std_accuracy']:.3f}")
        analyzer.plot_model_comparison(model_comparison)
    
    print("\n" + "=" * 50)
    print("Report Complete")
    print("=" * 50)