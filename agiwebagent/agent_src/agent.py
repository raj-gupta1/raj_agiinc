# agiwebagent/agent_src/agent.py

import time
from openai import OpenAI, RateLimitError
from . import utils
from .memory import AgentMemory
from .config import AgentConfig


class HighPerformanceAgent:
    def __init__(self, config: AgentConfig, client: OpenAI):
        self.config = config
        self.client = client

    def _call_llm_with_retry(self, **kwargs):
        max_retries = 5
        base_delay = 1
        for i in range(max_retries):
            try:
                return self.client.chat.completions.create(**kwargs)
            except RateLimitError as e:
                if i < max_retries - 1:
                    wait_time = base_delay * (2 ** i)
                    print(f"⏳ Agent LLM rate limited. Retrying in {wait_time} seconds...")
                    time.sleep(wait_time)
                else:
                    raise e
            except Exception as e:
                raise e

    def generate_plan(self, obs: dict, action_desc: str, prompts) -> str:
        print("🧠 Generating plan with LLM...")
        try:
            system_msgs = [{"type": "text", "text": prompts.PLANNING_SYSTEM_PROMPT}]
            user_msgs = [
                {"type": "text", "text": f"# Goal\n{obs['goal']}"},
                {"type": "text", "text": prompts.ACTION_SPACE_PROMPT.format(action_space=action_desc)},
                {"type": "image_url", "image_url": {"url": utils.image_to_jpg_base64_url(obs["screenshot"])}}
            ]
            response = self._call_llm_with_retry(
                model=self.config.model_name,
                messages=[{"role": "system", "content": system_msgs}, {"role": "user", "content": user_msgs}],
                max_tokens=1000
            )
            return response.choices[0].message.content
        except Exception as e:
            print(f"🔥 PLAN GENERATION FAILED: {e}")
            return "Start\nEnd Task"

    def execute_step(self, obs: dict, plan: list, current_plan_step: int, memory: AgentMemory, action_desc: str,
                     last_action_failed: bool, prompts) -> str:
        print(f"🎯 Executing step {current_plan_step + 1}...")
        try:
            current_instruction = plan[current_plan_step]

            system_prompt_text = prompts.EXECUTION_SYSTEM_PROMPT.format(current_step_instruction=current_instruction)
            system_msgs = [{"type": "text", "text": system_prompt_text}]

            user_context = prompts.EXECUTION_USER_CONTEXT.format(
                goal=obs['goal'],
                plan="\n".join(f"{i + 1}. {s}" for i, s in enumerate(plan)),
                completed_steps=", ".join(str(i) for i in range(1, current_plan_step + 1)) or "None",
                current_step_number=current_plan_step + 1,
                current_step_instruction=current_instruction,
                history=memory.get_formatted_history(),
                axtree=obs['axtree_txt']
            )

            user_msgs = [
                {"type": "text", "text": user_context},
                {"type": "text", "text": prompts.ACTION_SPACE_PROMPT.format(action_space=action_desc)},
                {"type": "text", "text": prompts.FEW_SHOT_EXAMPLE_PROMPT},
                {"type": "image_url", "image_url": {"url": utils.image_to_jpg_base64_url(obs["screenshot"])}}
            ]

            if last_action_failed and obs.get("last_action_error"):
                user_msgs.append({"type": "text", "text": prompts.SELF_CRITIQUE_PROMPT.format(
                    current_step_number=current_plan_step + 1,
                    error_message=obs['last_action_error']
                )})

            response = self._call_llm_with_retry(
                model=self.config.model_name,
                messages=[{"role": "system", "content": system_msgs}, {"role": "user", "content": user_msgs}],
                max_tokens=1000
            )
            return response.choices[0].message.content
        except Exception as e:
            print(f"🔥 STEP EXECUTION FAILED: {e}")
            return 'send_msg_to_user("Agent execution error")'