import os
from dotenv import load_dotenv

load_dotenv()

OPENAI_API_KEY = os.getenv("OPENAI_API_KEY", "your-openai-api-key-here")
MODEL = "gpt-4o"
TEMPERATURE = 0.3

VITALS_THRESHOLDS = {
    "heart_rate":    {"low": 50,  "high": 100},
    "systolic_bp":   {"low": 90,  "high": 140},
    "diastolic_bp":  {"low": 60,  "high": 90},
    "spo2":          {"low": 94,  "high": 100},
    "temperature":   {"low": 36.0,"high": 37.5},
    "blood_glucose": {"low": 70,  "high": 180},
}

FALL_RISK_THRESHOLDS = {
    "low":    0.3,
    "medium": 0.6,
    "high":   0.8,
}
