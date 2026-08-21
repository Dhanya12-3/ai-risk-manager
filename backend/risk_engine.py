from pathlib import Path
import json
import joblib
import pandas as pd


MODEL_PATH = Path("models/fraudshield_pipeline.joblib")
META_PATH = Path("models/model_metadata.json")


def load_model():
    if not MODEL_PATH.exists():
        raise FileNotFoundError(
            f"Model not found at {MODEL_PATH}. "
            "Run the training script first."
        )

    return joblib.load(MODEL_PATH)


def load_metadata():
    if not META_PATH.exists():
        return {}

    return json.loads(META_PATH.read_text())


def calculate_risk(transaction: dict):

    model = load_model()
    metadata = load_metadata()

    # Convert transaction into the format expected by the ML pipeline
    df = pd.DataFrame([transaction])

    # Get fraud probability from the trained model
    probability = float(model.predict_proba(df)[0][1])

    # Convert probability to 0-100 risk score
    risk_score = round(probability * 100)

    # Risk classification
    if risk_score < 30:
        risk_level = "LOW"
        decision = "APPROVE"

    elif risk_score < 60:
        risk_level = "MEDIUM"
        decision = "MONITOR"

    elif risk_score < 80:
        risk_level = "HIGH"
        decision = "VERIFY"

    elif risk_score < 90:
        risk_level = "HIGH"
        decision = "HOLD"

    else:
        risk_level = "CRITICAL"
        decision = "BLOCK"

    # Defensive explanations based on actual transaction signals
    reasons = []

    amount = transaction.get("amount", 0)
    avg_amount = transaction.get("avg_transaction_amount", 0)

    if avg_amount > 0 and amount > avg_amount * 5:
        reasons.append(
            "Transaction amount is significantly higher than "
            "the customer's historical average"
        )

    if transaction.get("is_new_device", 0) == 1:
        reasons.append(
            "Transaction originated from a new device"
        )

    if transaction.get("ip_risk_score", 0) > 0.5:
        reasons.append(
            "IP address has elevated risk score"
        )

    if transaction.get("failed_attempts_last_24h", 0) >= 3:
        reasons.append(
            "Multiple failed attempts detected recently"
        )

    if transaction.get("transactions_last_1h", 0) >= 5:
        reasons.append(
            "Unusually high transaction velocity"
        )

    if transaction.get("distance_from_usual_location", 0) > 100:
        reasons.append(
            "Transaction location is far from the customer's usual location"
        )

    if transaction.get("previous_fraud_flags", 0) > 0:
        reasons.append(
            "Customer has previous fraud-related flags"
        )

    if transaction.get("previous_chargebacks", 0) > 0:
        reasons.append(
            "Customer has previous chargeback history"
        )

    if transaction.get("merchant_risk_score", 0) > 0.6:
        reasons.append(
            "Merchant has an elevated historical risk score"
        )

    if not reasons:
        reasons.append(
            "No major behavioral risk indicators detected"
        )

    return {
        "risk_probability": round(probability, 4),
        "risk_score": risk_score,
        "risk_level": risk_level,
        "decision": decision,
        "model_version": metadata.get(
            "model_version",
            "1.0"
        ),
        "reasons": reasons,
        "disclaimer": (
            "This is a model-generated risk estimate for "
            "defensive fraud prevention and is not a definitive "
            "fraud determination."
        )
    }