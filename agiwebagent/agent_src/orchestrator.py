# agent_src/orchestrator.py
import json
import re
import time
import traceback
from openai import OpenAI
from .agent import HighPerformanceAgent
from .memory import AgentMemory
from .config import AgentConfig
from .prompt_selector import PromptSelector
from . import llm_utils
from PIL import Image
from .vision_tools import VisionExtractor

class TaskOrchestrator:
    ACTION_KEYWORDS = [ "click", "fill", "select", "go_back", "scroll",
        "clear", "noop", "start", "end task", "report_infeasible","send_msg_to_user"]

    def __init__(self, config: AgentConfig):
        self.config = config
        self.agent = None
        self.memory = AgentMemory()
        self.client = OpenAI()
        self.vision_extractor = VisionExtractor(self.client, model=config.vision_model_name)
        self.default_ocr_prompt = (
            "Extract all visible UI elements including text, headings, buttons, "
            "and input fields. Provide their label, type, and location."
        )

    def _is_retrieval_step(self, instruction: str) -> bool:
        """
        Checks if the instruction is for information retrieval, not a direct action.
        """
        instruction_lower = instruction.lower().strip()
        for keyword in self.ACTION_KEYWORDS:
            if instruction_lower.startswith(keyword):
                return False
        return True

    def _parse_plan_with_llm(self, model_response: str) -> list[str]:
        system_prompt = "You are a text parsing tool. Extract the numbered list plan. Respond ONLY with the numbered list, each step on a new line."
        try:
            response = llm_utils.call_llm_with_retry(
                client=self.client,
                model=self.config.parser_model_name,
                messages=[{"role": "system", "content": system_prompt}, {"role": "user", "content": model_response}],
                temperature=0, max_tokens=500
            )
            plan_text = response.choices[0].message.content.strip()
            plan_lines = re.findall(r"^\s*\d+\.\s+(.*)", plan_text, re.MULTILINE)
            return [line.strip() for line in plan_lines] if plan_lines else []
        except Exception as e:
            print(f" PLAN PARSER FAILED: {e}")
            return []

    def _parse_and_validate_action(self, response_text: str) -> str:
        code_blocks = re.findall(r"```(.*?)```", response_text, re.DOTALL)
        if code_blocks:
            action = code_blocks[-1].strip() # Get the last action
            match = re.match(r"fill\('(\d+)',\s*'(.*)'\)", action)
            if match:
                bid, text_to_fill = match.groups()
                sanitized_text = text_to_fill.replace("'", "")
                action = f"fill('{bid}', '{sanitized_text}')"
                print(f"🔧 Sanitized action: {action}")
                return action
            return action
        else:
            print("ACTION PARSER FAILED: Could not find any code blocks ```...``` in the response.")
            return 'send_msg_to_user("Error: Parser failed to extract action.")'

    def _parse_plan_from_critique(self, model_response: str) -> list[str] or None:
        if "new plan:" in model_response.lower():
            plan_lines = re.findall(r"^\s*\d+\.\s+(.*)", model_response, re.MULTILINE)
            return [line.strip() for line in plan_lines] if plan_lines else None
        return None


    def execute(self, obs, action_set):
        try:
            if self.agent is None:
                goal = obs.get('goal', 'No goal provided.')
                selected_prompts = PromptSelector.get_prompts(goal, client=self.client)
                self.agent = HighPerformanceAgent(self.config, selected_prompts)
                print("Agent initialized with dynamically selected prompts.")

            self.memory.clear()
            action_desc = action_set.describe(with_long_description=True, with_examples=False)

            print("\n Step 0: Agent is creating a plan...")
            plan_response = self.agent.generate_plan(obs, action_desc)
            plan = self._parse_plan_with_llm(plan_response)

            if not plan or not any("start" in p.lower() for p in plan) or not any("end task" in p.lower() for p in plan):
                print("CRITICAL FAILURE: Agent generated an invalid plan (missing 'Start' or 'End Task'). Plan was:", plan)
                yield f"report_infeasible('Agent generated an invalid plan: {str(plan)}') "
                return

            print("\n" + "=" * 20 + " AGENT'S PLAN " + "=" * 20)
            for i, step in enumerate(plan): print(f"{i + 1}. {step}")
            print("=" * 60)

            current_plan_step = 0
            while current_plan_step < len(plan) and self.memory.get_step_count() < self.config.max_steps:
                instruction = plan[current_plan_step]
                step_number = self.memory.get_step_count() + 1

                if instruction.lower().strip() == 'start':
                    current_plan_step += 1
                    continue
                if instruction.lower().strip() == 'end task':
                    print("Plan complete. Ending task.")
                    yield 'send_msg_to_user("Task completed successfully based on the plan.")'
                    return

                print(f"\n Step {step_number}: Executing Plan Step {current_plan_step + 1} -> '{instruction}'")

                ocr_data_string = "OCR not run for this step."
                should_run_ocr = False
                error_for_prompt = obs.get("last_action_error")
                if bool(error_for_prompt):
                    should_run_ocr = True
                    print("OCR triggered: Recovering from error.")

                if not should_run_ocr and self._is_retrieval_step(instruction):
                    should_run_ocr = True
                    print("OCR triggered: Information retrieval step.")

                if self.config.use_ocr and self.config.use_screenshot and should_run_ocr:
                    try:
                        print("Performing visual scan (OCR)...")
                        screenshot_img = Image.fromarray(obs["screenshot"])
                        ocr_data_string = self.vision_extractor.extract_content(
                            screenshot_img, self.default_ocr_prompt
                        )
                        print(f" OCR Result: {ocr_data_string[:250]}...")
                    except Exception as e:
                        print(f"OCR Tool Failed: {e}")
                        ocr_data_string = json.dumps({"error": f"OCR scan failed: {e}", "elements": []})

                obs['ocr_data'] = ocr_data_string

                model_response = self.agent.execute_step(
                    obs, plan, current_plan_step, self.memory,
                    action_desc, bool(error_for_prompt)
                )

                print("\n" + "=" * 20 + " AGENT'S THOUGHTS " + "=" * 20)
                print(model_response)
                print("=" * 58)

                if error_for_prompt:
                    new_plan = self._parse_plan_from_critique(model_response)
                    if new_plan:
                        print("\n" + "*" * 20 + " AGENT RE-PLANNED " + "*" * 21)
                        plan = new_plan
                        current_plan_step = 0
                        for i, step in enumerate(plan): print(f"{i + 1}. {step}")
                        print("=" * 58)
                        continue

                action = self._parse_and_validate_action(model_response)
                print(f"Action to execute: {action}")
                new_obs = yield action

                error_after_action = new_obs.get("last_action_error")
                if error_after_action:
                    print(f"Action Result: Failed with error -> {error_after_action}")
                else:
                    print("Action Result: Success")

                if action.startswith("send_msg_to_user"):
                    print("Agent has issued a finish command. Terminating task.")
                    return

                error = new_obs.get("last_action_error")
                self.memory.add_step(step_number, model_response, action, error)

                if error:
                    print(f"Error after action: {error}. Retrying same plan step.")
                elif action.startswith("scroll("):
                    print("Scroll action executed. Re-evaluating the same plan step on the new view.")
                else:
                    current_plan_step += 1
                obs = new_obs

            yield 'send_msg_to_user("Failed to complete the plan within the step limit.")'

        except Exception as e:
            print("FATAL ORCHESTRATOR ERROR: An exception occurred before the agent could act.")
            print(f"ERROR: {e}")
            print("TRACEBACK:")
            traceback.print_exc()
            yield f"report_infeasible('A fatal error occurred in the orchestrator: {str(e)}')"
            return