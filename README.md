# ElderCare AI - Multi-Agent Autonomous Care Platform

> **Hackathon Project | Japan Aging Society | Powered by Google Gemini API (FREE)**

A production-ready 4-agent AI system that monitors elderly patients, predicts health risks, coordinates caregivers, and keeps families informed — autonomously.

---

## Architecture

```
ElderCare AI
├── Agent 1: Health & Wellness Agent     → Vitals + Medication monitoring
├── Agent 2: Safety & Emergency Agent     → Predictive Elder Safety (fall prediction)
├── Agent 3: Care Coordination Agent      → Smart caregiver matching + family updates
└── Supervisor: AI Care Manager           → Orchestrator brain - fuses all signals
```

## NO OpenAI Required - Uses FREE Gemini API

Get your free API key at: https://ai.google.dev
- Free tier: 15 requests/minute, 1 million tokens/day
- No credit card needed

---

## Setup & Run

```bash
# 1. Clone
git clone https://github.com/2400032408prem/eldercare-ai-multiagent.git
cd eldercare-ai-multiagent

# 2. Install dependencies
pip install -r requirements.txt

# 3. Add your Gemini API key
echo "GEMINI_API_KEY=your-key-here" > .env

# 4. Run CLI version
python main.py

# 5. OR run Streamlit dashboard
streamlit run dashboard/app.py
```

---

## Project Structure

```
eldercare-ai-multiagent/
├── main.py                     # CLI entry point
├── config.py                   # Gemini API config + thresholds
├── requirements.txt
├── agents/
│   ├── base_agent.py           # BaseAgent class (Gemini-powered)
│   ├── health_agent.py         # Agent 1: Health & Wellness
│   ├── safety_agent.py         # Agent 2: Safety & Emergency
│   ├── coordination_agent.py   # Agent 3: Care Coordination
│   └── supervisor_agent.py     # Supervisor: AI Care Manager
├── tools/
│   ├── vitals_tools.py         # BP/HR/SpO2 anomaly detection
│   ├── medication_tools.py     # Medication adherence tracking
│   ├── fall_tools.py           # Predictive Elder Safety
│   └── schedule_tools.py       # Smart caregiver matching
├── data/
│   └── mock_data.py            # Simulated patient/caregiver data
├── memory/
│   └── patient_state.py        # Shared state (Pydantic)
└── dashboard/
    └── app.py                  # Streamlit visual dashboard
```

---

## Demo Scenarios

| Scenario | Vitals | Movement | Expected Output |
|---|---|---|---|
| `normal` | Normal range | Stable gait | Green / Routine |
| `elevated` | High BP + low steps | Reduced gait | Orange / Urgent |
| `critical` | Dangerous BP + low SpO2 | Fall detected | Red / Emergency |

---

## Key AI Features

- **Predictive Elder Safety**: Predicts fall risk 24-48h before it happens using gait, balance, and nighttime wandering patterns
- **Smart Caregiver Matching**: Scores caregivers by distance, skills, language, availability
- **Gemini Reasoning**: Each agent sends structured context to Gemini and returns JSON decisions
- **Shared State**: All agents share a Pydantic `PatientState` object for real-time coordination
- **Streamlit Dashboard**: Visual 4-tab dashboard with metrics, alerts, and family messages

---

## Hackathon Pitch

> ElderCare AI addresses Japan's caregiver shortage by autonomously monitoring elderly patients, predicting health crises before they happen, and coordinating the right care at the right time — while keeping families informed.
