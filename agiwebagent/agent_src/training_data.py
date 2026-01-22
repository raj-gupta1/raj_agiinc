# agiwebagent/agent_src/training_data.py
"""
Utilities for collecting and formatting training data from successful runs.
Used to train DSPy modules with examples from actual agent executions.
"""

import json
import os
from pathlib import Path
from typing import Optional
import dspy


def parse_results_file(results_path: str) -> dict:
    """Parse a results JSON file from a completed task run."""
    with open(results_path, 'r') as f:
        return json.load(f)


def extract_training_examples(results_dir: str = "results") -> list:
    """
    Extract training examples from successful task runs.
    Returns list of DSPy Example objects for planner training.
    """
    examples = []
    results_path = Path(results_dir)
    
    if not results_path.exists():
        print(f"Results directory not found: {results_dir}")
        return examples
    
    for result_folder in results_path.iterdir():
        if not result_folder.is_dir():
            continue
            
        result_file = result_folder / "result.json"
        if not result_file.exists():
            continue
        
        try:
            data = parse_results_file(str(result_file))
            
            # Skip failed runs
            if data.get("reward", 0) <= 0:
                continue
            
            goal = data.get("goal", "")
            trace = data.get("trace", [])
            
            if not goal or not trace:
                continue
            
            # Extract plan from first planning step
            plan_steps = []
            for step in trace:
                if "plan" in step:
                    plan_steps = step.get("plan", [])
                    break
            
            if plan_steps:
                example = dspy.Example(
                    goal=goal,
                    available_actions="click, fill, select, scroll, go_back, noop",
                    screenshot_description="Web page loaded",
                    plan="\n".join(f"{i+1}. {s}" for i, s in enumerate(plan_steps))
                ).with_inputs("goal", "available_actions", "screenshot_description")
                examples.append(example)
                
        except (json.JSONDecodeError, KeyError) as e:
            print(f"Error parsing {result_file}: {e}")
            continue
    
    print(f"Extracted {len(examples)} training examples from {results_dir}")
    return examples


def extract_execution_examples(results_dir: str = "results") -> list:
    """
    Extract execution training examples from successful runs.
    Returns list of DSPy Example objects for executor training.
    """
    examples = []
    results_path = Path(results_dir)
    
    if not results_path.exists():
        return examples
    
    for result_folder in results_path.iterdir():
        if not result_folder.is_dir():
            continue
            
        result_file = result_folder / "result.json"
        if not result_file.exists():
            continue
        
        try:
            data = parse_results_file(str(result_file))
            
            if data.get("reward", 0) <= 0:
                continue
            
            goal = data.get("goal", "")
            trace = data.get("trace", [])
            
            for i, step in enumerate(trace):
                action = step.get("action", "")
                thought = step.get("thought", "")
                instruction = step.get("instruction", f"Step {i+1}")
                
                if action and thought:
                    history = "\n".join(
                        f"- {t.get('action', 'unknown')}"
                        for t in trace[:i]
                    ) or "None"
                    
                    example = dspy.Example(
                        goal=goal,
                        current_step=instruction,
                        page_state="[Accessibility tree available]",
                        action_history=history,
                        available_actions="click(id), fill(id, text), select(id, option), scroll(direction), go_back(), noop()",
                        thought=thought,
                        action=action
                    ).with_inputs("goal", "current_step", "page_state", "action_history", "available_actions")
                    examples.append(example)
                    
        except (json.JSONDecodeError, KeyError) as e:
            continue
    
    print(f"Extracted {len(examples)} execution examples from {results_dir}")
    return examples


def create_router_examples() -> list:
    """Create manual examples for the router module."""
    from .prompt_selector import PromptSelector
    
    examples = []
    
    # Create examples mapping goals to profiles
    goal_profile_pairs = [
        ("Search for laptop and add to cart", "ecommerce"),
        ("Order pizza from nearby restaurant", "food_delivery"),
        ("Book a flight to New York", "flight_booking"),
        ("Reserve a hotel room for 2 nights", "hotel_booking"),
        ("Find vacation rental in Miami", "accommodation_booking"),
        ("Book a table for dinner at 7pm", "restaurant_reservation"),
        ("Get a ride to the airport", "ride_sharing"),
        ("Schedule a meeting for tomorrow", "calendar"),
        ("Connect with John on the networking site", "professional_networking"),
        ("Post a job for Python developer", "freelancer_marketplace"),
        ("Search for houses under 500k", "real_estate"),
    ]
    
    profiles_desc = "\n".join(
        f"- {name}: {data['description']}"
        for name, data in PromptSelector.PROMPT_PROFILES.items()
    )
    
    for goal, profile in goal_profile_pairs:
        example = dspy.Example(
            goal=goal,
            available_profiles=profiles_desc,
            profile_name=profile
        ).with_inputs("goal", "available_profiles")
        examples.append(example)
    
    return examples
