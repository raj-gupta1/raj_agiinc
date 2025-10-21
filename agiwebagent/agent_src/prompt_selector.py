import importlib
import time
from openai import OpenAI, RateLimitError

class PromptSelector:
    PROMPT_PROFILES = {
        # ... (other profiles remain the same) ...

        "professional_networking": {
            # MODIFIED AGAIN: Extremely explicit about messaging.
            "description": "Handles ALL tasks on professional networking sites (like NetworkIn/LinkedIn). MANDATORY for: searching jobs/people, connecting, **ALL on-site messaging (sending, replying, following up)**, posting updates, **retrieving/summarizing feed content or profile details.**",
            "path": "agent_src.prompts.networkIn_prompts"
        },

        # ... (other profiles remain the same) ...

        "general_web_tasks": {
            # MODIFIED AGAIN: Explicitly excludes tasks covered by other profiles.
            "description": "FALLBACK ONLY. Use for simple web tasks ONLY IF no other specific profile fits (e.g., ecommerce, professional_networking). **DO NOT USE for on-site messaging, connecting, retrieving feed content, or shopping.** Suitable for basic web searches or simple form filling on generic websites.",
            "path": "agent_src.prompts.general_prompts"
        },
    }

    # ... (rest of the file remains the same) ...

    FALLBACK_PROMPTS_PATH = "agent_src.prompts.general_prompts"

    @staticmethod
    def _call_llm_with_retry(client: OpenAI, **kwargs):
        max_retries = 5
        base_delay = 1
        for i in range(max_retries):
            try:
                return client.chat.completions.create(**kwargs)
            except RateLimitError:
                if i < max_retries - 1:
                    time.sleep(base_delay * (2 ** i))
                else: raise
            except Exception: raise

    @staticmethod
    def _select_profile_with_llm(goal: str, client: OpenAI):
        profile_descriptions = "\n".join(f"- **{name}**: {data['description']}" for name, data in PromptSelector.PROMPT_PROFILES.items())
        # MODIFIED SYSTEM PROMPT: Added emphasis on reading descriptions carefully.
        system_prompt = f"""
            You are an expert routing system. Your task is to select the most appropriate "prompt profile" for the given user goal.
            **Read the profile descriptions VERY carefully.** Choose the profile that best matches the required task, paying close attention to keywords like "messaging", "retrieving", "connecting", "shopping".
            Respond with ONLY the name of the chosen profile (e.g., "ecommerce").
            If absolutely NO specific profile matches, respond with "general_web_tasks".
            Available Profiles:\n{profile_descriptions}"""
        try:
            print("Prompt Selector: Calling LLM to route goal...")
            response = PromptSelector._call_llm_with_retry(
                client=client, model="gpt-4o-mini",
                messages=[{"role": "system", "content": system_prompt}, {"role": "user", "content": f"User Goal: \"{goal}\""}],
                temperature=0, max_tokens=25
            )
            profile_name = response.choices[0].message.content.strip().lower().replace('.', '')
            # Simple validation: Check if the chosen name is actually in our profiles
            if profile_name not in PromptSelector.PROMPT_PROFILES:
                 print(f"LLM chose an invalid profile name '{profile_name}'. Correcting to fallback.")
                 profile_name = "general_web_tasks" # Correct invalid names to fallback
            print(f"LLM Router analyzed goal and selected profile: '{profile_name}'")
            return profile_name
        except Exception as e:
            print(f"LLM ROUTER FAILED: {e}. Defaulting to '{PromptSelector.FALLBACK_PROMPTS_PATH}'.")
            return "general_web_tasks" # Keep fallback on error

    @staticmethod
    def get_prompts(goal: str, client: OpenAI):
        print("\n" + "="*20 + " PROMPT SELECTION " + "="*20)
        print(f"Routing Goal: {goal}")

        chosen_profile_name = PromptSelector._select_profile_with_llm(goal, client)
        # Use .get() with a default value pointing to the fallback profile's data
        fallback_profile_data = PromptSelector.PROMPT_PROFILES.get("general_web_tasks", {"path": PromptSelector.FALLBACK_PROMPTS_PATH})
        profile = PromptSelector.PROMPT_PROFILES.get(chosen_profile_name)

        if profile:
            module_path = profile['path']
            print(f"Loading specialized '{chosen_profile_name}' prompts from: {module_path}")
        else:
            # This case should be less likely now due to validation in _select_profile_with_llm
            # But kept as a safeguard
            print(f"Profile '{chosen_profile_name}' not found or invalid. Falling back to default.")
            module_path = fallback_profile_data["path"]
            chosen_profile_name = "general_web_tasks" # Ensure consistency if falling back

        try:
            prompts_module = importlib.import_module(module_path)
            print(f"Successfully loaded module: {module_path}")
        except (ImportError, ModuleNotFoundError) as e:
            print(f"CRITICAL FAILURE: Could not import '{module_path}'. Error: {e}")
            print(f"Falling back to default module: {PromptSelector.FALLBACK_PROMPTS_PATH}")
            try:
                # Attempt to load the ultimate fallback path
                prompts_module = importlib.import_module(PromptSelector.FALLBACK_PROMPTS_PATH)
            except ImportError as final_e:
                print(f"FATAL: Could not even load the default prompts ('{PromptSelector.FALLBACK_PROMPTS_PATH}'). Error: {final_e}")
                # Define a minimal structure if even fallback fails
                class EmptyPrompts:
                    PLANNING_SYSTEM_PROMPT = "FATAL: Planning prompt missing."
                    EXECUTION_SYSTEM_PROMPT = "FATAL: Execution prompt missing."
                    ACTION_SPACE_PROMPT = "FATAL: Action prompt missing."
                    FEW_SHOT_EXAMPLE_PROMPT = "FATAL: Few-shot prompt missing."
                    EXECUTION_USER_CONTEXT = "FATAL: Context prompt missing."
                    SELF_CRITIQUE_PROMPT = "FATAL: Critique prompt missing."
                prompts_module = EmptyPrompts()

        print("="*58 + "\n")
        return prompts_module