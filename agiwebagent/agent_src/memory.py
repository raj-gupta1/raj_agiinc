# agiwebagent/agent_src/memory.py

class AgentMemory:
    def __init__(self):
        self.steps = []

    def add_step(self, step_number: int, thought: str, action: str, error: str = None):
        self.steps.append({
            'step_number': step_number,
            'thought': thought,
            'action': action,
            'error': error
        })

    def get_step_count(self) -> int:
        return len(self.steps)

    def get_formatted_history(self) -> str:
        if not self.steps:
            return "No actions taken yet."

        history = []
        for step in self.steps[-3:]:  # Last 3 steps
            entry = f"Step {step['step_number']}: {step['action']}"
            if step['error']:
                entry += f" ❌ Error: {step['error']}"
            history.append(entry)

        return "\n".join(history)

    def clear(self):
        self.steps = []

    def get_last_thought(self) -> str:
        """Returns the 'thought' (model response) of the very last step."""
        if not self.steps:
            return "No thought recorded."
        return self.steps[-1].get('thought', 'Thought not recorded for last step.')

    def get_last_action(self) -> str:
        """Returns the 'action' string of the very last step."""
        if not self.steps:
            return "No action recorded."
        return self.steps[-1].get('action', 'Action not recorded for last step.')




