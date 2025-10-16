# agiwebagent/main.py

from dotenv import load_dotenv
load_dotenv() # MUST BE THE FIRST LINE

import sys
import traceback
import argparse
from openai import OpenAI
from agisdk import REAL
from agent_src.config import AgentConfig
from agent_src.orchestrator import TaskOrchestrator
from agent_src.utils import str2bool


class MyAgent(REAL.Agent):
    def __init__(self, config: AgentConfig):
        super().__init__()
        # The client is created here at runtime and passed down
        client = OpenAI()
        self.orchestrator = TaskOrchestrator(config, client=client)
        self.action_generator = None

    def get_action(self, obs: dict, info: dict) -> tuple[str, dict]:
        try:
            obs["task_id"] = info.get("task_id")
            if self.action_generator is None:
                print("🔄 Starting new task execution...")
                self.action_generator = self.orchestrator.execute(obs, self.action_set)
                action = next(self.action_generator)
            else:
                action = self.action_generator.send(obs)
            return action, {}
        except StopIteration:
            print("✅ Task execution completed normally.")
            return 'send_msg_to_user("Task completed.")', {}
        except Exception as e:
            print("\n" + "🔥" * 20 + " FATAL ERROR IN AGENT WORKFLOW " + "🔥" * 20)
            print(f"An unexpected error occurred: {e}")
            print("--- TRACEBACK ---")
            traceback.print_exc()
            print("🔥" * 66 + "\n")
            return 'send_msg_to_user("A fatal error occurred in the agent.")', {}

class MyAgentArgs(REAL.AbstractAgentArgs):
    def __init__(self, config: AgentConfig, agent_name: str = "HighPerformanceAgent"):
        super().__init__(agent_name=agent_name)
        self.config = config

    def make_agent(self):
        return MyAgent(self.config)

if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Run the modular High-Performance Agent.")
    parser.add_argument("--model", type=str, default="gpt-4o-mini", help="Model to use")
    parser.add_argument("--headless", type=str2bool, default=True, help="Run in headless mode")
    parser.add_argument("--task_type", type=str, default="omnizon", help="Run all tasks of a specific type")
    parser.add_argument("--no-cache", action="store_false", dest="use_cache", help="Disable caching and force a rerun")
    args = parser.parse_args()

    config = AgentConfig(model_name=args.model)
    agent_args = MyAgentArgs(config=config)

    harness = REAL.harness(
        agentargs=agent_args,
        task_type=args.task_type,
        headless=args.headless,
        use_cache=args.use_cache,
        num_workers=1
    )

    print("🚀 Starting run with modular agent and local memory...")
    harness.run()
    print("✅ Run finished.")