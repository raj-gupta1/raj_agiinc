<h1>Raj's Web Agent </h1>
1. This project contains a modular web agent designed to operate within the AGI SDK REAL benchmark. 
<br>
2. The agent is architected to be using a dynamic prompt-routing system to select the best strategy for a given task. 
<br>

<h2>System Architecture Diagram: </h2>
<h3>
https://miro.com/app/board/uXjVI86Rj0o=/?share_link_id=809744597370
</h3>

<h2>Current repo contains</h2>
<h4>

- Designed high level project architecture
- Orchestrator routing to prompts, agent, config, prompt_selector, main.
- Designed Memory and integration with MongoDB
- Prompt Routing
- LLM as a Judge
- Implemented prompt papers like Chain of Thought prompting.
- Prompt Creation for OMNIZON and NetworkIn.
- Model testing
- Setup and eval on realeval for OMNIZON and some tasks of NetworkIn.
</h4>

<h2>Possible Improvements</h2>
<h4>

- Integrating DSpy for better prompt creation and handling.
- Using RL for post training maybe GRPO, PPO, continueous learning.
- Testing with better LLMs and choose different LLMs for each role and cost optimisation.
- Building on better browser-use, Nova-act frameworks and fine tune some parts of multi-modal LLM.
</h4>


<h2>Future improvements</h2>
<h4>

- The algo for capturing screenshots and BrowserGym’s HighLevelActionSet feature don't sync properly.
- We can create a better map for button tasks, bid, action space by fine-tuning prompts or using more dedicated prompt with website workflow explanation.
- Integrating with more agentic frameworks for cost and speed optimisation.
</h4>


<h2>Cost & Model Limitations</h2>
<h4>

- I am using cheap gpt-40-mini for everything but models can be changed through config.py and using multimodal reasoning models will significatly improve the performance.
- Post training or using GRPO with DSpy can improve the performance significantly.
</h4>



<h1>🌟 Key Features</h1>

-  **Modular Architecture:** The agent's logic is separated into distinct components: a high-level Orchestrator (the project manager) and a focused Agent (the LLM specialist). 
- **Dynamic Prompt Routing:** Uses a small, fast LLM to analyze the task goal and dynamically load the correct "instruction manual" (prompt file) for the specific website (e.g., Omnizon, DashDish). 
- **Chain-of-Thought Planning:** The agent performs a "self-verification" step after creating a plan, critically reviewing it for logical flaws (like missing navigation steps) before execution begins. 
- **Advanced Self-Correction & Recovery:** The agent can detect when it's stuck in a repetitive failure loop (e.g., endless scrolling, trying to click a blocked element) and will change its strategy to recover. 
- **Planning:** Breaks down complex user goals into the smallest possible, single-action steps, which dramatically improves reliability, especially for multi-part UI interactions like selecting options in a dropdown.

<h1>📂 Project Structure</h1>
The agent's source code is located entirely within the agiwebagent/ directory.

agiwebagent/<br>
├── main.py                &nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp; # The main entry point to launch the agent.<br>
├── requirements.txt        &nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;# Python dependencies.<br>
└── agent_src/             &nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp; # The core source code for the agent.<br>
    ├── __init__.py<br>
    ├── agent.py           &nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp; # The "Specialist": Communicates with the LLM.<br>
    ├── config.py          &nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp; # Simple configuration data class.<br>
    ├── memory.py           &nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;# Stores the history of actions for each step.<br>
    ├── orchestrator.py     &nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;# The "Manager": Oversees the entire task lifecycle.<br>
    ├── prompt_selector.py  &nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;# The "Strategy Advisor": Chooses the correct prompt file.<br>
    ├── utils.py            &nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;# Helper functions (e.g., image conversion).<br>
    └── prompts/            &nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;# Directory containing all specialized "brains".<br>
        ├── __init__.py<br>
        ├── dashdish_prompts.py &nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;# The brain for the DashDish food delivery site.<br>
        └── omnizon_prompts.py  # The brain for the Omnizon e-commerce site.<br>



<h1>🛠️ Setup Instructions</h1>
Follow these steps from the root directory of the project (agiinc/).

1. Create and Activate a Virtual Environment<br>
It's highly recommended to use a virtual environment to manage dependencies.

```bash
python -m venv agienv

source agienv/bin/activate
```
(On Windows, use agienv\Scripts\activate)

2. Install Dependencies <br>
Install all the required Python packages from both the root requirements.txt and the agent's specific requirements.txt.
```bash
pip install -r requirements.txt

pip install -r agiwebagent/requirements.txt
```

3. Set Up Your API Key <br>
The agent requires an OpenAI API key to function.
Create a file named .env in the root agiinc/ directory.

Add your API key to this file:

```bash
OPENAI_API_KEY="sk-YourSecretAPIKeyHere"
```

<h1>🚀 Running the Agent </h1>
All commands should be run from the root agiinc/ directory. The main script is located at agiwebagent/main.py.

Running a Single Task<br>
To run a specific, named task, use the --task_name argument. This is perfect for debugging.

Example (networkin):
```bash
python agiwebagent/main.py --task_name webclones.networkin-3 --no-cache --headless true
```

Running a Full Task Suite<br>
To run all tasks for a specific website (like all 10 omnizon tasks), use the --task_type argument. This is ideal for benchmarking.

Example (Run all networkin tasks):
```bash
python agiwebagent/main.py --task_type networkin --no-cache --headless true
```

Example (Run all Omnizon tasks):
```bash
python agiwebagent/main.py --task_type omnizon --no-cache --headless true
```


| Argument | Description | Example |
|----------|-------------|---------|
| `--task_name` | Runs a single, specific task by its full ID. | `webclones.dashdish-2` |
| `--task_type` | Runs all tasks belonging to a specific benchmark suite. | `dashdish`, `omnizon` |
| `--headless` | `true` or `false`. Runs the browser in the background (`true`) or shows the UI (`false`). Default is `false`. | `--headless true` |
| `--no-cache` | Disables caching and forces the agent to re-run the task from scratch. Highly recommended for testing changes. | `--no-cache` |
| `--model` | Specifies the OpenAI model to use for the main agent. | `--model gpt-4o` |