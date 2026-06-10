from agents.base_agent import BaseAgent
from tools.schedule_tools import find_best_caregiver, build_care_plan
from data.mock_data import PATIENT


COORD_PROMPT = """
You are the Care Coordination Agent in an AI-powered elder care system for Japan.
Your responsibilities:
1. Coordinate caregivers: find the best-matched caregiver based on skills, location, language, availability.
2. Build and schedule care visits based on health and safety signals.
3. Generate family update messages (clear, empathetic, actionable).
4. Manage the daily care plan: meals, medications, exercise, check-ins.
5. Track and confirm upcoming visits.

Always respond in valid JSON only, no markdown. Keys required:
- coordination_status: "scheduled" | "escalated" | "monitoring"
- visit_scheduled: boolean
- caregiver_assigned: dict or null
- care_plan: dict or null
- family_update: string (plain language, 2-3 sentences)
- next_steps: list of strings
"""


class CareCoordinationAgent(BaseAgent):

    def __init__(self):
        super().__init__("Care Coordination Agent", COORD_PROMPT)

    def run(self, scenario_data: dict) -> dict:
        self.log("info", "Coordinating care and matching caregivers...")

        health_risk = self.state.health_risk
        fall_risk   = self.state.fall_risk
        emergency   = self.state.active_emergency

        # Determine required skills based on current risk levels
        required_skills = ["nursing"]
        if fall_risk in ("high", "critical") or emergency:
            required_skills.append("fall-prevention")
        if health_risk in ("high", "critical"):
            required_skills.append("medication-management")
        if "type-2 diabetes" in PATIENT.get("conditions", []):
            required_skills.append("diabetes-care")

        # Tool 1: Find best caregiver
        preferred_time = "13:00" if emergency else "15:00"
        caregiver = find_best_caregiver(
            required_skills=required_skills,
            preferred_language="Japanese",
            preferred_time=preferred_time,
        )

        # Tool 2: Build care plan
        care_plan = None
        if caregiver:
            purpose = "Emergency Response" if emergency else f"Routine Visit - {health_risk.title()} Health Risk"
            care_plan = build_care_plan(purpose, caregiver, preferred_time)

        # Gemini reasoning
        context = {
            "patient":          PATIENT["name"],
            "age":              PATIENT["age"],
            "health_risk":      health_risk,
            "fall_risk":        fall_risk,
            "active_emergency": emergency,
            "required_skills":  required_skills,
            "best_caregiver":   caregiver,
            "care_plan":        care_plan,
            "missed_meds":      self.state.missed_meds,
            "emergency_contacts": PATIENT["emergency_contacts"],
        }
        raw    = self.think("Generate care coordination output including family update and next steps in JSON.", context)
        result = self.parse_json_response(raw)

        output = {
            "agent":               self.name,
            "coordination_status": result.get("coordination_status", "scheduled" if caregiver else "monitoring"),
            "visit_scheduled":     caregiver is not None,
            "caregiver_assigned":  caregiver,
            "care_plan":           care_plan,
            "family_update":       result.get("family_update", ""),
            "next_steps":          result.get("next_steps", []),
            "required_skills":     required_skills,
        }

        # Update shared state
        self.state.scheduled_visit    = care_plan
        self.state.assigned_caregiver = caregiver
        self.state.family_notified    = True

        cg_name = caregiver["name"] if caregiver else "None available"
        self.log("success", f"Visit scheduled: {output['visit_scheduled']} | Caregiver: {cg_name}")
        return output
