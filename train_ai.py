import pandas as pd
import numpy as np
from sklearn.ensemble import IsolationForest
import joblib
import os

MODEL_DIR = "models"
MODEL_PATH = os.path.join(MODEL_DIR, "iforest.joblib")

def train_model():
    print("Generating synthetic normal traffic flows for training...")
    # Features: [packet_count, byte_count, duration]
    # This ensures no labeled dataset is needed, 
    # train on "normal" traffic profile.
    
    np.random.seed(42)
    n_samples = 5000
    
    # Normal traffic: Web browsing, short connections, moderate packets
    durations = np.random.uniform(0.1, 30.0, n_samples)
    packets = np.random.poisson(lam=15, size=n_samples) + 2
    bytes_ = packets * np.random.uniform(40, 1500, n_samples)
    
    # Pack into dataframe
    X_train = pd.DataFrame({
        "duration": durations,
        "packet_count": packets,
        "byte_count": bytes_
    })
    
    print("Training Isolation Forest on normal flows...")
    # contamination: expected proportion of outliers (0.01 = 1%)
    clf = IsolationForest(contamination=0.01, random_state=42, n_estimators=100)
    clf.fit(X_train)
    
    if not os.path.exists(MODEL_DIR):
        os.makedirs(MODEL_DIR)
        
    joblib.dump(clf, MODEL_PATH)
    print(f"Model saved to {MODEL_PATH}")
    print("Training complete! The AI is ready to score new flows.")

if __name__ == "__main__":
    train_model()
