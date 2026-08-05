import os
import joblib
import pandas as pd

MODEL_PATH = "models/iforest.joblib"
MODEL_ABS_PATH = os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), MODEL_PATH)

class AIAnomalyDetector:
    def __init__(self):
        self.model = None
        self.enabled = False
        self._load_model()

    def _load_model(self):
        if os.path.exists(MODEL_ABS_PATH):
            try:
                self.model = joblib.load(MODEL_ABS_PATH)
                self.enabled = True
                print("[AI] Isolation Forest model loaded successfully.")
            except Exception as e:
                print(f"[AI] Failed to load model: {e}")
        else:
            print("[AI] No AI model found. Run 'python train_ai.py' to enable AI detection.")

    def analyze(self, flow):
        if not self.enabled or self.model is None:
            return None
            
        duration = flow.duration()
        packets = flow.packet_count
        bytes_ = flow.byte_count
        
        # Build pandas DataFrame for prediction features
        X_test = pd.DataFrame({
            "duration": [duration],
            "packet_count": [packets],
            "byte_count": [bytes_]
        })
        
        # Obtain prediction (-1 means anomaly, +1 means normal)
        prediction = self.model.predict(X_test)[0]
        
        # Calculate positive anomaly score where higher means more anomalous
        # decision_function goes from negative (anomaly) to positive (normal)
        score_val = self.model.decision_function(X_test)[0]
        anomaly_score = float(-score_val)
        
        # Deliverable: Alert when score crosses threshold
        # Our model sets prediction == -1 natively depending on its contamination threshold
        # Let's use the prediction == -1 as the main alert trigger, which implies anomaly_score > internal_threshold.
        if prediction == -1:
            severity = "high" if anomaly_score > 0.05 else "medium"
            return {
                "type": "AI Anomaly",
                "severity": severity,
                "reason": f"AI detected anomalous flow behavior (Anomaly Score: {anomaly_score:.3f})"
            }

        return None
