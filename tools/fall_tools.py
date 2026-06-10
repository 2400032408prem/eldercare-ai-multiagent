from config import FALL_RISK_THRESHOLDS


def compute_fall_risk(movement: dict) -> tuple:
    """
    Predictive Elder Safety: compute fall risk score 0.0-1.0.
    Uses gait speed, step variability, balance, wandering, activity.
    """
    risk_score   = 0.0
    risk_factors = []

    gait = movement.get("gait_speed_m_s", 1.0)
    if gait < 0.4:
        risk_score += 0.35
        risk_factors.append(f"Very slow gait: {gait} m/s (critical)")
    elif gait < 0.6:
        risk_score += 0.20
        risk_factors.append(f"Reduced gait: {gait} m/s")

    variability = movement.get("step_variability", 0.05)
    if variability > 0.25:
        risk_score += 0.25
        risk_factors.append(f"High step variability: {variability} (unstable)")
    elif variability > 0.15:
        risk_score += 0.12
        risk_factors.append(f"Moderate step variability: {variability}")

    balance = movement.get("balance_score", 0.9)
    if balance < 0.45:
        risk_score += 0.25
        risk_factors.append(f"Poor balance: {balance:.2f}")
    elif balance < 0.65:
        risk_score += 0.12
        risk_factors.append(f"Reduced balance: {balance:.2f}")

    wandering = movement.get("nighttime_wandering", 0)
    if wandering >= 3:
        risk_score += 0.10
        risk_factors.append(f"Frequent nighttime wandering: {wandering} episodes")
    elif wandering >= 1:
        risk_score += 0.05
        risk_factors.append(f"Nighttime wandering: {wandering} episode(s)")

    if movement.get("last_fall"):
        risk_score += 0.30
        risk_factors.append("Recent fall detected!")

    if movement.get("activity_level") == "none":
        risk_score += 0.15
        risk_factors.append("Zero activity — possible immobility or fall")
    elif movement.get("activity_level") == "reduced":
        risk_score += 0.05
        risk_factors.append("Significantly reduced activity")

    risk_score = round(min(risk_score, 1.0), 3)
    if risk_score < FALL_RISK_THRESHOLDS["low"]:    label = "low"
    elif risk_score < FALL_RISK_THRESHOLDS["medium"]: label = "medium"
    elif risk_score < FALL_RISK_THRESHOLDS["high"]:  label = "high"
    else:                                            label = "critical"
    return risk_score, label, risk_factors


def detect_emergency(movement: dict) -> tuple:
    """Returns (is_emergency: bool, description: str)."""
    if movement.get("last_fall"):
        return True, f"FALL DETECTED at {movement['last_fall']}"
    if movement.get("activity_level") == "none" and movement.get("room_transitions", 10) == 0:
        return True, "No movement detected for extended period — possible collapse"
    return False, ""
