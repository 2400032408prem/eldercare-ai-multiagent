import json
import re
import google.generativeai as genai
from config import GEMINI_API_KEY, MODEL, TEMPERATURE
from memory.patient_state import shared_state
from rich.console import Console

console = Console()
genai.configure(api_key=GEMINI_API_KEY)


class BaseAgent:
    """
    Base class for all ElderCare AI agents.
    Uses Google Gemini API (FREE tier) instead of OpenAI.
    All agents inherit from this.
    """

    def __init__(self, name: str, system_prompt: str):
        self.name          = name
        self.system_prompt = system_prompt
        self.state         = shared_state
        self.model         = genai.GenerativeModel(
            model_name=MODEL,
            generation_config=genai.GenerationConfig(
                temperature=TEMPERATURE,
                max_output_tokens=2048,
            ),
            system_instruction=system_prompt,
        )

    def think(self, user_message: str, context: dict = None) -> str:
        """Send context + message to Gemini and get a response."""
        if context:
            prompt = f"CONTEXT:\n{json.dumps(context, indent=2, default=str)}\n\nTASK:\n{user_message}"
        else:
            prompt = user_message
        try:
            response = self.model.generate_content(prompt)
            return response.text.strip()
        except Exception as e:
            self.log("warning", f"Gemini API error: {e}")
            return "{}"

    def parse_json_response(self, raw: str) -> dict:
        """Extract JSON from Gemini response (handles markdown code blocks)."""
        try:
            json_match = re.search(r'\{.*\}', raw, re.DOTALL)
            if json_match:
                return json.loads(json_match.group())
        except (json.JSONDecodeError, AttributeError):
            pass
        return {}

    def log(self, level: str, message: str):
        """Rich-colored console logging + adds event to shared state."""
        colors = {
            "info":     "cyan",
            "warning":  "yellow",
            "alert":    "bold red",
            "critical": "bold white on red",
            "success":  "bold green",
        }
        color = colors.get(level, "white")
        console.print(f"[{color}][{self.name}][/{color}] {message}")
        self.state.add_event(self.name, level, message)

    def run(self, scenario_data: dict) -> dict:
        """Override in each subclass agent."""
        raise NotImplementedError("Each agent must implement run()")
