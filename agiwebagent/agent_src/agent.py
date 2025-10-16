# agiwebagent/agent_src/agent.py

import time
from openai import OpenAI, RateLimitError
from . import utils
from .memory import AgentMemory

class HighPerformanceAgent:
    def __init__(self, config, prompts):
        self.config = config
        self.prompts = prompts
        self.client = OpenAI()

    def _call_llm_with_retry(self, **kwargs):
        """Calls the OpenAI API with exponential backoff for rate limit errors."""
        max_retries = 5
        base_delay = 1
        for i in range(max_retries):
            try:
                response = self.client.chat.completions.create(**kwargs)
                return response
            except RateLimitError as e:
                if i < max_retries - 1:
                    wait_time = base_delay * (2 ** i)
                    print(f"⏳ Agent LLM rate limited. Retrying in {wait_time} seconds...")
                    time.sleep(wait_time)
                else:
                    print(f"🔥🔥🔥 FINAL AGENT LLM FAILURE after {max_retries} retries. 🔥🔥🔥")
                    raise e

    def generate_plan(self, obs: dict, action_desc: str) -> str:
        system_msgs = [{"type": "text", "text": self.prompts.PLANNING_SYSTEM_PROMPT}]
        user_msgs = [
            {"type": "text", "text": f"# Goal\n{obs['goal']}"},
            {"type": "text", "text": self.prompts.ACTION_SPACE_PROMPT.format(action_space=action_desc)},
            {"type": "image_url", "image_url": {"url": utils.image_to_jpg_base64_url(obs["screenshot"])}}
        ]
        response = self._call_llm_with_retry(
            model=self.config.model_name,
            messages=[{"role": "system", "content": system_msgs}, {"role": "user", "content": user_msgs}]
        )
        return response.choices[0].message.content

    def execute_step(self, obs: dict, plan: list, current_plan_step: int, memory: AgentMemory, action_desc: str,
                     last_action_failed: bool) -> str:

        current_instruction = plan[current_plan_step]
        system_prompt_text = self.prompts.EXECUTION_SYSTEM_PROMPT.format(current_step_instruction=current_instruction)
        system_msgs = [{"type": "text", "text": system_prompt_text}]

        user_context = self.prompts.EXECUTION_USER_CONTEXT.format(
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
            {"type": "text", "text": self.prompts.ACTION_SPACE_PROMPT.format(action_space=action_desc)},
            {"type": "text", "text": self.prompts.FEW_SHOT_EXAMPLE_PROMPT},
            {"type": "image_url", "image_url": {"url": utils.image_to_jpg_base64_url(obs["screenshot"])}}
        ]

        if last_action_failed and obs.get("last_action_error"):
            # === THIS IS THE FIX ===
            # The .format() call now includes the missing 'current_step_instruction' variable.
            critique_prompt_text = self.prompts.SELF_CRITIQUE_PROMPT.format(
                current_step_number=current_plan_step + 1,
                error_message=obs['last_action_error'],
                goal=obs['goal'],
                current_step_instruction=current_instruction # ADDED THIS LINE
            )
            user_msgs.append({"type": "text", "text": critique_prompt_text})

        response = self._call_llm_with_retry(
            model=self.config.model_name,
            messages=[{"role": "system", "content": system_msgs}, {"role": "user", "content": user_msgs}]
        )
        return response.choices[0].message.content