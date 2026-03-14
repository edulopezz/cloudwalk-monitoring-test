from fastapi import FastAPI

app = FastAPI()

def detect_anomaly(deny_rate, fail_rate, reverse_rate):

    if deny_rate > 0.20:
        return "CRITICAL_DENY"

    if fail_rate > 0.03:
        return "CRITICAL_FAIL"

    if reverse_rate > 0.03:
        return "CRITICAL_REVERSE"

    if deny_rate > 0.10:
        return "WARNING_DENY"

    if fail_rate > 0.01:
        return "WARNING_FAIL"

    if reverse_rate > 0.02:
        return "WARNING_REVERSE"

    return "NORMAL"

@app.post("/monitor")
def monitor_transaction(data: dict):

    deny_rate = data["denied"] / data["total"]
    fail_rate = data["failed"] / data["total"]
    reverse_rate = data["reversed"] / data["total"]

    alert = detect_anomaly(deny_rate, fail_rate, reverse_rate)

    return {
        "deny_rate": deny_rate,
        "fail_rate": fail_rate,
        "reverse_rate": reverse_rate,
        "alert": alert
    }
