import pandas as pd
import numpy as np
from datetime import datetime, timedelta
from sklearn.ensemble import RandomForestClassifier
from sklearn.preprocessing import StandardScaler
from sklearn.model_selection import train_test_split
import joblib

class TabClassifier:
    """
    ML model to classify tabs for decluttering suggestions
    """
    def __init__(self):
        self.model = RandomForestClassifier(
            n_estimators=100,
            max_depth=10,
            random_state=42
        )
        self.scaler = StandardScaler()
        self.feature_names = [
            'days_since_created',
            'days_since_activated',
            'activation_count',
            'total_active_time_minutes',
            'avg_active_time_per_visit',
            'is_pinned',
            'has_group',
            'domain_frequency',
            'hour_of_day',
            'day_of_week'
        ]
        
    def prepare_features(self, tab_data):
        """
        Convert tab data into ML features
        """
        features = []
        now = datetime.now()
        
        for tab in tab_data:
            created_at = datetime.fromtimestamp(tab['createdAt'] / 1000)
            last_activated = datetime.fromtimestamp(tab['lastActivated'] / 1000)
            
            # Time-based features
            days_since_created = (now - created_at).days
            days_since_activated = (now - last_activated).days
            
            # Activity features
            activation_count = tab.get('activationCount', 0)
            total_active_time = tab.get('totalActiveTime', 0) / 60000  # Convert to minutes
            avg_active_time = total_active_time / max(activation_count, 1)
            
            # Tab properties
            is_pinned = 1 if tab.get('isPinned', False) else 0
            has_group = 1 if tab.get('groupId', -1) != -1 else 0
            
            # Domain frequency (would need aggregation across all tabs)
            domain_frequency = tab.get('domainFrequency', 1)
            
            # Time context
            hour_of_day = last_activated.hour
            day_of_week = last_activated.weekday()
            
            features.append([
                days_since_created,
                days_since_activated,
                activation_count,
                total_active_time,
                avg_active_time,
                is_pinned,
                has_group,
                domain_frequency,
                hour_of_day,
                day_of_week
            ])
            
        return np.array(features)
    
    def classify_tabs(self, tab_data):
        """
        Classify tabs into categories:
        - keep: Important, frequently used
        - close: Can be safely closed
        - review: Needs user review
        - archive: Bookmark and close
        """
        features = self.prepare_features(tab_data)
        
        # Rule-based classification (can be replaced with trained model)
        classifications = []
        
        for i, tab in enumerate(tab_data):
            feat = features[i]
            
            # Pinned tabs are always kept
            if feat[5] == 1:  # is_pinned
                classifications.append({
                    'id': tab['id'],
                    'action': 'keep',
                    'reason': 'Pinned tab',
                    'confidence': 1.0
                })
                continue
            
            # Never activated and old = close
            if feat[2] == 0 and feat[0] > 1:  # activation_count == 0 and days_since_created > 1
                classifications.append({
                    'id': tab['id'],
                    'action': 'close',
                    'reason': 'Never used',
                    'confidence': 0.95
                })
                continue
            
            # Not used in 7+ days = archive
            if feat[1] > 7:  # days_since_activated > 7
                classifications.append({
                    'id': tab['id'],
                    'action': 'archive',
                    'reason': f'Not used in {int(feat[1])} days',
                    'confidence': 0.85
                })
                continue
            
            # Low activation and old = close
            if feat[2] < 3 and feat[0] > 3:
                classifications.append({
                    'id': tab['id'],
                    'action': 'close',
                    'reason': 'Rarely used',
                    'confidence': 0.75
                })
                continue
            
            # Frequently used = keep
            if feat[2] > 10 or feat[3] > 30:  # Many activations or long active time
                classifications.append({
                    'id': tab['id'],
                    'action': 'keep',
                    'reason': 'Frequently used',
                    'confidence': 0.9
                })
                continue
            
            # Default = review
            classifications.append({
                'id': tab['id'],
                'action': 'review',
                'reason': 'Moderate usage',
                'confidence': 0.5
            })
        
        return classifications
    
    def find_duplicates(self, tab_data):
        """
        Find duplicate tabs by URL
        """
        url_map = {}
        duplicates = []
        
        for tab in tab_data:
            url = tab.get('url', '')
            if url:
                if url not in url_map:
                    url_map[url] = []
                url_map[url].append(tab)
        
        for url, tabs in url_map.items():
            if len(tabs) > 1:
                # Keep the most recently activated, suggest closing others
                sorted_tabs = sorted(tabs, key=lambda t: t.get('lastActivated', 0), reverse=True)
                keep_tab = sorted_tabs[0]
                close_tabs = sorted_tabs[1:]
                
                duplicates.append({
                    'url': url,
                    'keep': {
                        'id': keep_tab['id'],
                        'title': keep_tab.get('title', ''),
                        'lastActivated': keep_tab.get('lastActivated', 0)
                    },
                    'close': [
                        {
                            'id': t['id'],
                            'title': t.get('title', '')
                        } for t in close_tabs
                    ]
                })
        
        return duplicates
    
    def suggest_groups(self, tab_data):
        """
        Suggest tab groupings based on domain and usage patterns
        """
        domain_groups = {}
        
        for tab in tab_data:
            domain = tab.get('domain', '')
            if domain and tab.get('groupId', -1) == -1:  # Not already grouped
                if domain not in domain_groups:
                    domain_groups[domain] = []
                domain_groups[domain].append(tab)
        
        suggestions = []
        for domain, tabs in domain_groups.items():
            if len(tabs) >= 3:  # Only suggest grouping for 3+ tabs
                suggestions.append({
                    'domain': domain,
                    'name': self._generate_group_name(domain),
                    'tabs': [
                        {
                            'id': t['id'],
                            'title': t.get('title', ''),
                            'url': t.get('url', '')
                        } for t in tabs
                    ],
                    'count': len(tabs)
                })
        
        return sorted(suggestions, key=lambda x: x['count'], reverse=True)
    
    def _generate_group_name(self, domain):
        """
        Generate a friendly group name from domain
        """
        # Remove common prefixes/suffixes
        name = domain.replace('www.', '').replace('.com', '').replace('.org', '')
        
        # Special cases
        if 'github' in name:
            return 'GitHub'
        elif 'google' in name:
            return 'Google'
        elif 'stackoverflow' in name:
            return 'Stack Overflow'
        elif 'youtube' in name:
            return 'YouTube'
        else:
            # Capitalize first letter
            return name.capitalize()
    
    def calculate_tab_health_score(self, tab_data):
        """
        Calculate overall tab health score (0-100)
        Lower score = needs decluttering
        """
        total_tabs = len(tab_data)
        if total_tabs == 0:
            return 100
        
        # Factors that decrease health score
        never_used = sum(1 for t in tab_data if t.get('activationCount', 0) == 0)
        old_tabs = sum(1 for t in tab_data if self._days_old(t.get('createdAt', 0)) > 7)
        inactive_tabs = sum(1 for t in tab_data if self._days_old(t.get('lastActivated', 0)) > 3)
        
        # Calculate penalties
        never_used_penalty = (never_used / total_tabs) * 30
        old_tabs_penalty = (old_tabs / total_tabs) * 20
        inactive_penalty = (inactive_tabs / total_tabs) * 20
        too_many_penalty = max(0, (total_tabs - 20) * 1) if total_tabs > 20 else 0
        
        # Base score minus penalties
        score = 100 - never_used_penalty - old_tabs_penalty - inactive_penalty - too_many_penalty
        
        return max(0, min(100, score))
    
    def _days_old(self, timestamp_ms):
        """
        Calculate days since timestamp
        """
        if timestamp_ms == 0:
            return 0
        then = datetime.fromtimestamp(timestamp_ms / 1000)
        now = datetime.now()
        return (now - then).days


def analyze_tabs(tab_data):
    """
    Main function to analyze tabs and provide suggestions
    """
    classifier = TabClassifier()
    
    # Classify all tabs
    classifications = classifier.classify_tabs(tab_data)
    
    # Find duplicates
    duplicates = classifier.find_duplicates(tab_data)
    
    # Suggest groups
    group_suggestions = classifier.suggest_groups(tab_data)
    
    # Calculate health score
    health_score = classifier.calculate_tab_health_score(tab_data)
    
    # Compile results
    results = {
        'health_score': health_score,
        'total_tabs': len(tab_data),
        'classifications': classifications,
        'duplicates': duplicates,
        'group_suggestions': group_suggestions,
        'summary': {
            'to_close': len([c for c in classifications if c['action'] == 'close']),
            'to_archive': len([c for c in classifications if c['action'] == 'archive']),
            'to_keep': len([c for c in classifications if c['action'] == 'keep']),
            'to_review': len([c for c in classifications if c['action'] == 'review']),
            'duplicate_tabs': sum(len(d['close']) for d in duplicates),
            'grouping_opportunities': len(group_suggestions)
        }
    }
    
    return results