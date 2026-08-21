def calculate_final_risk(
    ml_probability: float,
    transaction: dict,
    fraud_spike: bool = False,
    spike_multiplier: float = 1.0
):
    """
    Combine ML probability and behavioral risk indicators
    into an explainable defensive risk decision.
    """

    # -----------------------------
    # 1. ML SIGNAL
    # -----------------------------

    ml_score = ml_probability * 100

    # -----------------------------
    # 2. BEHAVIORAL SIGNAL
    # -----------------------------

    behavioral_score = 0
    behavioral_reasons = []

    amount = transaction.get("amount", 0)
    avg_amount = transaction.get(
        "avg_transaction_amount",
        0
    )

    if avg_amount > 0:

        amount_ratio = amount / avg_amount

        if amount_ratio >= 10:
            behavioral_score += 20
            behavioral_reasons.append(
                "Transaction is more than 10x the customer's normal amount"
            )

        elif amount_ratio >= 5:
            behavioral_score += 12
            behavioral_reasons.append(
                "Transaction is significantly larger than normal"
            )

    # New device
    if transaction.get("is_new_device", 0) == 1:

        behavioral_score += 10

        behavioral_reasons.append(
            "New device detected"
        )

    # Failed attempts
    failed_attempts = transaction.get(
        "failed_attempts_last_24h",
        0
    )

    if failed_attempts >= 5:

        behavioral_score += 15

        behavioral_reasons.append(
            "High number of failed attempts"
        )

    elif failed_attempts >= 3:

        behavioral_score += 8

        behavioral_reasons.append(
            "Multiple failed attempts"
        )

    # Transaction velocity
    velocity = transaction.get(
        "transactions_last_1h",
        0
    )

    if velocity >= 10:

        behavioral_score += 15

        behavioral_reasons.append(
            "Very high transaction velocity"
        )

    elif velocity >= 5:

        behavioral_score += 8

        behavioral_reasons.append(
            "Elevated transaction velocity"
        )

    # Location anomaly
    distance = transaction.get(
        "distance_from_usual_location",
        0
    )

    if distance >= 500:

        behavioral_score += 15

        behavioral_reasons.append(
            "Transaction location is highly unusual"
        )

    elif distance >= 100:

        behavioral_score += 8

        behavioral_reasons.append(
            "Transaction location differs from usual location"
        )

    # Previous fraud
    if transaction.get(
        "previous_fraud_flags",
        0
    ) > 0:

        behavioral_score += 10

        behavioral_reasons.append(
            "Previous fraud-related flags exist"
        )

    # Previous chargebacks
    if transaction.get(
        "previous_chargebacks",
        0
    ) > 0:

        behavioral_score += 8

        behavioral_reasons.append(
            "Previous chargeback history exists"
        )

    # -----------------------------
    # 3. MERCHANT RISK
    # -----------------------------

    merchant_risk = (
        transaction.get(
            "merchant_risk_score",
            0
        ) * 100
    )

    merchant_score = merchant_risk * 0.15

    if merchant_risk >= 60:

        behavioral_reasons.append(
            "Merchant has elevated historical risk"
        )

    # -----------------------------
    # 4. FRAUD SPIKE
    # -----------------------------

    spike_score = 0

    if fraud_spike:

        if spike_multiplier >= 5:

            spike_score = 20

        elif spike_multiplier >= 3:

            spike_score = 15

        else:

            spike_score = 10

        behavioral_reasons.append(
            f"Fraud spike detected ({spike_multiplier:.1f}x baseline)"
        )

    # -----------------------------
    # 5. FINAL SCORE
    # -----------------------------

    final_score = (
        (ml_score * 0.60)
        + (behavioral_score * 0.25)
        + merchant_score
        + spike_score
    )

    final_score = min(
        round(final_score),
        100
    )

    # -----------------------------
    # 6. DECISION
    # -----------------------------

    if final_score < 30:

        risk_level = "LOW"
        decision = "APPROVE"

    elif final_score < 50:

        risk_level = "MEDIUM"
        decision = "MONITOR"

    elif final_score < 70:

        risk_level = "HIGH"
        decision = "VERIFY"

    elif final_score < 85:

        risk_level = "HIGH"
        decision = "HOLD"

    else:

        risk_level = "CRITICAL"
        decision = "BLOCK"

    # -----------------------------
    # 7. FALLBACK EXPLANATION
    # -----------------------------

    if not behavioral_reasons:

        behavioral_reasons.append(
            "No significant behavioral anomalies detected"
        )

    return {

        "final_risk_score": final_score,

        "risk_level": risk_level,

        "decision": decision,

        "signal_breakdown": {

            "ml_score": round(
                ml_score,
                2
            ),

            "behavioral_score": round(
                behavioral_score,
                2
            ),

            "merchant_score": round(
                merchant_score,
                2
            ),

            "fraud_spike_score": spike_score

        },

        "reasons": behavioral_reasons,

        "explanation": (
            f"Final risk score is {final_score}/100. "
            f"Decision: {decision}. "
            f"The score combines ML fraud probability, "
            f"transaction behavior, merchant risk and "
            f"fraud-spike signals."
        )
    }