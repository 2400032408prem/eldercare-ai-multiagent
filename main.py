"""
ElderCare AI - Multi-Agent System
Powered by Google Gemini API (FREE tier)

Run: python main.py
Setup: pip install -r requirements.txt
       Add GEMINI_API_KEY to .env file
Get free API key: https://ai.google.dev
"""
import json
from rich.console import Console
from rich.panel import Panel
from rich.table import Table
from rich import box

from agents.health_agent import HealthWellnessAgent
from agents.safety_agent import SafetyEmergencyAgent
from agents.coordination_agent import CareCoordinationAgent
from agents.supervisor_agent import SupervisorAgent
from data.mock_data import PATIENT, generate_vitals, generate_movement_data
from memory.patient_state import shared_state

console = Console()


def print_banner():
    console.print(Panel.fit(
        "[bold cyan]ElderCare AI[/bold cyan] [white]Multi-Agent Autonomous Care Platform[/white]\n"
        "[dim]Powered by Google Gemini API (FREE) | Japan Elder Care System[/dim]",
        border_style="cyan"
    ))


def print_section(title: str):
    console.print(f"\n[bold yellow]{'='*60}[/bold yellow]")
    console.print(f"[bold yellow]  {title}[/bold yellow]")
    console.print(f"[bold yellow]{'='*60}[/bold yellow]")


def print_report(report: dict, title: str):
    console.print(f"\n[bold green]{title}[/bold green]")
    for k, v in report.items():
        if k == "agent":
            continue
        if isinstance(v, list):
            console.print(f"  [cyan]{k}:[/cyan]")
            for item in v:
                console.print(f"    - {item}")
        elif isinstance(v, dict):
            console.print(f"  [cyan]{k}:[/cyan] {json.dumps(v, default=str)[:120]}")
        else:
            console.print(f"  [cyan]{k}:[/cyan] {v}")


def run_scenario(scenario_name: str, vitals_scenario: str, movement_scenario: str):
    console.print(f"\n[bold magenta]SCENARIO: {scenario_name}[/bold magenta]")

    # Generate data
    vitals   = generate_vitals(vitals_scenario)
    movement = generate_movement_data(movement_scenario)
    scenario_data = {
        "vitals":      vitals,
        "medications": PATIENT["medications"],
        "movement":    movement,
    }

    # ─── Agent 1: Health & Wellness ────────────────────────────
    print_section("Agent 1: Health & Wellness")
    health_agent  = HealthWellnessAgent()
    health_report = health_agent.run(scenario_data)
    print_report(health_report, "Health Assessment:")

    # ─── Agent 2: Safety & Emergency ───────────────────────────
    print_section("Agent 2: Safety & Emergency")
    safety_agent  = SafetyEmergencyAgent()
    safety_report = safety_agent.run(scenario_data)
    print_report(safety_report, "Safety Assessment:")

    # ─── Agent 3: Care Coordination ────────────────────────────
    print_section("Agent 3: Care Coordination")
    coord_agent  = CareCoordinationAgent()
    coord_report = coord_agent.run(scenario_data)
    print_report(coord_report, "Coordination Output:")

    # ─── Supervisor: AI Care Manager ───────────────────────────
    print_section("Supervisor: AI Care Manager")
    supervisor        = SupervisorAgent()
    supervisor_report = supervisor.run({
        "health":      health_report,
        "safety":      safety_report,
        "coordination":coord_report,
    })
    print_report(supervisor_report, "Final Decision:")

    # ─── Final State Summary ──────────────────────────────────
    console.print(f"\n[bold white on blue]  PATIENT STATE SUMMARY  [/bold white on blue]")
    console.print(f"[white]{shared_state.get_summary()}[/white]")
    if supervisor_report.get("daily_summary"):
        console.print(f"\n[italic]{supervisor_report['daily_summary']}[/italic]")

    return {
        "health":      health_report,
        "safety":      safety_report,
        "coordination":coord_report,
        "supervisor":  supervisor_report,
    }


if __name__ == "__main__":
    print_banner()
    console.print(f"\n[cyan]Patient: {PATIENT['name']}, Age {PATIENT['age']}[/cyan]")
    console.print(f"[dim]Conditions: {', '.join(PATIENT['conditions'])}[/dim]")

    # Run the elevated risk scenario (hackathon demo scenario)
    results = run_scenario(
        scenario_name="Elevated BP + High Fall Risk",
        vitals_scenario="elevated",
        movement_scenario="risky",
    )

    console.print("\n[bold green]ElderCare AI pipeline complete![/bold green]")
    console.print("[dim]Run: streamlit run dashboard/app.py  to open the visual dashboard[/dim]\n")
