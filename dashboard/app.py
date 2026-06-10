"""
ElderCare AI - Streamlit Dashboard
Run: streamlit run dashboard/app.py
"""
import sys
import os
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

import streamlit as st
import json
from data.mock_data import PATIENT, generate_vitals, generate_movement_data
from agents.health_agent import HealthWellnessAgent
from agents.safety_agent import SafetyEmergencyAgent
from agents.coordination_agent import CareCoordinationAgent
from agents.supervisor_agent import SupervisorAgent
from memory.patient_state import shared_state

# ─── Page Config ────────────────────────────────────────────
st.set_page_config(
    page_title="ElderCare AI Dashboard",
    page_icon="🏥",
    layout="wide",
    initial_sidebar_state="expanded",
)

RISK_COLORS = {"low": "green", "medium": "orange", "high": "red", "critical": "darkred"}

# ─── Header ───────────────────────────────────────────────
st.title("🏥 ElderCare AI - Multi-Agent Care Platform")
st.caption("Powered by Google Gemini | Japan Aging Society | Hackathon Demo")

# ─── Sidebar ─────────────────────────────────────────────
st.sidebar.title("Control Panel")
st.sidebar.subheader(f"👤 {PATIENT['name']}")
st.sidebar.write(f"Age: {PATIENT['age']}")
st.sidebar.write(f"Conditions: {', '.join(PATIENT['conditions'])}")
st.sidebar.divider()

scenario = st.sidebar.selectbox(
    "Scenario",
    ["Elevated Risk", "Normal", "Critical Emergency"],
    index=0,
)
scenario_map = {
    "Elevated Risk":      ("elevated", "risky"),
    "Normal":             ("normal",   "normal"),
    "Critical Emergency": ("critical", "fall"),
}
vitals_s, movement_s = scenario_map[scenario]

run_button = st.sidebar.button("🚀 Run ElderCare AI", type="primary", use_container_width=True)

if not run_button:
    st.info("⬅ Select a scenario and click **Run ElderCare AI** to start the multi-agent pipeline.")
    st.stop()

# ─── Run Pipeline ──────────────────────────────────────────
with st.spinner("Running 4-agent ElderCare AI pipeline..."):
    vitals   = generate_vitals(vitals_s)
    movement = generate_movement_data(movement_s)
    data     = {"vitals": vitals, "medications": PATIENT["medications"], "movement": movement}

    health_report = HealthWellnessAgent().run(data)
    safety_report = SafetyEmergencyAgent().run(data)
    coord_report  = CareCoordinationAgent().run(data)
    sup_report    = SupervisorAgent().run({"health": health_report, "safety": safety_report, "coordination": coord_report})

st.success("✅ Pipeline complete!")

# ─── Dashboard Alert Banner ─────────────────────────────────
_risk   = sup_report.get("overall_risk", "low")
_alert  = sup_report.get("dashboard_alert", "")
_prio   = sup_report.get("priority", "routine")

if _prio == "emergency":
    st.error(f"🚨 EMERGENCY | {_alert}")
elif _prio == "urgent":
    st.warning(f"⚠️ URGENT | {_alert}")
else:
    st.success(f"✅ ROUTINE | {_alert}")

# ─── Top Metrics ───────────────────────────────────────────
c1, c2, c3, c4 = st.columns(4)
c1.metric("Health Risk",  health_report.get("health_risk","?").upper(),   delta=f"{health_report.get('risk_score',0):.0%}")
c2.metric("Fall Risk",    safety_report.get("fall_risk","?").upper(),     delta=f"{safety_report.get('fall_risk_score',0):.0%}")
c3.metric("Medication",   f"{health_report.get('medication_score',0):.0%}", delta=f"{len(health_report.get('missed_meds',[]))} missed")
c4.metric("Care Score",   f"{sup_report.get('care_quality_score',0)}/10",  delta=sup_report.get("priority","routine").upper())

st.divider()

# ─── Agent Reports ─────────────────────────────────────────
tab1, tab2, tab3, tab4 = st.tabs([
    "💚 Health & Wellness",
    "🛡️ Safety & Emergency",
    "📅 Care Coordination",
    "🧠 AI Care Manager"
])

with tab1:
    st.subheader("💚 Health & Wellness Agent")
    st.write(health_report.get("summary", ""))
    if health_report.get("missed_meds"):
        st.error("Missed Medications: " + ", ".join(health_report["missed_meds"]))
    if health_report.get("recommended_actions"):
        st.subheader("Recommended Actions")
        for a in health_report["recommended_actions"]:
            st.write(f"• {a}")
    st.subheader("Current Vitals")
    st.json(vitals)

with tab2:
    st.subheader("🛡️ Safety & Emergency Agent")
    if safety_report.get("active_emergency"):
        st.error(f"🚨 {safety_report.get('emergency_details','')}")
    st.write(f"**Prediction:** {safety_report.get('prediction_window','')}")
    if safety_report.get("risk_factors"):
        st.subheader("Risk Factors")
        for rf in safety_report["risk_factors"]:
            st.write(f"⚠️ {rf}")
    if safety_report.get("escalation_actions"):
        st.subheader("Escalation Actions")
        for ea in safety_report["escalation_actions"]:
            st.write(f"➡ {ea}")

with tab3:
    st.subheader("📅 Care Coordination Agent")
    if coord_report.get("visit_scheduled") and coord_report.get("caregiver_assigned"):
        cg = coord_report["caregiver_assigned"]
        st.success(f"✅ Visit Scheduled with {cg['name']} (Match Score: {cg.get('match_score',0)}/100)")
        cp = coord_report.get("care_plan", {})
        if cp:
            st.write(f"**Time:** {cp.get('scheduled_time','?')} | **Purpose:** {cp.get('visit_purpose','')}")
            st.write("**Tasks:**")
            for t in cp.get("tasks", []):
                st.write(f"  - {t}")
    st.subheader("Family Update")
    st.info(coord_report.get("family_update", ""))

with tab4:
    st.subheader("🧠 AI Care Manager (Supervisor)")
    st.write(f"**Reasoning:** {sup_report.get('reasoning','')}")
    st.subheader("Daily Summary (Family Dashboard)")
    st.success(sup_report.get("daily_summary", ""))
    if sup_report.get("final_actions"):
        st.subheader("Final Action Plan")
        for action in sorted(sup_report["final_actions"], key=lambda x: x.get("priority", 99) if isinstance(x, dict) else 99):
            if isinstance(action, dict):
                st.write(f"**P{action.get('priority','?')}** → {action.get('action','')} [{action.get('assigned_to','')}]")
            else:
                st.write(f"• {action}")

st.divider()
st.caption(f"ElderCare AI | {len(shared_state.events)} events logged | Google Gemini API")
