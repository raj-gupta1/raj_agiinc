# agent_src/prompt_selector.py

import importlib
from .prompts import base_prompts


class PromptSelector:
    # Map the task_id prefix to the prompt module
    PROMPT_ROUTING = {
        "omnizon": "agent_src.prompts.ecommerce_prompts",
        "dashdish": "agent_src.prompts.dashdish_prompts",
        "fly-unified": "agent_src.prompts.flyunified_prompts",
        "gocalendar": "agent_src.prompts.gocalendar_prompts",
        "networkin": "agent_src.prompts.networkIn_prompts",
        "opendining": "agent_src.prompts.opendining_prompts",
        "staynb": "agent_src.prompts.staynb_prompts",
        "topwork": "agent_src.prompts.topwork_prompts",
        "udriver": "agent_src.prompts.udriver_prompts",
        "zilloft": "agent_src.prompts.zilloft_prompts",
        "marrisuite": "agent_src.prompts.marrisuite_prompts",
    }

    # --- CORRECTED DEFAULTS ---
    # The new general prompt is now the default for any unrecognized task.
    DEFAULT_PROMPT = "agent_src.prompts.general_prompts"
    RETRIEVAL_PROMPT = "agent_src.prompts.retrieval_prompts"

    @staticmethod
    def get_prompts_for_task(task_id: str, goal: str):
        """
        Selects the appropriate prompt module based on the task_id or goal keywords.
        """
        task_prefix = task_id.split('-')[0].lower()
        specific_prompts_module = PromptSelector.PROMPT_ROUTING.get(task_prefix)

        if specific_prompts_module:
            print(f"✅ Prompt Selector: Task ID '{task_prefix}' detected. Loading specialized prompts.")
        else:
            goal_lower = goal.lower()
            retrieval_keywords = ["find", "retrieve", "list", "what is", "search for", "display", "identify"]
            if any(keyword in goal_lower for keyword in retrieval_keywords):
                print(f"✅ Prompt Selector: Retrieval task detected for '{task_prefix}'. Loading retrieval prompts.")
                specific_prompts_module = PromptSelector.RETRIEVAL_PROMPT
            else:
                print(f"⚠️ Prompt Selector: No specific prompts for '{task_prefix}'. Using general-purpose default.")
                specific_prompts_module = PromptSelector.DEFAULT_PROMPT

        # The rest of the file remains the same...
        try:
            specific_prompts = importlib.import_module(specific_prompts_module)
        except ImportError:
            print(f"🔥🔥🔥 CRITICAL FAILURE: Could not import prompt module {specific_prompts_module}")
            from .prompts import general_prompts as specific_prompts  # Fallback to general

        class Prompts:
            PLANNING_SYSTEM_PROMPT = getattr(specific_prompts, 'PLANNING_SYSTEM_PROMPT', "")
            EXECUTION_SYSTEM_PROMPT = base_prompts.EXECUTION_SYSTEM_PROMPT
            ACTION_SPACE_PROMPT = base_prompts.ACTION_SPACE_PROMPT
            FEW_SHOT_EXAMPLE_PROMPT = base_prompts.FEW_SHOT_EXAMPLE_PROMPT
            EXECUTION_USER_CONTEXT = base_prompts.EXECUTION_USER_CONTEXT
            SELF_CRITIQUE_PROMPT = base_prompts.SELF_CRITIQUE_PROMPT

        return Prompts()