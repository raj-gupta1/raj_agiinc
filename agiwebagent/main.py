# agiwebagent/main.py

import sys
import argparse
from dotenv import load_dotenv
from agisdk import REAL
from agent_src.config import AgentConfig
from agent_src.orchestrator import TaskOrchestrator
from agent_src.utils import str2bool


class MyAgent(REAL.Agent):
    def __init__(self, config: AgentConfig):
        super().__init__()
        self.orchestrator = TaskOrchestrator(config)
        self.action_generator = None

    def get_action(self, obs: dict) -> tuple[str, dict]:
        try:
            if self.action_generator is None:
                self.action_generator = self.orchestrator.execute(obs, self.action_set)
                action = next(self.action_generator)
            else:
                action = self.action_generator.send(obs)

            return action, {}
        except StopIteration:
            return 'send_msg_to_user("Orchestrator finished.")', {}


class MyAgentArgs(REAL.AbstractAgentArgs):
    def __init__(self, config: AgentConfig, agent_name: str = "HighPerformanceAgent"):
        super().__init__(agent_name=agent_name)
        self.config = config

    def make_agent(self):
        return MyAgent(self.config)


if __name__ == "__main__":
    load_dotenv()

    parser = argparse.ArgumentParser(description="Run the modular High-Performance Agent.")

    parser.add_argument("--model", type=str, default="gpt-4o-mini", help="Model to use")
    parser.add_argument("--vision_model", type=str, default="gpt-4o", help="Vision model for OCR")
    parser.add_argument("--headless", type=str2bool, default=False, help="Run in headless mode")
    parser.add_argument("--use_screenshot", type=str2bool, default=True, help="Use screenshots")
    parser.add_argument("--use_ocr", type=str2bool, default=False, help="Use visual OCR scan on screenshots")
    parser.add_argument("--no-cache", action="store_false", dest="use_cache", help="Disable caching and force a rerun")
    parser.add_argument("--leaderboard", type=str2bool, default=False, help="Submit to leaderboard")
    parser.add_argument("--run_id", type=str, default=None, help="Run ID for leaderboard submission")
    parser.add_argument("--task_name", type=str, default=None, help="Run a single specific task by name (e.g., webclones.omnizon-1)")
    parser.add_argument("--task_type", type=str, default=None, help="Run all tasks of a specific type (e.g., omnizon)")

    args = parser.parse_args()

    if not args.task_name and not args.task_type:
        print("ERROR: You must specify either --task_name or --task_type.")
        sys.exit(1)

    config = AgentConfig(
        model_name=args.model,
        use_screenshot=args.use_screenshot,
        use_ocr=args.use_ocr,
        vision_model_name=args.vision_model
    )
    agent_args = MyAgentArgs(config=config)

    harness = REAL.harness(
        agentargs=agent_args,
        task_name=args.task_name,
        task_type=args.task_type,
        headless=args.headless,
        use_cache=args.use_cache,
        use_screenshot=config.use_screenshot,
        use_axtree=config.use_axtree,
        leaderboard=True,
        run_id="81b8ec39-3a80-4143-b2f5-d1de51d12a73",
        num_workers=1
    )

    print("Starting run with modular agent and local memory...")
    harness.run()
    print("✅ Run finished.")