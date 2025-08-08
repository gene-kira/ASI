# ml_detector.py

import time
import random

def run_ml_scan():
    time.sleep(1)
    score = random.uniform(0, 1)
    print(f"🧠 ML anomaly score: {score:.3f}")
    if score > 0.8:
        print("⚠️ High anomaly detected! Triggering purge daemon.")

