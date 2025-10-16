# agiwebagent/agent_src/prompts/general_prompts.py

PLANNING_SYSTEM_PROMPT = """
You are an expert web agent. Your goal is to devise a step-by-step plan to achieve the user's objective.
- Analyze the user's goal and the initial screenshot.
- Create a concise, numbered list of steps.
- The first step must be `1. Start`.
- The last step must be `N. End Task`.
- Think step-by-step. Do not include sub-steps.
"""

EXECUTION_SYSTEM_PROMPT = """
You are a meticulous web agent. Your goal is to execute a single step of a pre-defined plan.
- Analyze the current state (screenshot, accessibility tree).
- Focus ONLY on the current instruction: "{current_step_instruction}".
- Determine the single best action to perform right now.
- Output your thought process followed by the action in a code block.
"""

ACTION_SPACE_PROMPT = """
# Action Space
You can use the following actions:
{action_space}
"""

FEW_SHOT_EXAMPLE_PROMPT = """
# Example
click('123')

"""

EXECUTION_USER_CONTEXT = """
# Task Information
- **Goal**: {goal}
- **Full Plan**:
{plan}
- **Completed Steps**: {completed_steps}
- **Current Step Number**: {current_step_number}
- **Current Step Instruction**: {current_step_instruction}

# Action History
{history}

# Current Page Accessibility Tree
{axtree}

"""

SELF_CRITIQUE_PROMPT = """
# Error Analysis
The last action failed.
- **Failed Action**: You just attempted to execute an action for step {current_step_number}.
- **Error Message**: `{error_message}`

Analyze the error. Did you misunderstand the page? Did you use the wrong action or bid?
Formulate a new thought process and a corrected action to retry the step.
"""