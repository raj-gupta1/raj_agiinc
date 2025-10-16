# agent_src/memory.py
from typing import List, Dict, Any


class AgentMemory:
    def __init__(self):
        self.history: List[Dict[str, Any]] = []

    def add_step(self, step_number: int, thought: str, action: str, error: str = None):
        self.history.append({"step": step_number, "thought": thought, "action": action, "error": error})

    def get_formatted_history(self) -> str:
        if not self.history:
            return "No actions taken yet."
        return "\n".join(
            f"- Step {s['step']}: Action `{s['action']}` resulted in: {'Success' if not s['error'] else f'Failure ({s['error']})'}"
            for s in self.history)

    def get_step_count(self) -> int:
        return len(self.history)

    def clear(self):
        self.history.clear()