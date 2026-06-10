from agents.base_agent import BaseAgent
from tools.vitals_tools import (
    check_vitals_against_thresholds,
    compute_health_risk_score,
    calculate_vitals_deviation,
)
from tools.medication_tools import compute_medication_score, get_medication_report
from data.mock_data import PATIENT


HEALTH_PROMPT = """
You are the Health & Wellness Agent in an AI-powered elder care system for Japan.
Your responsibilities:
1. Analyze patient vital signs vs personal baseline and clinical thresholds.
2. Evaluate medication adherence; flag every missed dose.
3. Predict health deterioration risk using deviation patterns.
4. Generate concise clinical summaries for caregivers AND simple reassuring/urgent messages for family.

Always respond in valid JSON only, no markdown. Keys required:
- health_risk: "low" | "medium" | "high" | "critical"
- risk_score: float 0.0-1.0
- summary: string (2-3 clinical sentences for caregivers)
- family_message: string (plain, empathetic, 1-2 sentences for family)
- recommended_actions: list of strings
- alerts: list of strings (metric names that are out of range)
"""


class HealthWellnessAgent(BaseAgent):

    def __init__(self):
        super().__init__("Health & Wellness Agent", HEALTH_PROMPT)

    def run(self, scenario_data: dict) -> dict:
        self.log("info", "Starting health & vitals analysis...")

        vitals      = scenario_data["vitals"]
        medications = scenario_data["medications"]
        baseline    = PATIENT["baseline"]

        # Tool 1: Threshold checks
        threshold_alerts = check_vitals_against_thresholds(vitals)

        # Tool 2: Baseline deviation
        deviations = calculate_vitals_deviation(vitals, baseline)

        # Tool 3: Weighted health risk score
        risk_score, risk_label = compute_health_risk_score(vitals, baseline)

        # Tool 4: Medication adherence
        med_score, missed_meds = compute_medication_score(medications)
        med_report = get_medication_report(medications)

        # Gemini reasoning
        context = {
            "patient":          PATIENT["name"],
            "age":              PATIENT["age"],
            "conditions":       PATIENT["conditions"],
            "current_vitals":   vitals,
            "baseline":         baseline,
            "deviations_pct":   deviations,
            "threshold_alerts": threshold_alerts,
            "risk_score":       risk_score,
            "risk_label":       risk_label,
            "medication_report":med_report,
            "missed_meds":      missed_meds,
            "med_adherence":    med_score,
        }
        raw    = self.think("Analyze patient health data and return structured JSON assessment.", context)
        result = self.parse_json_response(raw)

        output = {
            "agent":            self.name,
            "health_risk":      result.get("health_risk", risk_label),
            "risk_score":       result.get("risk_score", risk_score),
            "threshold_alerts": threshold_alerts,
            "deviations":       deviations,
            "medication_score": med_score,
            "missed_meds":      missed_meds,
            "summary":          result.get("summary", med_report),
            "family_message":   result.get("family_message", ""),
            "recommended_actions": result.get("recommended_actions", []),
            "alerts":           result.get("alerts", [a["metric"] for a in threshold_alerts]),
        }

        # Update shared state
        self.state.health_risk      = output["health_risk"]
        self.state.vitals_summary   = vitals
        self.state.medication_score = med_score
        self.state.missed_meds      = missed_meds

        level = "alert" if risk_label in ("high", "critical") else "info"
        self.log(level, f"Health risk: {output['health_risk'].upper()} | Med adherence: {med_score:.0%} | Missed: {len(missed_meds)} dose(s)")
        return output
