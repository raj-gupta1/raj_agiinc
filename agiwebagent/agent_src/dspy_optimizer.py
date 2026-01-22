# agiwebagent/agent_src/dspy_optimizer.py
"""
DSPy integration for automated prompt optimization.
Provides optimizable signatures for planning, execution, and routing.
"""

import dspy
from typing import Optional


# === DSPy Signatures ===

class WebAgentPlanningSignature(dspy.Signature):
    """Generate a step-by-step plan to achieve a web browsing goal."""
    
    goal: str = dspy.InputField(desc="The user's goal to accomplish on the website")
    available_actions: str = dspy.InputField(desc="Available browser actions")
    screenshot_description: str = dspy.InputField(desc="Description of current page state")
    
    plan: str = dspy.OutputField(desc="Numbered list of specific steps to achieve the goal")


class WebAgentExecutionSignature(dspy.Signature):
    """Execute a single step from the plan by generating the appropriate action."""
    
    goal: str = dspy.InputField(desc="The overall goal")
    current_step: str = dspy.InputField(desc="The current step instruction to execute")
    page_state: str = dspy.InputField(desc="Current page accessibility tree")
    action_history: str = dspy.InputField(desc="Previous actions taken")
    available_actions: str = dspy.InputField(desc="Available action format")
    
    thought: str = dspy.OutputField(desc="Reasoning about how to execute this step")
    action: str = dspy.OutputField(desc="The specific action to take, e.g., click(id)")


class WebAgentRouterSignature(dspy.Signature):
    """Select the most appropriate prompt profile for a given goal."""
    
    goal: str = dspy.InputField(desc="The user's web browsing goal")
    available_profiles: str = dspy.InputField(desc="Available prompt profiles with descriptions")
    
    profile_name: str = dspy.OutputField(desc="Name of the selected profile")


class WebAgentSelfCritiqueSignature(dspy.Signature):
    """Analyze a failed action and suggest correction."""
    
    goal: str = dspy.InputField(desc="The overall goal")
    current_step: str = dspy.InputField(desc="The step that was being executed")
    last_action: str = dspy.InputField(desc="The action that failed")
    error_message: str = dspy.InputField(desc="The error that occurred")
    
    analysis: str = dspy.OutputField(desc="Analysis of what went wrong")
    corrected_action: str = dspy.OutputField(desc="The corrected action to try")


# === DSPy Modules ===

class WebAgentPlanner(dspy.Module):
    """Module for generating plans using DSPy optimization."""
    
    def __init__(self):
        super().__init__()
        self.planner = dspy.ChainOfThought(WebAgentPlanningSignature)
    
    def forward(self, goal: str, available_actions: str, screenshot_description: str) -> str:
        result = self.planner(
            goal=goal,
            available_actions=available_actions,
            screenshot_description=screenshot_description
        )
        return result.plan


class WebAgentExecutor(dspy.Module):
    """Module for executing single steps using DSPy optimization."""
    
    def __init__(self):
        super().__init__()
        self.executor = dspy.ChainOfThought(WebAgentExecutionSignature)
    
    def forward(self, goal: str, current_step: str, page_state: str, 
                action_history: str, available_actions: str) -> tuple[str, str]:
        result = self.executor(
            goal=goal,
            current_step=current_step,
            page_state=page_state,
            action_history=action_history,
            available_actions=available_actions
        )
        return result.thought, result.action


class WebAgentRouter(dspy.Module):
    """Module for routing goals to appropriate prompt profiles."""
    
    def __init__(self):
        super().__init__()
        self.router = dspy.Predict(WebAgentRouterSignature)
    
    def forward(self, goal: str, available_profiles: str) -> str:
        result = self.router(goal=goal, available_profiles=available_profiles)
        return result.profile_name.lower().strip()


# === DSPy Configuration ===

def configure_dspy(model_name: str = "gpt-4o", api_key: Optional[str] = None):
    """Configure DSPy with the specified LLM."""
    import os
    
    api_key = api_key or os.getenv("OPENAI_API_KEY")
    lm = dspy.LM(model=f"openai/{model_name}", api_key=api_key)
    dspy.configure(lm=lm)
    return lm


# === Optimizer Utilities ===

class DSPyOptimizer:
    """Handles optimization of DSPy modules using training examples."""
    
    def __init__(self, cache_dir: str = "dspy_cache"):
        self.cache_dir = cache_dir
        self.planner = WebAgentPlanner()
        self.executor = WebAgentExecutor()
        self.router = WebAgentRouter()
    
    def optimize_planner(self, trainset: list, metric_fn=None):
        """Optimize the planner module with training examples."""
        from dspy.teleprompt import BootstrapFewShot
        
        if metric_fn is None:
            # Default: check if plan has numbered steps
            metric_fn = lambda example, pred, trace: (
                any(c.isdigit() for c in pred.plan) and len(pred.plan) > 20
            )
        
        optimizer = BootstrapFewShot(metric=metric_fn, max_bootstrapped_demos=3)
        self.planner = optimizer.compile(self.planner, trainset=trainset)
        return self.planner
    
    def optimize_executor(self, trainset: list, metric_fn=None):
        """Optimize the executor module with training examples."""
        from dspy.teleprompt import BootstrapFewShot
        
        if metric_fn is None:
            # Default: check if action has valid format
            metric_fn = lambda example, pred, trace: (
                any(kw in pred.action.lower() for kw in ["click", "fill", "scroll", "select"])
            )
        
        optimizer = BootstrapFewShot(metric=metric_fn, max_bootstrapped_demos=3)
        self.executor = optimizer.compile(self.executor, trainset=trainset)
        return self.executor
    
    def save(self, path: str):
        """Save optimized modules."""
        import os
        os.makedirs(path, exist_ok=True)
        self.planner.save(f"{path}/planner.json")
        self.executor.save(f"{path}/executor.json")
        self.router.save(f"{path}/router.json")
    
    def load(self, path: str):
        """Load optimized modules."""
        self.planner.load(f"{path}/planner.json")
        self.executor.load(f"{path}/executor.json")
        self.router.load(f"{path}/router.json")
