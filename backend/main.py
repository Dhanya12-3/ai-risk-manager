from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware

from backend.schemas import TransactionRequest
from backend.risk_engine import calculate_risk
from backend.fraud_spike import detect_fraud_spikes
from backend.decision_engine import calculate_final_risk

import json
from pathlib import Path


app = FastAPI(
    title="AI Risk Manager",
    version="1.0"
)


app.add_middleware(
    CORSMiddleware,
    allow_origins=[
        "http://localhost:5173",
        "http://127.0.0.1:5173",
        "http://localhost:5500",
        "http://127.0.0.1:5500",
        "http://localhost:3000",
        "http://127.0.0.1:3000"
    ],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


@app.get("/")
def root():
    return {
        "name": "AI Risk Manager",
        "version": "1.0",
        "status": "running",
        "purpose": "Defensive payment fraud detection"
    }


@app.get("/health")
def health():
    return {
        "status": "healthy"
    }


@app.post("/transactions/analyze")
def analyze_transaction(transaction: TransactionRequest):

    try:
        transaction_data = transaction.model_dump()

        result = calculate_risk(transaction_data)

        return {
            "success": True,
            "transaction": transaction_data,
            "risk": result
        }

    except FileNotFoundError as e:
        raise HTTPException(
            status_code=500,
            detail=str(e)
        )

    except Exception as e:
        raise HTTPException(
            status_code=500,
            detail=f"Risk analysis failed: {str(e)}"
        )


@app.get("/fraud-spikes")
def fraud_spikes():

    try:
        spikes = detect_fraud_spikes()

        return {
            "success": True,
            "spikes_detected": len(spikes),
            "alerts": spikes
        }

    except Exception as e:
        raise HTTPException(
            status_code=500,
            detail=f"Fraud spike detection failed: {str(e)}"
        )


@app.post("/transactions/risk-decision")
def risk_decision(transaction: TransactionRequest):

    try:
        transaction_data = transaction.model_dump()

        ml_result = calculate_risk(transaction_data)

        final_result = calculate_final_risk(
            ml_probability=ml_result["risk_probability"],
            transaction=transaction_data,
            fraud_spike=False,
            spike_multiplier=1.0
        )

        return {
            "success": True,
            "risk_decision": final_result
        }

    except Exception as e:
        raise HTTPException(
            status_code=500,
            detail=f"Risk decision failed: {str(e)}"
        )


@app.get("/model/metrics")
def model_metrics():

    try:
        path = Path("models/model_metadata.json")

        with open(path, "r") as f:
            metadata = json.load(f)

        return {
            "model": metadata.get(
                "model",
                "Logistic Regression"
            ),
            "threshold": metadata.get(
                "threshold",
                0.35
            ),
            "precision": metadata.get(
                "precision",
                0
            ),
            "recall": metadata.get(
                "recall",
                0
            ),
            "f1": metadata.get(
                "f1",
                0
            ),
            "evaluation": "Held-out validation/test set"
        }

    except Exception as e:
        return {
            "error": str(e)
        }