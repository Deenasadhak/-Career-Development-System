import os
import joblib
import pandas as pd
import numpy as np
from sklearn.ensemble import RandomForestClassifier
from django.conf import settings

# Path to save the model
MODEL_PATH = os.path.join(settings.BASE_DIR, 'core', 'career_model.joblib')

class CareerPredictor:
    def __init__(self):
        self.model = None
        self.courses = [
            'B.Tech Computer Science', 'MBBS', 'B.Com Finance', 'LLB Law', 
            'B.Sc Psychology', 'B.Des Fashion Design', 'BA English', 
            'BBA Management', 'B.Sc Physics', 'B.Arch Architecture'
        ]
        self._load_or_train()

    def _generate_synthetic_data(self, n=1000):
        """Generates synthetic training data based on Kerala student trends."""
        np.random.seed(42)
        
        # Features: aptitude (0-600), 12th% (0-100), 20 MCQ answers (1-4)
        aptitude = np.random.randint(200, 600, n)
        twelfth = np.random.randint(50, 100, n)
        mcq_responses = np.random.randint(1, 5, size=(n, 20))
        
        X = np.column_stack([aptitude, twelfth, mcq_responses])
        
        # Simple rule-based targets for synthetic data
        y = []
        for i in range(n):
            score = aptitude[i]
            # Analytical focus
            if score > 500 and mcq_responses[i, 0] == 1:
                y.append(self.courses[0]) # B.Tech CS
            # Medical focus
            elif twelfth[i] > 90 and mcq_responses[i, 1] == 4:
                y.append(self.courses[1]) # MBBS
            # Creative focus
            elif mcq_responses[i, 2] == 3:
                y.append(self.courses[5]) # B.Des
            # Business focus
            elif score > 400 and mcq_responses[i, 3] == 2:
                y.append(self.courses[7]) # BBA
            # Law focus
            elif mcq_responses[i, 4] == 2:
                y.append(self.courses[3]) # LLB
            else:
                y.append(np.random.choice(self.courses))
                
        return X, y

    def _load_or_train(self):
        if os.path.exists(MODEL_PATH):
            try:
                self.model = joblib.load(MODEL_PATH)
                print("ML Model loaded from disk.")
            except:
                self._train_new_model()
        else:
            self._train_new_model()

    def _train_new_model(self):
        print("Training new Career Prediction model...")
        X, y = self._generate_synthetic_data()
        self.model = RandomForestClassifier(n_estimators=100, random_state=42)
        self.model.fit(X, y)
        joblib.dump(self.model, MODEL_PATH)
        print(f"Model trained and saved to {MODEL_PATH}")

    def predict(self, aptitude_score, twelfth_percentage, mcq_responses):
        """
        aptitude_score: int (0-600)
        twelfth_percentage: float (0-100)
        mcq_responses: list of 20 ints (1-4)
        """
        if self.model is None:
            return "General Engineering"
            
        # Scale aptitude if it's 0-100 to 0-600
        if aptitude_score <= 100:
            aptitude_score = aptitude_score * 6

        features = np.array([aptitude_score, twelfth_percentage] + list(mcq_responses)).reshape(1, -1)
        prediction = self.model.predict(features)
        return prediction[0]

# Singleton instance
predictor = CareerPredictor()
