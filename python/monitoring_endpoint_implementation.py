from fastapi import FastAPI
from pydantic import BaseModel, field_validator
from datetime import datetime

app = FastAPI()

# Thresholds derived from statistical analysis of transactions.csv
# deny_rate:    P95 = 10.42% → WARNING | P99 = 28.45% → CRITICAL (rounded to 20%)
# fail_rate:    P95 = 0.00% → WARNING at 1% | Max observed = 8.70% → CRITICAL at 3%
# reverse_rate: P95 = 2.33% → WARNING at 2% | P99 = 3.25% → CRITICAL at 3%

THRESHOLDS = {
    "deny": {"warning": 0.10, "critical": 0.20},
    "fail": {"warning": 0.01, "critical": 0.03},
    "reverse": {"warning": 0.02, "critical": 0.03},
}

class TransactionWindow(BaseModel):
    timestamp: datetime | None = None
    total: int
    denied: int
    failed: int
    reversed: int

    @field_validator("total")
    @classmethod
    def total_must_be_positive(cls, v):
        if v <= 0:
            raise ValueError("total must be greater than zero")
        return v


def detect_anomaly(deny_rate: float, fail_rate: float, reverse_rate: float) -> str:
    rates = {"deny": deny_rate, "fail": fail_rate, "reverse": reverse_rate}

    for metric, value in rates.items():
        if value > THRESHOLDS[metric]["critical"]:
            return f"CRITICAL_{metric.upper()}"

    for metric, value in rates.items():
        if value > THRESHOLDS[metric]["warning"]:
            return f"WARNING_{metric.upper()}"

    return "NORMAL"


@app.post("/monitor")
def monitor_transaction(data: TransactionWindow):

    deny_rate = data.denied / data.total
    fail_rate = data.failed / data.total
    reverse_rate = data.reversed / data.total

    alert = detect_anomaly(deny_rate, fail_rate, reverse_rate)

    return {
        "timestamp": data.timestamp or datetime.utcnow(),
        "deny_rate": round(deny_rate, 4),
        "fail_rate": round(fail_rate, 4),
        "reverse_rate": round(reverse_rate, 4),
        "alert": alert,
    }
