<h1>Raj's AGI Inc Web Agent </h1>
1. This project contains a high-performance, modular web agent designed to operate within the AGI SDK REAL benchmark. 
<br>
2. The agent is architected to be highly adaptable, using a dynamic prompt-routing system to select the best strategy for a given task. 
<br>
3. It features advanced reasoning capabilities, including self-correction, loop-breaking, and hyper-atomic planning to solve complex, multi-step web automation tasks.
<br>

<h2>Current Progress</h2>
<h4>

- Designed high level project architecture
- Orchestrator routing to prompts, agent, config, prompt_selector, main.
- Agent Designing
- Designed Memory and integration with MongoDB
- Prompt Routing
- LLM as a Judge
- Implemented prompt papers like Chain of Thought prompting.
- Prompt Creation for OMNIZON and DASHDISH.
- Model testing
- Setup and eval on realeval for OMNIZON and some tasks of DASHDISH.
</h4>

<h2>Future Work I will do</h2>
<h4>

- Submitting to public leader board and writing prompt for all special domain tasks.
- Improvising current Agent architecture (have to read some SOTA papers on Web Agent architectures)
- Testing with better LLMs and choose different LLM for each role and cost optimisation.
- Adding short term memory for faster inference.
- Building on better browser-use, Nova-act frameworks and fine tune some parts of multi-modal LLM.
- Prompt creation and fine-tuning prompts for all tasks.
- Setup and eval on realeval for all tasks.
- Based on the eval I will try out different algorithms and maybe try RLHF, DPO or some RL practises.
</h4>


<h2>Future improvements</h2>
<h4>

- The algo for capturing screenshots and BrowserGym’s HighLevelActionSet feature don't sync properly.
- We can create a map for button tasks, bid, action space by fine-tuning prompts or using more dedicated prompt with website workflow explanation.
- Add more tasks and make the AGI Inc Agent more generalised.
- Integrating with more agentic frameworks for cost and speed optimisation.
</h4>


<h1>🌟 Key Features</h1>
1. Modular Architecture: The agent's logic is separated into distinct components: a high-level Orchestrator (the project manager) and a focused Agent (the LLM specialist).

<br>
2. Dynamic Prompt Routing: Uses a small, fast LLM to analyze the task goal and dynamically load the correct "instruction manual" (prompt file) for the specific website (e.g., Omnizon, DashDish).

<br>
3. Chain-of-Thought Planning: The agent performs a "self-verification" step after creating a plan, critically reviewing it for logical flaws (like missing navigation steps) before execution begins.

<br>
4. Advanced Self-Correction & Recovery: The agent can detect when it's stuck in a repetitive failure loop (e.g., endless scrolling, trying to click a blocked element) and will change its strategy to recover.

<br>
5. Planning: Breaks down complex user goals into the smallest possible, single-action steps, which dramatically improves reliability, especially for multi-part UI interactions like selecting options in a dropdown.

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

Example (DashDish - Order Pizza):
```bash
python agiwebagent/main.py --task_name webclones.dashdish-3 --no-cache --headless true
```

Running a Full Task Suite<br>
To run all tasks for a specific website (like all 10 omnizon tasks), use the --task_type argument. This is ideal for benchmarking.

Example (Run all DashDish tasks):
```bash
python agiwebagent/main.py --task_type dashdish --no-cache --headless true
```

Example (Run all Omnizon tasks):
```bash
python agiwebagent/main.py --task_type omnizon --no-cache --headless true
```

Command-Line Arguments <br>
Argument	  &nbsp;&nbsp;&nbsp;&nbsp;||&nbsp;&nbsp; Description	&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;||&nbsp;&nbsp;&nbsp;Example <br>
--task_name	  &nbsp;||&nbsp;&nbsp;Runs a single, specific task by its full ID.&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;||&nbsp;&nbsp;	webclones.dashdish-2<br>
--task_type	  &nbsp;&nbsp;||&nbsp;&nbsp;Runs all tasks belonging to a specific benchmark suite.	&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;||&nbsp;&nbsp; dashdish, omnizon<br>
--headless	  &nbsp;&nbsp;||&nbsp;&nbsp;true or false. Runs the browser in the background (true) or shows the UI (false). &nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;||&nbsp;&nbsp; Default is false.	--headless true<br>
--no-cache	  &nbsp;&nbsp;||&nbsp;&nbsp;Disables caching and forces the agent to re-run the task from scratch. Highly recommended for testing changes.	&nbsp;&nbsp;||&nbsp;&nbsp; --no-cache<br>
--model	    &nbsp;&nbsp;||&nbsp;&nbsp;Specifies the OpenAI model to use for the main agent.	&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;||&nbsp;&nbsp;--model gpt-4o<br>

