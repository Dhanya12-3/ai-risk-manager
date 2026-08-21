import pandas as pd


def detect_fraud_spikes(
    csv_path="data/raw/transactions.csv",
    window_size=500,
    spike_multiplier=2.5
):
    """
    Detect unusually high fraud rates in recent transactions.

    This is a defensive fraud-monitoring component.
    It does not generate attack instructions or offensive behavior.
    """

    df = pd.read_csv(csv_path)

    # Make sure timestamp exists
    if "timestamp" in df.columns:
        df["timestamp"] = pd.to_datetime(
            df["timestamp"],
            errors="coerce"
        )

        df = df.sort_values("timestamp")

    results = []

    # Check required columns
    required_columns = {
        "merchant_category",
        "label"
    }

    missing = required_columns - set(df.columns)

    if missing:
        raise ValueError(
            f"Missing required columns: {list(missing)}"
        )

    # Analyze each merchant category
    for category in df["merchant_category"].dropna().unique():

        category_df = df[
            df["merchant_category"] == category
        ].copy()

        # Need enough historical data
        if len(category_df) < window_size * 2:
            continue

        # Historical transactions
        baseline = category_df.iloc[:-window_size]

        # Most recent transactions
        current = category_df.iloc[-window_size:]

        baseline_rate = float(
            baseline["label"].mean()
        )

        current_rate = float(
            current["label"].mean()
        )

        # Avoid division by zero
        if baseline_rate <= 0:
            continue

        multiplier = (
            current_rate / baseline_rate
        )

        increase_percentage = (
            (current_rate - baseline_rate)
            / baseline_rate
        ) * 100

        # Only report meaningful spikes
        if multiplier >= spike_multiplier:

            if multiplier >= 5:
                severity = "CRITICAL"

            elif multiplier >= 3:
                severity = "HIGH"

            else:
                severity = "MEDIUM"

            results.append({

                "merchant_category": str(category),

                "baseline_fraud_rate": round(
                    baseline_rate * 100,
                    2
                ),

                "current_fraud_rate": round(
                    current_rate * 100,
                    2
                ),

                "increase_percentage": round(
                    increase_percentage,
                    2
                ),

                "spike_multiplier": round(
                    multiplier,
                    2
                ),

                "severity": severity,

                "affected_transactions": int(
                    len(current)
                ),

                "recommended_action": (
                    "Increase verification for high-risk "
                    "transactions and investigate the affected "
                    "merchant category."
                )
            })

    # Highest spike first
    results.sort(
        key=lambda x: x["spike_multiplier"],
        reverse=True
    )

    return results