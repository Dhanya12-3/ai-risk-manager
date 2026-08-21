from pathlib import Path
import numpy as np
import pandas as pd

RNG = np.random.default_rng(42)
N = 30000

def sigmoid(x):
    return 1.0 / (1.0 + np.exp(-np.clip(x, -30, 30)))

def main():
    out = Path("data/raw")
    out.mkdir(parents=True, exist_ok=True)

    timestamps = pd.date_range("2025-01-01", periods=N, freq="15min")
    customers = RNG.integers(1, 5001, N)
    merchants = RNG.integers(1, 501, N)

    amount = np.round(np.exp(RNG.normal(np.log(1800), 1.0, N)), 2)
    account_age = RNG.integers(5, 2500, N)
    is_new_device = RNG.binomial(1, 0.08, N)
    ip_risk = np.round(RNG.beta(1.5, 7, N), 4)
    distance = np.round(RNG.exponential(8, N), 2)
    failed = RNG.poisson(0.35, N)
    tx_1h = RNG.poisson(1.2, N)
    tx_24h = tx_1h + RNG.poisson(5, N)
    avg_amount = np.round(np.exp(RNG.normal(np.log(1700), 0.65, N)), 2)
    amount_deviation = np.round(amount / np.maximum(avg_amount, 1), 3)
    chargebacks = RNG.poisson(0.12, N)
    previous_flags = RNG.poisson(0.18, N)
    merchant_risk = np.round(RNG.beta(1.7, 6, N), 4)
    velocity = np.round(tx_1h / np.maximum(tx_24h, 1), 4)

    payment_methods = RNG.choice(["UPI", "CARD", "NETBANKING", "WALLET"], N, p=[0.55, .28, .10, .07])
    categories = RNG.choice(
        ["Electronics", "Fashion", "Grocery", "Travel", "Gaming", "Healthcare"],
        N, p=[.20, .18, .25, .12, .12, .13]
    )
    locations = RNG.choice(["Bengaluru", "Mumbai", "Delhi", "Hyderabad", "Chennai", "Pune"], N)
    hours = timestamps.hour.to_numpy()
    unusual_hour = ((hours < 5) | (hours >= 23)).astype(int)

    logit = (
        -6.6
        + 1.35 * np.log1p(amount_deviation)
        + 1.25 * is_new_device
        + 3.0 * ip_risk
        + 0.025 * distance
        + 0.18 * failed
        + 0.18 * tx_1h
        + 0.55 * velocity
        + 0.22 * chargebacks
        + 0.30 * previous_flags
        + 1.8 * merchant_risk
        + 0.75 * unusual_hour
        + 0.00012 * amount
    )
    fraud_probability = sigmoid(logit)
    label = RNG.binomial(1, fraud_probability)

    df = pd.DataFrame({
        "transaction_id": [f"TXN-{i:07d}" for i in range(1, N + 1)],
        "customer_id": customers,
        "merchant_id": merchants,
        "amount": amount,
        "timestamp": timestamps,
        "payment_method": payment_methods,
        "merchant_category": categories,
        "customer_account_age_days": account_age,
        "is_new_device": is_new_device,
        "ip_risk_score": ip_risk,
        "location": locations,
        "distance_from_usual_location": distance,
        "failed_attempts_last_24h": failed,
        "transactions_last_1h": tx_1h,
        "transactions_last_24h": tx_24h,
        "avg_transaction_amount": avg_amount,
        "transaction_amount_deviation": amount_deviation,
        "previous_chargebacks": chargebacks,
        "previous_fraud_flags": previous_flags,
        "merchant_risk_score": merchant_risk,
        "account_velocity": velocity,
        "hour_of_day": hours,
        "day_of_week": timestamps.dayofweek.to_numpy(),
        "label": label,
    })
    df.to_csv(out / "transactions.csv", index=False)

    print(f"Generated {len(df):,} synthetic transactions.")
    print(f"Fraud rate: {df.label.mean():.2%}")
    print(f"Saved to {out / 'transactions.csv'}")

if __name__ == "__main__":
    main()
