from pydantic import BaseModel, Field


class TransactionRequest(BaseModel):
    amount: float = Field(gt=0)

    payment_method: str

    merchant_category: str

    customer_account_age_days: int = Field(ge=0)

    is_new_device: int = Field(ge=0, le=1)

    ip_risk_score: float = Field(ge=0, le=1)

    location: str

    distance_from_usual_location: float = Field(ge=0)

    failed_attempts_last_24h: int = Field(ge=0)

    transactions_last_1h: int = Field(ge=0)

    transactions_last_24h: int = Field(ge=0)

    avg_transaction_amount: float = Field(gt=0)

    transaction_amount_deviation: float = Field(ge=0)

    previous_chargebacks: int = Field(ge=0)

    previous_fraud_flags: int = Field(ge=0)

    merchant_risk_score: float = Field(ge=0, le=1)

    account_velocity: float = Field(ge=0)

    hour_of_day: int = Field(ge=0, le=23)

    day_of_week: int = Field(ge=0, le=6)