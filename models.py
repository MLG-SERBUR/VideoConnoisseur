"""
Machine Learning Models Module
Handles model loading and prediction
"""

import numpy as np
import json
from sklearn.ensemble import RandomForestRegressor
import joblib
import os
import logging

logger = logging.getLogger(__name__)

class ScorePredictor:
    def __init__(self):
        self.model = RandomForestRegressor(n_estimators=100, random_state=42)
        self.is_trained = False
        self.feature_names = [
            'heard_keyword_victory',
            'heard_keyword_glitch',
            'heard_speaker_change',
            'heard_high_energy',
            'saw_win_screen',
            'saw_glitch_effect',
            'saw_object_detected'
        ]
    
    def train(self, X, y):
        """Train the model."""
        self.model.fit(X, y)
        self.is_trained = True
        logger.info("Model trained successfully")
    
    def predict(self, features):
        """Predict score based on features."""
        if not self.is_trained:
            # Return default score based on weighted features
            return self._calculate_default_score(features)
        
        # Convert features to model input format
        X = np.array([[features.get(feat, 0) for feat in self.feature_names]])
        prediction = self.model.predict(X)[0]
        
        # Ensure prediction is reasonable
        return max(0, min(100, prediction))
    
    def _calculate_default_score(self, features):
        """Calculate score using weighted features when model is not trained."""
        weights = self._get_default_weights()
        score = 0
        
        for feature_name, feature_value in features.items():
            weight = weights.get(feature_name, 1.0)
            score += feature_value * weight
        
        # Normalize to 0-100 range
        max_possible = sum(weights.values())
        if max_possible > 0:
            score = (score / max_possible) * 100
        
        return score
    
    def _get_default_weights(self):
        """Get default weights for feature scoring."""
        return {
            'heard_keyword_victory': 10,
            'heard_keyword_glitch': 8,
            'heard_speaker_change': 3,
            'heard_high_energy': 5,
            'saw_win_screen': 15,
            'saw_glitch_effect': 12,
            'saw_object_detected': 4
        }
    
    def update_with_feedback(self, features, actual_score, learning_rate=0.1):
        """Update model based on user feedback (self-adjusting learning)."""
        # This is a simplified update mechanism
        # In practice, you'd want to retrain the model with new data
        pass
    
    def save_model(self, filepath='models/model.joblib'):
        """Save the trained model."""
        os.makedirs(os.path.dirname(filepath), exist_ok=True)
        joblib.dump(self.model, filepath)
        logger.info(f"Model saved to {filepath}")
    
    def load_model(self, filepath='models/model.joblib'):
        """Load a trained model."""
        try:
            self.model = joblib.load(filepath)
            self.is_trained = True
            logger.info(f"Model loaded from {filepath}")
        except FileNotFoundError:
            logger.info("No pre-trained model found, using default scoring")
            pass