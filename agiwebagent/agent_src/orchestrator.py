# agiwebagent/agent_src/orchestrator.py

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
    ACTION_KEYWORDS = ["click", "fill", "select", "go_back", "scroll","clear", "noop", "start", "end task", "report_infeasible", "send_msg_to_user"]

    def __init__(self, config: AgentConfig):
        self.config = config
        self.agent = None
        self.memory = AgentMemory()
        self.client = OpenAI()
        self.vision_extractor = VisionExtractor(self.client, model=config.vision_model_name)
        self.default_ocr_prompt = (
            "Extract all visible UI elements for content and information. "
            "Provide their label and type. Do not provide location data."
        )

    def _is_retrieval_step(self, instruction: str) -> bool:
        """
        Checks if the instruction is for information retrieval, not a direct action.
        """
        instruction_clean = instruction.lower().strip().replace('**', '')
        if instruction_clean in self.ACTION_KEYWORDS:
            return False
        for keyword in self.ACTION_KEYWORDS:
            if instruction_clean.startswith(keyword):
                return False
        print(f"Identified retrieval step: {instruction}")
        return True

    def _parse_plan_with_llm(self, model_response: str) -> list[str]:
        print("Parsing agent's plan response with regex...")
        try:
            plan_lines = re.findall(r"^\s*\d+\.\s+(.*)", model_response, re.MULTILINE)
            if plan_lines:
                print("Regex parser found plan.")
                return [line.strip() for line in plan_lines]
            else:
                single_line_plan = re.findall(r"\d+\.\s+(.*?)(?=\s*\d+\.|\s*$)", model_response)
                if single_line_plan:
                    print("Regex parser found single-line plan.")
                    return [line.strip() for line in single_line_plan]
            print(f"PLAN PARSER: No numbered list found in model response: {model_response[:100]}...")
            return []
        except Exception as e:
            print(f" PLAN PARSER REGEX FAILED: {e}")
            return []

    def _parse_and_validate_action(self, response_text: str) -> str:
        code_blocks = re.findall(r"```(.*?)```", response_text, re.DOTALL)
        action = None

        if code_blocks:
            action = code_blocks[-1].strip()
        else:
            action_line = re.search(r"^\s*(\d\.)?\s*action:\s*(.*)", response_text, re.MULTILINE | re.IGNORECASE)
            if action_line:
                action = action_line.group(2).strip()

        if action:
            match = re.match(r"fill\((['\"]?)(\d+)\1,\s*(['\"])(.*?)\3\)", action, re.DOTALL)
            if match:
                bid, text_to_fill = match.group(2), match.group(4)
                action = f"fill('{bid}', '{text_to_fill}')"
                print(f"🔧 Sanitized action: {action}")
            return action
        else:
            print("ACTION PARSER FAILED: Could not find code block ```...``` or 'action: ...' line.")
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
                selected_prompts = PromptSelector.get_prompts(goal, client=self.client, config=self.config)
                self.agent = HighPerformanceAgent(self.config, selected_prompts)
                print("Agent initialized with dynamically selected prompts.")

            self.memory.clear()
            action_desc = action_set.describe(with_long_description=True, with_examples=False)

            plan = []
            plan_retries = 0
            while plan_retries < self.config.max_retries:
                print(
                    f"\n Step 0.{plan_retries + 1}: Agent is creating a plan (Attempt {plan_retries + 1}/{self.config.max_retries})...")
                plan_response = self.agent.generate_plan(obs, action_desc)
                plan = self._parse_plan_with_llm(plan_response)  # Using regex parser

                start_found = any("start" in p.lower().strip().replace('**', '') for p in plan)
                end_found = any("end task" in p.lower().strip().replace('**', '') for p in plan)

                if plan and start_found and end_found:
                    print("Plan generated successfully.")
                    break
                else:
                    plan_retries += 1
                    print(
                        f"CRITICAL WARNING: Agent generated an invalid plan (Attempt {plan_retries}). Plan was: {plan}")
                    if plan_retries >= self.config.max_retries:
                        print("CRITICAL FAILURE: Max retries exceeded for plan generation.")
                        yield f"report_infeasible('Agent failed to generate a valid plan after {self.config.max_retries} attempts.')"
                        return
                    else:
                        print("Retrying plan generation...")
                        time.sleep(1)

            print("\n" + "=" * 20 + " AGENT'S PLAN " + "=" * 20)
            for i, step in enumerate(plan): print(f"{i + 1}. {step}")
            print("=" * 60)

            current_plan_step = 0
            while current_plan_step < len(plan) and self.memory.get_step_count() < self.config.max_steps:
                instruction = plan[current_plan_step]
                step_number = self.memory.get_step_count() + 1
                instruction_clean = instruction.lower().strip().replace('**', '')

                if instruction_clean == 'start':
                    current_plan_step += 1
                    continue
                if instruction_clean == 'end task':
                    print("Plan complete. Ending task.")
                    yield 'noop()'
                    return

                print(f"\n Step {step_number}: Executing Plan Step {current_plan_step + 1} -> '{instruction}'")

                ocr_data_string = "OCR is disabled."
                if self.config.use_ocr and self.config.use_screenshot and self._is_retrieval_step(instruction):
                    try:
                        print("OCR triggered: Information retrieval step.")
                        screenshot_img = Image.fromarray(obs["screenshot"])
                        ocr_data_string = self.vision_extractor.extract_content(
                            screenshot_img, self.default_ocr_prompt
                        )
                        print(f" OCR Result: {ocr_data_string[:250]}...")
                    except Exception as e:
                        print(f"OCR Tool Failed: {e}")
                        ocr_data_string = json.dumps({"error": f"OCR scan failed: {e}", "elements": []})

                error_for_prompt = obs.get("last_action_error")

                model_response = self.agent.execute_step(
                    obs, plan, current_plan_step, self.memory,
                    action_desc,
                    bool(error_for_prompt),
                    ocr_data_string
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
                        print("\n" + "=" * 20 + " NEW PLAN " + "=" * 20)
                        for i, step in enumerate(plan): print(f"{i + 1}. {step}")
                        print("=" * 60)
                        continue

                action = self._parse_and_validate_action(model_response)
                print(f"Action to execute: {action}")
                new_obs = yield action

                error_after_action = new_obs.get("last_action_error")
                if error_after_action:
                    print(f"Action Result: Failed with error -> {error_after_action}")
                else:
                    print("Action Result: Success")

                print("!!! DEBUG: ORCHESTRATOR V2 CHECKING FINISH COMMAND !!!")

                if action.startswith("report_infeasible"):
                    print("Agent has issued a finish command. Terminating task.")
                    return

                error = new_obs.get("last_action_error")
                self.memory.add_step(step_number, model_response, action, error)

                if error:
                    print(f"Error after action: {error}. Retrying same plan step.")

                elif action.startswith("scroll("):
                    print("Scroll action executed. Re-evaluating the same plan step on the new view.")

                elif action.strip() == "noop()":
                    if self._is_retrieval_step(instruction):
                        print("Confirmation/Retrieval noop executed. Proceeding to next step.")
                        current_plan_step += 1
                    else:
                        print("Waiting noop executed. Re-evaluating the same plan step.")
                else:
                    print(f"Action '{action}' successful. Proceeding to next step.")
                    current_plan_step += 1

                obs = new_obs

            if self.memory.get_step_count() >= self.config.max_steps:
                yield 'report_infeasible("Failed to complete the plan within the step limit.")'

        except Exception as e:
            print("FATAL ORCHESTRATOR ERROR: An exception occurred before the agent could act.")
            print(f"ERROR: {e}")
            print("TRACEBACK:")
            traceback.print_exc()
            yield f"report_infeasible('A fatal error occurred in the orchestrator: {str(e)}')"
            return