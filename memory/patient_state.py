from datetime import datetime
from typing import Optional
from pydantic import BaseModel, Field


class PatientState(BaseModel):
    patient_id:         str = "P001"
    last_updated:       str = Field(default_factory=lambda: datetime.now().isoformat())

    # Health
    health_risk:        str = "low"      # low | medium | high | critical
    vitals_summary:     dict = {}
    medication_score:   float = 1.0
    missed_meds:        list = []

    # Safety
    fall_risk:          str = "low"      # low | medium | high | critical
    fall_risk_score:    float = 0.0
    active_emergency:   bool = False
    emergency_details:  Optional[str] = None

    # Care
    scheduled_visit:    Optional[dict] = None
    assigned_caregiver: Optional[dict] = None
    family_notified:    bool = False

    # Event log
    events: list = []

    def add_event(self, source: str, level: str, message: str):
        self.events.append({
            "timestamp": datetime.now().isoformat(),
            "source":    source,
            "level":     level,   # info | warning | alert | critical
            "message":   message,
        })
        self.last_updated = datetime.now().isoformat()

    def get_summary(self) -> str:
        return (
            f"Patient: {self.patient_id} | "
            f"Health Risk: {self.health_risk.upper()} | "
            f"Fall Risk: {self.fall_risk.upper()} ({self.fall_risk_score:.0%}) | "
            f"Med Score: {self.medication_score:.0%} | "
            f"Emergency: {'YES' if self.active_emergency else 'No'}"
        )


# Global singleton shared by all agents
shared_state = PatientState()
