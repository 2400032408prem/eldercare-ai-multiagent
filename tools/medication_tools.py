def compute_medication_score(medications: list) -> tuple:
    """Returns (adherence_score 0.0-1.0, missed_med_names)."""
    total_doses  = 0
    taken_doses  = 0
    missed_names = []
    for med in medications:
        times = med.get("times", [])
        taken = med.get("taken", [])
        for i, time_slot in enumerate(times):
            total_doses += 1
            if i < len(taken) and taken[i]:
                taken_doses += 1
            else:
                missed_names.append(f"{med['name']} ({time_slot})")
    score = taken_doses / total_doses if total_doses > 0 else 1.0
    return round(score, 2), missed_names


def get_medication_report(medications: list) -> str:
    """Human-readable medication adherence report."""
    score, missed = compute_medication_score(medications)
    lines = [f"Medication Adherence Score: {score:.0%}"]
    if missed:
        lines.append(f"Missed doses ({len(missed)}):")
        for m in missed:
            lines.append(f"  - {m}")
    else:
        lines.append("All doses taken on time.")
    return "\n".join(lines)
