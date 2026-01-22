# agiwebagent/agent_src/config.py

from dataclasses import dataclass

@dataclass
class AgentConfig:
    model_name: str = "gpt-4o"
    plan_model_name: str = "gpt-4o"
    parser_model_name: str = "gpt-4o-mini"
    vision_model_name: str = "gpt-4o"
    max_steps: int = 25
    max_retries: int = 3
    use_screenshot: bool = True
    use_axtree: bool = True
    use_ocr: bool = False