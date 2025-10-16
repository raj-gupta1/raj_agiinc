# debug_startup.py

import os
import traceback
from dotenv import load_dotenv
from openai import OpenAI
from agent_src.config import AgentConfig
from agent_src.orchestrator import TaskOrchestrator


# A mock object to simulate the action_set
class MockActionSet:
    def describe(self, *args, **kwargs):
        return "Mocked action descriptions."


def run_test():
    """Mimics the startup sequence to expose the hidden error."""
    print("--- Starting Direct Startup Test ---")

    try:
        # 1. Load Environment
        print("[1/5] Loading .env file...")
        load_dotenv()
        if not os.getenv("OPENAI_API_KEY"):
            print("❌ FAILURE: OPENAI_API_KEY not found. Check your .env file.")
            return
        print("   ✅ .env loaded.")

        # 2. Create Config and Client
        print("[2/5] Creating Config and OpenAI Client...")
        config = AgentConfig()
        client = OpenAI()
        print("   ✅ Config and Client created.")

        # 3. Create Orchestrator (this will also create the Agent)
        print("[3/5] Creating TaskOrchestrator...")
        orchestrator = TaskOrchestrator(config, client=client)
        print("   ✅ Orchestrator created successfully.")

        # 4. Prepare fake data for the first call
        print("[4/5] Preparing fake observation and action set...")
        fake_obs = {
            "goal": "Search for 'laptop' and display the first product.",
            "task_id": "omnizon-1",
            "screenshot": None,  # Not needed for this test
            "axtree_txt": "mock accessibility tree"
        }
        fake_action_set = MockActionSet()
        print("   ✅ Fake data prepared.")

        # 5. Attempt to start the generator (THIS IS THE LIKELY FAILURE POINT)
        print("[5/5] Attempting to start the orchestrator's execute generator...")
        generator = orchestrator.execute(fake_obs, fake_action_set)
        first_action = next(generator)
        print("   ✅ Generator started successfully.")
        print(f"   - First yielded action: {first_action}")

        print("\n" + "🎉" * 20)
        print("🎉🎉🎉 SUCCESS: The agent's startup sequence is working correctly! 🎉🎉🎉")
        print("🎉" * 20 + "\n")

    except Exception as e:
        print("\n" + "🔥" * 20 + " FATAL STARTUP ERROR DETECTED " + "🔥" * 20)
        print(f"The application crashed during initialization. Here is the exact error:")
        print("--- TRACEBACK ---")
        traceback.print_exc()
        print("🔥" * 68 + "\n")


if __name__ == "__main__":
    run_test()