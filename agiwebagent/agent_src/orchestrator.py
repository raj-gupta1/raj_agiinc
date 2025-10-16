# agiwebagent/agent_src/orchestrator.py

import re
import time
from openai import OpenAI, RateLimitError
from .agent import HighPerformanceAgent
from .memory import AgentMemory
from .config import AgentConfig
from .prompt_selector import PromptSelector


class TaskOrchestrator:
    def __init__(self, config: AgentConfig, client: OpenAI):
        self.config = config
        self.client = client
        self.agent = HighPerformanceAgent(config, client=self.client)
        self.memory = AgentMemory()
        self.parser_client = self.client
        self.prompts = None

    def _call_llm_with_retry(self, **kwargs):
        """Calls the OpenAI API with exponential backoff for rate limit errors."""
        max_retries = 5
        base_delay = 1
        for i in range(max_retries):
            try:
                return self.parser_client.chat.completions.create(**kwargs)
            except RateLimitError as e:
                if i < max_retries - 1:
                    wait_time = base_delay * (2 ** i)
                    print(f"⏳ Parser LLM rate limited. Retrying in {wait_time} seconds...")
                    time.sleep(wait_time)
                else:
                    raise e
            except Exception as e:
                raise e

    def _parse_plan_with_llm(self, model_response: str) -> list[str]:
        system_prompt = "You are a text parsing tool. Extract the numbered list plan. Respond ONLY with the numbered list, each step on a new line."
        try:
            response = self._call_llm_with_retry(
                model=self.config.parser_model_name,
                messages=[{"role": "system", "content": system_prompt}, {"role": "user", "content": model_response}],
                temperature=0, max_tokens=500
            )
            plan_text = response.choices[0].message.content.strip()
            return re.findall(r"^\s*\d+\.\s+(.*)", plan_text, re.MULTILINE) or []
        except Exception as e:
            print(f"🔥🔥🔥 PLAN PARSER FAILED: {e} 🔥🔥🔥")
            return []

    def _parse_and_validate_action(self, response_text: str) -> str:
        """Uses an LLM to parse and then validates/corrects the bid and scroll format."""
        system_prompt = "You are an expert parsing tool. Extract a single action command like `function('param')` from the user's text. Respond with ONLY the command. If no command is found, respond with `send_msg_to_user('Parse Error')`."
        try:
            response = self._call_llm_with_retry(
                model=self.config.parser_model_name,
                messages=[{"role": "system", "content": system_prompt}, {"role": "user", "content": response_text}],
                temperature=0, max_tokens=150
            )
            action = response.choices[0].message.content.strip().replace("```", "")
            match = re.search(r"(\w+)\((.*)\)", action)
            if match:
                action_name, args_str = match.groups()
                if action_name in ['click', 'fill']:
                    bid_match = re.search(r"(?<!['\"])\b(\d+)\b(?!['\"])", args_str)
                    if bid_match:
                        bid_num = bid_match.group(1)
                        corrected_args = args_str.replace(bid_num, f"'{bid_num}'", 1)
                        action = f"{action_name}({corrected_args})"
                        print(f"🛠️ Parser corrected invalid bid format -> {action}")

                elif action_name == 'scroll':
                    if "'" in args_str or '"' in args_str:
                        action = action.replace("'", "").replace('"', '')
                        print(f"🛠️ Parser corrected invalid scroll format -> {action}")
            return action
        except Exception as e:
            print(f"🔥🔥🔥 ACTION PARSER FAILED: {e} 🔥🔥🔥")
            return 'send_msg_to_user("Error: Parser API failed.")'

    def _parse_plan_from_critique(self, model_response: str) -> list[str] or None:
        if "new plan:" in model_response.lower():
            return re.findall(r"^\s*\d+\.\s+(.*)", model_response, re.MULTILINE) or None
        return None

    def execute(self, obs, action_set):
        try:
            print("🔧 Starting orchestrator.execute()...")
            goal = obs['goal']
            print(f"🎯 Task goal: {goal}")

            # Load appropriate prompts
            print("🔄 Calling PromptSelector.get_prompts_for_goal()...")
            self.prompts = PromptSelector.get_prompts_for_goal(goal, client=self.client)
            print("✅ Prompts loaded successfully")

            self.memory.clear()
            action_desc = action_set.describe(with_long_description=True, with_examples=False)
            print(f"📋 Action space described ({len(action_desc)} chars)")

            print("\n🤔 Step 0: Agent is creating a plan...")
            plan_response = self.agent.generate_plan(obs, action_desc, self.prompts)
            print(f"📝 Plan response received ({len(plan_response)} chars)")

            plan = self._parse_plan_with_llm(plan_response)
            print(f"📊 Plan parsed: {len(plan)} steps")

            if not plan:
                print("🔥 Plan parsing failed - no steps found")
                yield "report_infeasible('Agent failed to generate a valid plan.')"
                return

            if plan[0].lower() != "start" or plan[-1].lower() != "end task":
                print(f"🔥 Invalid plan structure. First: '{plan[0]}', Last: '{plan[-1]}'")
                yield "report_infeasible('Agent generated an invalid plan (missing Start/End).')"
                return

            print("\n" + "=" * 20 + " AGENT'S PLAN " + "=" * 21)
            for i, step in enumerate(plan):
                print(f"{i + 1}. {step}")
            print("=" * 58)

            current_plan_step = 0
            while current_plan_step < len(plan) and self.memory.get_step_count() < self.config.max_steps:
                instruction = plan[current_plan_step]
                step_number = self.memory.get_step_count() + 1

                if instruction.lower() == 'start':
                    current_plan_step += 1
                    continue

                print(f"\n🤔 Step {step_number}: Executing Plan Step {current_plan_step + 1} -> '{instruction}'")

                error_for_prompt = obs.get("last_action_error")
                model_response = self.agent.execute_step(obs, plan, current_plan_step, self.memory, action_desc,
                                                         bool(error_for_prompt), self.prompts)

                print("\n" + "=" * 20 + " AGENT'S THOUGHTS " + "=" * 20)
                print(model_response)
                print("=" * 58)

                if error_for_prompt:
                    new_plan = self._parse_plan_from_critique(model_response)
                    if new_plan:
                        print("\n" + "🔥" * 20 + " AGENT RE-PLANNED " + "🔥" * 21)
                        plan = new_plan
                        current_plan_step = 0
                        for i, step in enumerate(plan):
                            print(f"{i + 1}. {step}")
                        print("=" * 58)
                        continue

                action = self._parse_and_validate_action(model_response)
                print(f"🎬 Action to execute: {action}")

                new_obs = yield action

                if action.startswith("send_msg_to_user"):
                    print("✅ Agent has issued a finish command. Terminating task.")
                    return

                error = new_obs.get("last_action_error")
                self.memory.add_step(step_number, model_response, action, error)

                if error:
                    print(f"❌ Error after action: {error}. Retrying same plan step.")
                elif action.startswith("scroll("):
                    print("↕️ Scroll action executed. Re-evaluating the same plan step on the new view.")
                else:
                    current_plan_step += 1

                obs = new_obs

            yield 'send_msg_to_user("Failed to complete the plan within the step limit.")'

        except Exception as e:
            print(f"🔥🔥🔥 ORCHESTRATOR EXECUTE CRASH: {e}")
            import traceback
            traceback.print_exc()
            yield "report_infeasible('Orchestrator crashed during execution.')"