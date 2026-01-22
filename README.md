# 🤖 AGI Web Agent

[![Python 3.11+](https://img.shields.io/badge/python-3.11+-blue.svg)](https://www.python.org/downloads/)
[![License: MIT](https://img.shields.io/badge/License-MIT-green.svg)](LICENSE)
[![Docker](https://img.shields.io/badge/docker-ready-blue.svg)](Dockerfile)

A modular web agent designed for the **AGI SDK REAL benchmark**, featuring dynamic prompt routing and Chain-of-Thought planning for autonomous web navigation.

📐 **[System Architecture Diagram (Miro)](https://miro.com/app/board/uXjVI86Rj0o=/?share_link_id=809744597370)**

---

## ✨ Key Features

- **🧠 Modular Architecture** — High-level Orchestrator (project manager) + focused Agent (LLM specialist)
- **🔀 Dynamic Prompt Routing** — Automatically selects task-specific prompts based on the goal
- **💭 Chain-of-Thought Planning** — Self-verification step reviews plans for logical flaws before execution
- **🔄 Advanced Self-Correction** — Detects stuck states and changes strategy to recover
- **📋 Granular Planning** — Breaks down complex goals into single-action steps for reliability

---

## 📂 Project Structure

```
agiinc/
├── README.md
├── requirements.txt              # Root dependencies
├── Dockerfile                    # Docker support
├── docker-compose.yml            # Easy orchestration
│
├── agiwebagent/                  # Web agent implementation
│   ├── main.py                   # Entry point
│   ├── requirements.txt          # Agent-specific dependencies
│   └── agent_src/
│       ├── agent.py              # LLM communication layer
│       ├── config.py             # Configuration dataclass
│       ├── memory.py             # Action history tracking
│       ├── orchestrator.py       # Task lifecycle manager
│       ├── prompt_selector.py    # Dynamic prompt routing
│       ├── llm_utils.py          # LLM utilities with retry logic
│       ├── vision_tools.py       # Visual OCR extraction
│       ├── utils.py              # Helper functions
│       └── prompts/              # Task-specific prompt files
│           ├── omnizon_prompts.py
│           ├── dashdish_prompts.py
│           └── ...
│
└── agisdk/                       # AGI SDK (submodule/dependency)
```

---

## 🚀 Quick Start

### Option 1: Local Installation

1. **Create a virtual environment**
   ```bash
   python -m venv agienv
   source agienv/bin/activate  # On Windows: agienv\Scripts\activate
   ```

2. **Install dependencies**
   ```bash
   pip install -r requirements.txt
   pip install -r agiwebagent/requirements.txt
   ```

3. **Configure your API key**
   
   Copy the example environment file and add your API key:
   ```bash
   cp .env.example .env
   # Edit .env and replace 'sk-your-api-key-here' with your actual OpenAI API key
   ```

4. **Run the agent**
   ```bash
   python agiwebagent/main.py --task_name webclones.omnizon-1 --headless true
   ```

### Option 2: Docker (Recommended)

1. **Configure your API key**
   ```bash
   cp .env.example .env
   # Edit .env and add your OpenAI API key
   ```

2. **Build and run**
   ```bash
   docker compose build
   docker compose run --rm agiwebagent \
     --task_name webclones.omnizon-1 \
     --headless true
   ```

---

## 📖 Usage

### Running a Single Task

```bash
python agiwebagent/main.py --task_name webclones.omnizon-1 --no-cache --headless true
```

### Running a Full Task Suite

```bash
# Run all Omnizon (e-commerce) tasks
python agiwebagent/main.py --task_type omnizon --headless true

# Run all DashDish (food delivery) tasks
python agiwebagent/main.py --task_type dashdish --headless true

# Run all NetworkIn (professional networking) tasks
python agiwebagent/main.py --task_type networkin --headless true
```

### Command-Line Arguments

| Argument | Description | Example |
|----------|-------------|---------|
| `--task_name` | Run a single task by ID | `webclones.omnizon-1` |
| `--task_type` | Run all tasks of a type | `omnizon`, `dashdish` |
| `--headless` | Run browser in background | `true` / `false` |
| `--no-cache` | Force re-run without cache | Flag |
| `--model` | OpenAI model for main agent | `gpt-4o`, `gpt-4o-mini` |
| `--vision_model` | Model for OCR/vision | `gpt-4o` |
| `--use_ocr` | Enable visual OCR | `true` / `false` |

### 🌐 Local Browser Agent (New!)

Run the agent on **any website** with natural language goals using `local_agent.py`:

```bash
# Install dependencies
pip install browser-use langchain-openai python-dotenv

# Run on any website
python agiwebagent/local_agent.py --goal "Go to amazon.com and search for wireless headphones"

# Or with a specific starting URL
python agiwebagent/local_agent.py --url "https://google.com" --goal "Search for Python tutorials"
```

| Argument | Description | Example |
|----------|-------------|---------|
| `--url` | Starting URL (optional) | `https://google.com` |
| `--goal` | Task in natural language | `"Search for laptops"` |
| `--model` | OpenAI model | `gpt-4o` |

---

## ⚙️ Configuration

### Environment Variables

| Variable | Description | Required |
|----------|-------------|----------|
| `OPENAI_API_KEY` | Your OpenAI API key | ✅ Yes |

### Agent Configuration

Edit `agiwebagent/agent_src/config.py` to customize:

```python
@dataclass
class AgentConfig:
    model_name: str = "gpt-4o"          # Main execution model
    plan_model_name: str = "gpt-4o"     # Planning model
    parser_model_name: str = "gpt-4o-mini"  # Prompt routing model
    vision_model_name: str = "gpt-4o"   # OCR/vision model
    max_steps: int = 25                 # Max steps per task
    max_retries: int = 3                # Max plan generation retries
    use_screenshot: bool = True         # Include screenshots
    use_axtree: bool = True             # Include accessibility tree
    use_ocr: bool = False               # Enable visual OCR
```

---

## 🔧 Troubleshooting

### Common Issues

**1. Playwright browsers not installed**
```bash
playwright install chromium
playwright install-deps
```

**2. Rate limit errors**
The agent has built-in exponential backoff retry logic. If you're hitting limits frequently, consider:
- Using a model with higher rate limits
- Reducing parallel execution

**3. Docker display issues (headed mode)**
For headed mode in Docker on Linux:
```bash
xhost +local:docker
docker-compose run --rm agiwebagent --headless false
```

---

## 🏗️ Architecture

```
┌─────────────────────────────────────────────────────────────┐
│                        main.py                              │
│                    (Entry Point)                            │
└──────────────────────────┬──────────────────────────────────┘
                           │
                           ▼
┌─────────────────────────────────────────────────────────────┐
│                    TaskOrchestrator                         │
│              (Manages task lifecycle)                       │
│  • Creates plans  • Handles errors  • Tracks progress       │
└──────────────────────────┬──────────────────────────────────┘
                           │
              ┌────────────┴────────────┐
              ▼                         ▼
┌──────────────────────┐    ┌──────────────────────┐
│   PromptSelector     │    │  HighPerformanceAgent │
│ (Routes to prompts)  │    │    (LLM Interface)    │
└──────────────────────┘    └──────────────────────┘
              │                         │
              ▼                         ▼
┌──────────────────────┐    ┌──────────────────────┐
│  prompts/*.py        │    │    AgentMemory       │
│ (Task-specific)      │    │  (History tracking)  │
└──────────────────────┘    └──────────────────────┘
```

---

## 🔮 Future Improvements

- [ ] Integrate DSPy for better prompt optimization
- [ ] Add RL post-training (GRPO, PPO)
- [ ] Test with different LLMs for role-based cost optimization
- [ ] Build on Nova-act and browser-use frameworks
- [ ] Fine-tune multimodal LLM components

---

## 📝 License

This project is licensed under the MIT License - see the [LICENSE](LICENSE) file for details.

---

## 🤝 Contributing

Contributions are welcome! Please feel free to submit a Pull Request.

1. Fork the repository
2. Create your feature branch (`git checkout -b feature/amazing-feature`)
3. Commit your changes (`git commit -m 'Add amazing feature'`)
4. Push to the branch (`git push origin feature/amazing-feature`)
5. Open a Pull Request
