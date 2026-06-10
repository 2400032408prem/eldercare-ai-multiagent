import random
from datetime import datetime

# ─── Patient Profile ────────────────────────────────────────────────
PATIENT = {
    "id": "P001",
    "name": "Mrs. Sato Yuki",
    "age": 78,
    "conditions": ["hypertension", "type-2 diabetes", "mild osteoporosis"],
    "medications": [
        {"name": "Amlodipine",  "dose": "5mg",   "times": ["08:00", "20:00"],          "taken": [True, False]},
        {"name": "Metformin",   "dose": "500mg",  "times": ["07:30", "13:00", "19:00"], "taken": [True, True, False]},
        {"name": "Calcium+D3",  "dose": "1000mg", "times": ["09:00"],                   "taken": [False]},
    ],
    "baseline": {
        "heart_rate":   72,
        "systolic_bp":  128,
        "diastolic_bp": 80,
        "spo2":         97,
        "daily_steps":  3200,
        "sleep_hours":  6.5,
    },
    "emergency_contacts": [
        {"name": "Sato Kenji (Son)", "phone": "+81-90-1234-5678", "relation": "son"},
        {"name": "Dr. Tanaka",       "phone": "+81-3-1234-5678",  "relation": "physician"},
    ],
}

# ─── Simulated Vitals Stream ─────────────────────────────────────────
def generate_vitals(scenario="elevated"):
    base = {
        "timestamp":     datetime.now().isoformat(),
        "heart_rate":    random.randint(68, 75),
        "systolic_bp":   random.randint(120, 130),
        "diastolic_bp":  random.randint(76, 84),
        "spo2":          random.randint(96, 99),
        "temperature":   round(random.uniform(36.4, 37.0), 1),
        "blood_glucose": random.randint(95, 115),
        "daily_steps":   random.randint(2800, 3600),
        "sleep_hours":   round(random.uniform(5.5, 7.5), 1),
    }
    if scenario == "elevated":
        base["systolic_bp"]   = random.randint(148, 162)
        base["diastolic_bp"]  = random.randint(92, 98)
        base["heart_rate"]    = random.randint(95, 105)
        base["daily_steps"]   = random.randint(1200, 1800)
        base["blood_glucose"] = random.randint(180, 220)
    elif scenario == "critical":
        base["systolic_bp"]   = random.randint(170, 185)
        base["spo2"]          = random.randint(88, 92)
        base["heart_rate"]    = random.randint(108, 118)
        base["daily_steps"]   = random.randint(400, 900)
        base["blood_glucose"] = random.randint(250, 310)
    return base

# ─── Simulated Movement/Gait Data ────────────────────────────────────
def generate_movement_data(scenario="risky"):
    base = {
        "timestamp":           datetime.now().isoformat(),
        "gait_speed_m_s":      round(random.uniform(0.9, 1.2), 2),
        "step_variability":    round(random.uniform(0.05, 0.10), 3),
        "nighttime_wandering": random.randint(0, 1),
        "balance_score":       round(random.uniform(0.75, 0.95), 2),
        "activity_level":      "normal",
        "room_transitions":    random.randint(8, 15),
        "last_fall":           None,
    }
    if scenario == "risky":
        base["gait_speed_m_s"]      = round(random.uniform(0.45, 0.65), 2)
        base["step_variability"]    = round(random.uniform(0.18, 0.30), 3)
        base["nighttime_wandering"] = random.randint(2, 5)
        base["balance_score"]       = round(random.uniform(0.40, 0.58), 2)
        base["activity_level"]      = "reduced"
        base["room_transitions"]    = random.randint(2, 4)
    elif scenario == "fall":
        base["gait_speed_m_s"]   = 0.0
        base["balance_score"]    = 0.10
        base["activity_level"]   = "none"
        base["last_fall"]        = datetime.now().isoformat()
    return base

# ─── Caregiver Database ──────────────────────────────────────────────
CAREGIVERS = [
    {"id": "C001", "name": "Tanaka Rie",      "skills": ["nursing", "fall-prevention", "wound-care"],    "languages": ["Japanese", "English"], "distance_km": 1.2, "available_slots": ["10:00", "14:00", "17:00"], "rating": 4.9},
    {"id": "C002", "name": "Yamamoto Hiroshi", "skills": ["physiotherapy", "dementia-care", "fall-prevention"], "languages": ["Japanese"],           "distance_km": 2.8, "available_slots": ["09:00", "13:00"],          "rating": 4.7},
    {"id": "C003", "name": "Kim Soo-Jin",      "skills": ["nursing", "medication-management", "diabetes-care"], "languages": ["Japanese", "Korean", "English"], "distance_km": 0.9, "available_slots": ["11:00", "15:00", "18:00"], "rating": 4.8},
    {"id": "C004", "name": "Nakamura Yuki",   "skills": ["elderly-care", "meal-prep", "companionship"],  "languages": ["Japanese"],           "distance_km": 4.5, "available_slots": ["08:00", "16:00"],          "rating": 4.5},
]
