from pathlib import Path
import csv


def detect_fraud_spikes():

    path = Path("data/transactions.csv")

    if not path.exists():
        return []

    with open(path, "r", newline="") as f:
        rows = list(csv.DictReader(f))

    if not rows:
        return []

    suspicious = 0

    for row in rows:
        try:
            ip_risk = float(row.get("ip_risk_score", 0))
            failed = int(row.get("failed_attempts_last_24h", 0))

            if ip_risk >= 0.7 or failed >= 3:
                suspicious += 1

        except (ValueError, TypeError):
            continue

    if suspicious >= 5:

        return [
            {
                "severity": "HIGH",
                "message": (
                    f"Fraud spike detected: {suspicious} "
                    "suspicious transactions found."
                ),
                "suspicious_transactions": suspicious,
                "action": "Review affected transactions immediately"
            }
        ]

    return []