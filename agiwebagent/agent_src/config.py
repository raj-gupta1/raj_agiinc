# agiwebagent/agent_src/config.py
from dataclasses import dataclass

@dataclass
class AgentConfig:
    model_name: str = "gpt-4o-mini"
    parser_model_name: str = "gpt-4o-mini"
    max_steps: int = 25
    max_retries: int = 3
    use_screenshot: bool = True
    use_axtree: bool = True