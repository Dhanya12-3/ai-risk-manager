from pathlib import Path
import json
import joblib
import pandas as pd

MODEL_PATH = Path("models/fraudshield_pipeline.joblib")
META_PATH = Path("models/model_metadata.json")

def predict_transaction(transaction: dict) -> dict:
    model = joblib.load(MODEL_PATH)
    meta = json.loads(META_PATH.read_text())
    df = pd.DataFrame([transaction])
    probability = float(model.predict_proba(df)[:, 1][0])
    score = round(probability * 100)
    if score < 30:
        level, decision = "LOW", "APPROVE"
    elif score < 60:
        level, decision = "MEDIUM", "MONITOR"
    elif score < 80:
        level, decision = "HIGH", "VERIFY"
    elif score < 90:
        level, decision = "HIGH", "HOLD"
    else:
        level, decision = "CRITICAL", "BLOCK"
    return {
        "risk_probability": probability,
        "risk_score": score,
        "risk_level": level,
        "decision": decision,
        "threshold": meta["selected_threshold"],
    }
