import os
from dotenv import load_dotenv

load_dotenv()

# ─── Gemini API (Free at ai.google.dev) ────────────────────────────
GEMINI_API_KEY = os.getenv("GEMINI_API_KEY", "your-gemini-api-key-here")
MODEL = "gemini-1.5-flash"   # Free tier: 15 RPM, 1M tokens/day
TEMPERATURE = 0.3

# ─── Vitals Alert Thresholds ───────────────────────────────────────
VITALS_THRESHOLDS = {
    "heart_rate":    {"low": 50,  "high": 100},
    "systolic_bp":   {"low": 90,  "high": 140},
    "diastolic_bp":  {"low": 60,  "high": 90},
    "spo2":          {"low": 94,  "high": 100},
    "temperature":   {"low": 36.0, "high": 37.5},
    "blood_glucose": {"low": 70,  "high": 180},
}

# ─── Fall Risk Score Thresholds ────────────────────────────────────
FALL_RISK_THRESHOLDS = {
    "low":    0.3,
    "medium": 0.6,
    "high":   0.8,
}
