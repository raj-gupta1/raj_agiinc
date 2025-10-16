# agiwebagent/agent_src/prompt_selector.py

import importlib
from openai import OpenAI


class PromptSelector:
    PROMPT_PROFILES = {
        "ecommerce": {
            "description": "Handles online shopping on sites like Omnizon: searching products, adding to a cart, and checking out.",
            "path": "agent_src.prompts.omnizon_prompts"
        },
        "food_delivery": {
            "description": "Handles food delivery on sites like DashDish: browsing restaurants, adding menu items to an order, and checking out.",
            "path": "agent_src.prompts.dashdish_prompts"
        },
        "flight_booking": {
            "description": "Handles booking flights on sites like Fly Unified: searching routes, selecting dates, and entering passenger info.",
            "path": "agent_src.prompts.flyunified_prompts"
        },
        "hotel_booking": {
            "description": "Handles booking hotel stays on sites like Marrisuite: searching for hotels by destination and date, and completing reservations.",
            "path": "agent_src.prompts.marrisuite_prompts"
        },
        "accommodation_booking": {
            "description": "Handles booking vacation rentals on sites like Staynb: searching properties, selecting dates, and simulating a booking.",
            "path": "agent_src.prompts.staynb_prompts"
        },
        "restaurant_reservation": {
            "description": "Handles booking tables at restaurants on sites like OpenDining for a specific date, time, and party size.",
            "path": "agent_src.prompts.opendining_prompts"
        },
        "ride_sharing": {
            "description": "Handles ride-sharing tasks on sites like UDriver: booking a ride between two locations and comparing prices.",
            "path": "agent_src.prompts.udriver_prompts"
        },
        "calendar": {
            "description": "Handles scheduling on sites like GoCalendar: creating, modifying, or deleting events and managing calendars.",
            "path": "agent_src.prompts.gocalendar_prompts"
        },
        "professional_networking": {
            "description": "Handles tasks on professional social media like NetworkIn: finding jobs or people, and sending messages.",
            "path": "agent_src.prompts.networkIn_prompts"
        },
        "freelancer_marketplace": {
            "description": "Handles tasks on freelancer sites like TopWork: posting jobs, searching for freelancers, and managing hiring.",
            "path": "agent_src.prompts.topwork_prompts"
        },
        "real_estate": {
            "description": "Handles real estate tasks on sites like Zilloft: searching for homes, filtering properties, and viewing listings.",
            "path": "agent_src.prompts.zilloft_prompts"
        }
    }

    BASE_PROMPTS_PATH = "agent_src.prompts.base_prompts"

    @staticmethod
    def _select_profile_with_llm(goal: str, client: OpenAI):
        profile_descriptions = "\n".join(
            f"- **{name}**: {data['description']}" for name, data in PromptSelector.PROMPT_PROFILES.items())
        system_prompt = f"""
            You are an expert routing system. Your task is to select the most appropriate "prompt profile" for a given user goal.
            Respond with ONLY the name of the chosen profile (e.g., "ecommerce").
            If no profile is a good match, respond with "base".

            Available Profiles:
            {profile_descriptions}
            - **base**: A general-purpose profile for tasks that do not fit other categories.
            """
        try:
            response = client.chat.completions.create(
                model="gpt-4o-mini",
                messages=[{"role": "system", "content": system_prompt},
                          {"role": "user", "content": f"User Goal: \"{goal}\""}],
                temperature=0, max_tokens=20
            )
            return response.choices[0].message.content.strip().lower()
        except Exception as e:
            print(f"🔥🔥🔥 LLM ROUTER FAILED: {e}. Defaulting to 'base'.")
            return "base"

    @staticmethod
    def get_prompts_for_goal(goal: str, client: OpenAI):
        print(f"🎯 Goal: {goal}")

        # For now, always use base prompts to avoid import issues
        print("⚙️ Using base prompts for all tasks (specialized prompts disabled)")
        chosen_profile_name = "base"

        # Uncomment below to enable LLM-based routing
        chosen_profile_name = PromptSelector._select_profile_with_llm(goal, client=client)
        print(f"🧠 LLM Router selected profile: '{chosen_profile_name}'")

        if chosen_profile_name in PromptSelector.PROMPT_PROFILES:
            module_path = PromptSelector.PROMPT_PROFILES[chosen_profile_name]['path']
            print(f"📦 Loading specialized prompts from: {module_path}")
        else:
            module_path = PromptSelector.BASE_PROMPTS_PATH
            print(f"⚙️ Loading default base prompts from: {module_path}")

        try:
            module = importlib.import_module(module_path)
            print(f"✅ Successfully loaded prompts from: {module_path}")
            return module
        except ImportError as e:
            print(f"🔥🔥🔥 CRITICAL FAILURE: Could not import {module_path}. Error: {e}")
            print("🔄 Falling back to base_prompts...")
            from .prompts import base_prompts
            return base_prompts