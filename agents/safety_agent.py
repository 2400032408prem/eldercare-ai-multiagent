from agents.base_agent import BaseAgent
from tools.fall_tools import compute_fall_risk, detect_emergency
from data.mock_data import PATIENT


SAFETY_PROMPT = """
You are the Safety & Emergency Agent in an AI-powered elder care system.
You specialise in PREDICTIVE ELDER SAFETY - predicting falls before they happen.
Your responsibilities:
1. Analyze gait, balance, and movement patterns to compute fall risk.
2. Detect active emergencies (falls, immobility events).
3. Predict increased fall risk 24-48 hours in advance.
4. Generate real-time alerts with severity levels.
5. Recommend escalation actions based on risk level.

Always respond in valid JSON only, no markdown. Keys required:
- fall_risk: "low" | "medium" | "high" | "critical"
- fall_risk_score: float 0.0-1.0
- active_emergency: boolean
- emergency_details: string or null
- risk_factors: list of strings
- prediction_window: string (e.g. "high fall risk in next 24 hours")
- escalation_actions: list of strings
- alert_level: "green" | "yellow" | "orange" | "red"
"""


class SafetyEmergencyAgent(BaseAgent):

    def __init__(self):
        super().__init__("Safety & Emergency Agent", SAFETY_PROMPT)

    def run(self, scenario_data: dict) -> dict:
        self.log("info", "Analyzing movement patterns and fall risk...")

        movement = scenario_data["movement"]

        # Tool 1: Fall risk computation
        fall_risk_score, fall_risk_label, risk_factors = compute_fall_risk(movement)

        # Tool 2: Emergency detection
        is_emergency, emergency_details = detect_emergency(movement)

        # Gemini reasoning
        context = {
            "patient":          PATIENT["name"],
            "age":              PATIENT["age"],
            "conditions":       PATIENT["conditions"],
            "movement_data":    movement,
            "fall_risk_score":  fall_risk_score,
            "fall_risk_label":  fall_risk_label,
            "risk_factors":     risk_factors,
            "active_emergency": is_emergency,
            "emergency_details":emergency_details,
            "current_health_risk": self.state.health_risk,
        }
        raw    = self.think("Analyze movement data and produce fall risk & safety assessment in JSON.", context)
        result = self.parse_json_response(raw)

        output = {
            "agent":              self.name,
            "fall_risk":          result.get("fall_risk", fall_risk_label),
            "fall_risk_score":    result.get("fall_risk_score", fall_risk_score),
            "active_emergency":   result.get("active_emergency", is_emergency),
            "emergency_details":  result.get("emergency_details", emergency_details),
            "risk_factors":       result.get("risk_factors", risk_factors),
            "prediction_window":  result.get("prediction_window", ""),
            "escalation_actions": result.get("escalation_actions", []),
            "alert_level":        result.get("alert_level", "yellow"),
        }

        # Update shared state
        self.state.fall_risk        = output["fall_risk"]
        self.state.fall_risk_score  = fall_risk_score
        self.state.active_emergency = output["active_emergency"]
        if output["active_emergency"]:
            self.state.emergency_details = output["emergency_details"]

        level = "critical" if is_emergency else ("alert" if fall_risk_label in ("high", "critical") else "info")
        self.log(level, f"Fall risk: {output['fall_risk'].upper()} ({fall_risk_score:.0%}) | Emergency: {'YES!' if is_emergency else 'No'}")
        return output
