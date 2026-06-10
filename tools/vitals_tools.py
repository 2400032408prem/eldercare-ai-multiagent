from config import VITALS_THRESHOLDS


def check_vitals_against_thresholds(vitals: dict) -> list:
    """Returns list of threshold violations."""
    alerts = []
    for metric, thresholds in VITALS_THRESHOLDS.items():
        val = vitals.get(metric)
        if val is None:
            continue
        if val > thresholds["high"]:
            alerts.append({
                "metric": metric, "value": val,
                "threshold": thresholds["high"], "direction": "HIGH",
                "severity": "critical" if val > thresholds["high"] * 1.15 else "warning"
            })
        elif val < thresholds["low"]:
            alerts.append({
                "metric": metric, "value": val,
                "threshold": thresholds["low"], "direction": "LOW",
                "severity": "critical" if val < thresholds["low"] * 0.85 else "warning"
            })
    return alerts


def calculate_vitals_deviation(current: dict, baseline: dict) -> dict:
    """% deviation from personal baseline for each metric."""
    deviations = {}
    for metric in set(current.keys()) & set(baseline.keys()):
        try:
            base = float(baseline[metric])
            curr = float(current[metric])
            if base != 0:
                deviations[metric] = round((curr - base) / base * 100, 1)
        except (TypeError, ValueError):
            continue
    return deviations


def compute_health_risk_score(vitals: dict, baseline: dict) -> tuple:
    """
    Weighted health risk score 0.0-1.0.
    Weights: BP 35%, SpO2 25%, HR 20%, steps 10%, glucose 10%.
    """
    deviations = calculate_vitals_deviation(vitals, baseline)
    weights = {
        "systolic_bp":   0.35,
        "spo2":          0.25,
        "heart_rate":    0.20,
        "daily_steps":   0.10,
        "blood_glucose": 0.10,
    }
    score = 0.0
    for metric, weight in weights.items():
        dev = abs(deviations.get(metric, 0.0))
        score += min(dev / 30.0, 1.0) * weight
    score = round(min(score, 1.0), 3)
    if score < 0.3:   label = "low"
    elif score < 0.6: label = "medium"
    elif score < 0.8: label = "high"
    else:             label = "critical"
    return score, label
