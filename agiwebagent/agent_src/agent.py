# agiwebagent/agent_src/agent.py

from openai import OpenAI
from . import utils, llm_utils
from .memory import AgentMemory

class HighPerformanceAgent:
    def __init__(self, config, prompts):
        self.config = config
        self.prompts = prompts
        self.client = OpenAI()

    def generate_plan(self, obs: dict, action_desc: str) -> str:
        system_msgs = [{"type": "text", "text": self.prompts.PLANNING_SYSTEM_PROMPT}]
        user_msgs = [
            {"type": "text", "text": f"# Goal\n{obs['goal']}"},
            {"type": "text", "text": self.prompts.ACTION_SPACE_PROMPT.format(action_space=action_desc)},
            {"type": "image_url", "image_url": {"url": utils.image_to_jpg_base64_url(obs["screenshot"])}}
        ]

        response = llm_utils.call_llm_with_retry(
            client=self.client,
            model=self.config.plan_model_name,
            messages=[{"role": "system", "content": system_msgs}, {"role": "user", "content": user_msgs}]
        )
        return response.choices[0].message.content

    def execute_step(self, obs: dict, plan: list, current_plan_step: int, memory: AgentMemory, action_desc: str, last_action_failed: bool) -> str:
        current_instruction = plan[current_plan_step]
        system_prompt_text = self.prompts.EXECUTION_SYSTEM_PROMPT.format(
            current_step_number=current_plan_step + 1,
            current_step_instruction=current_instruction
        )
        system_msgs = [{"type": "text", "text": system_prompt_text}]
        user_context = self.prompts.EXECUTION_USER_CONTEXT.format(
            goal=obs['goal'],
            plan="\n".join(f"{i + 1}. {s}" for i, s in enumerate(plan)),
            completed_steps=", ".join(str(i) for i in range(1, current_plan_step + 1)) or "None",
            current_step_number=current_plan_step + 1,
            current_step_instruction=current_instruction,
            history=memory.get_formatted_history(),
            axtree=obs['axtree_txt'],
            ocr_data=obs.get('ocr_data', 'No OCR data available.')
        )
        user_msgs = [
            {"type": "text", "text": user_context},
            {"type": "text", "text": self.prompts.ACTION_SPACE_PROMPT.format(action_space=action_desc)},
            {"type": "text", "text": self.prompts.FEW_SHOT_EXAMPLE_PROMPT},
            {"type": "image_url", "image_url": {"url": utils.image_to_jpg_base64_url(obs["screenshot"])}}
        ]
        if last_action_failed and obs.get("last_action_error"):
            critique_prompt_text = self.prompts.SELF_CRITIQUE_PROMPT.format(
                current_step_number=current_plan_step + 1,
                error_message=obs['last_action_error'],
                goal=obs['goal'],
                current_step_instruction=current_instruction,
                history=memory.get_formatted_history()
            )
            user_msgs.append({"type": "text", "text": critique_prompt_text})

        response = llm_utils.call_llm_with_retry(
            client=self.client,
            model=self.config.model_name,
            messages=[{"role": "system", "content": system_msgs}, {"role": "user", "content": user_msgs}]
        )
        return response.choices[0].message.content