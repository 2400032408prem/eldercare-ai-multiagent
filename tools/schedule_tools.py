from data.mock_data import CAREGIVERS


def score_caregiver(caregiver: dict, required_skills: list,
                   preferred_language: str = "Japanese",
                   max_distance_km: float = 5.0) -> float:
    """Score caregiver 0-100 based on distance, skills, language, rating."""
    score = 0.0
    dist = caregiver.get("distance_km", 99)
    if dist <= max_distance_km:
        score += max(0, 30 - (dist / max_distance_km) * 30)
    matched = sum(1 for s in required_skills if s in caregiver.get("skills", []))
    score += (matched / max(len(required_skills), 1)) * 40
    if preferred_language in caregiver.get("languages", []):
        score += 10
    score += (caregiver.get("rating", 4.0) / 5.0) * 20
    return round(score, 1)


def find_best_caregiver(required_skills: list,
                       preferred_language: str = "Japanese",
                       preferred_time: str = None) -> dict:
    """Find and return best-matched available caregiver."""
    scored = []
    for cg in CAREGIVERS:
        if preferred_time:
            slots = cg.get("available_slots", [])
            if not any(preferred_time <= slot for slot in slots):
                continue
        s = score_caregiver(cg, required_skills, preferred_language)
        scored.append((s, cg))
    if not scored:
        return None
    scored.sort(key=lambda x: x[0], reverse=True)
    best_score, best_cg = scored[0]
    return {**best_cg, "match_score": best_score}


def build_care_plan(visit_purpose: str, caregiver: dict,
                   preferred_time: str = "15:00") -> dict:
    """Build a structured care plan dict."""
    slots = caregiver.get("available_slots", [preferred_time])
    chosen_slot = preferred_time
    for s in sorted(slots):
        if s >= preferred_time:
            chosen_slot = s
            break
    return {
        "visit_purpose":   visit_purpose,
        "caregiver_id":    caregiver["id"],
        "caregiver_name":  caregiver["name"],
        "scheduled_time":  chosen_slot,
        "tasks": [
            "Blood pressure measurement",
            "Medication compliance review",
            "Gait & balance assessment",
            "Fall risk reassessment",
            "Care plan update",
        ],
        "family_notification":  True,
        "follow_up_in_hours":   24,
    }
