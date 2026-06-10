from agents.base_agent import BaseAgent
from data.mock_data import PATIENT


SUPERVISOR_PROMPT = """
You are the AI Care Manager - the Supervisor/Orchestrator in an elder care multi-agent system.
You receive aggregated reports from 3 specialist agents and make final, holistic care decisions.

Your responsibilities:
1. Fuse all incoming signals: health risk + fall risk + emergency status + care coordination.
2. Prioritize emergencies above all else.
3. Determine the overall patient risk level and urgency.
4. Generate a unified daily summary for the family dashboard.
5. Issue final recommended actions with priorities.
6. Explain your reasoning step-by-step.

Always respond in valid JSON only, no markdown. Keys required:
- overall_risk: "low" | "medium" | "high" | "critical"
- priority: "routine" | "urgent" | "emergency"
- reasoning: string (3-5 sentences explaining the decision)
- daily_summary: string (2-3 sentences for family dashboard)
- final_actions: list of dicts with keys: action, priority (1=highest), assigned_to
- dashboard_alert: string (one-line status for dashboard header)
- care_quality_score: float 0.0-10.0 (overall care status score)
"""


class SupervisorAgent(BaseAgent):

    def __init__(self):
        super().__init__("AI Care Manager (Supervisor)", SUPERVISOR_PROMPT)

    def run(self, agent_reports: dict) -> dict:
        self.log("info", "AI Care Manager synthesizing all agent reports...")

        health_report = agent_reports.get("health", {})
        safety_report = agent_reports.get("safety", {})
        coord_report  = agent_reports.get("coordination", {})

        # Determine priority from shared state
        state          = self.state
        is_emergency   = state.active_emergency
        health_risk    = state.health_risk
        fall_risk      = state.fall_risk
        med_score      = state.medication_score
        visit_ok       = state.scheduled_visit is not None

        # Fast-path for emergencies (no need to wait for LLM)
        if is_emergency:
            auto_priority = "emergency"
            auto_risk     = "critical"
        elif health_risk in ("high", "critical") or fall_risk in ("high", "critical"):
            auto_priority = "urgent"
            auto_risk     = "high"
        else:
            auto_priority = "routine"
            auto_risk     = health_risk

        # Gemini deep reasoning
        context = {
            "patient":          PATIENT["name"],
            "age":              PATIENT["age"],
            "conditions":       PATIENT["conditions"],
            "health_report":    health_report,
            "safety_report":    safety_report,
            "coordination_report": coord_report,
            "shared_state": {
                "health_risk":      health_risk,
                "fall_risk":        fall_risk,
                "fall_risk_score":  state.fall_risk_score,
                "medication_score": med_score,
                "missed_meds":      state.missed_meds,
                "active_emergency": is_emergency,
                "visit_scheduled":  visit_ok,
                "caregiver":        state.assigned_caregiver,
            },
        }
        raw    = self.think("Synthesize all reports and produce final orchestration decision in JSON.", context)
        result = self.parse_json_response(raw)

        output = {
            "agent":              self.name,
            "overall_risk":       result.get("overall_risk",    auto_risk),
            "priority":           result.get("priority",         auto_priority),
            "reasoning":          result.get("reasoning",        "See individual agent reports."),
            "daily_summary":      result.get("daily_summary",    ""),
            "final_actions":      result.get("final_actions",    []),
            "dashboard_alert":    result.get("dashboard_alert",  f"Risk: {auto_risk.upper()}"),
            "care_quality_score": result.get("care_quality_score", 5.0),
            "event_count":        len(state.events),
        }

        level = "critical" if auto_priority == "emergency" else ("alert" if auto_priority == "urgent" else "success")
        self.log(level, f"FINAL: {output['overall_risk'].upper()} | Priority: {output['priority'].upper()} | Score: {output['care_quality_score']}/10")
        return output
