#!/usr/bin/env python3
"""
Local Browser Agent - Run browser automation tasks on any website.

Usage:
    python local_agent.py --url "https://amazon.com" --goal "Search for laptop"
    python local_agent.py --goal "Find the weather in New York"
    
Note: Requires OPENAI_API_KEY or BROWSER_USE_API_KEY environment variable.
"""

import argparse
import asyncio
import os
import sys
from pathlib import Path

# Add parent directory for imports
sys.path.insert(0, str(Path(__file__).parent))

try:
    from browser_use import Agent
    # Try to use ChatBrowserUse if available (requires BROWSER_USE_API_KEY)
    try:
        from browser_use import ChatBrowserUse
        HAS_CHAT_BROWSER_USE = True
    except ImportError:
        HAS_CHAT_BROWSER_USE = False
    from langchain_openai import ChatOpenAI
except ImportError as e:
    print("❌ Missing dependencies. Please install browser-use:")
    print("   pip install browser-use langchain-openai")
    print(f"\nError: {e}")
    sys.exit(1)

from dotenv import load_dotenv

# Load environment variables
load_dotenv()


class BrowserUseLLM:
    """Wrapper to make ChatOpenAI compatible with browser-use v0.11+"""
    
    def __init__(self, model: str = "gpt-4o", temperature: float = 0):
        self._chat = ChatOpenAI(model=model, temperature=temperature)
        self.provider = "openai"  # Required by browser-use
        self.model = model
    
    def __getattr__(self, name):
        # Delegate all other attributes to the underlying ChatOpenAI
        return getattr(self._chat, name)
    
    async def ainvoke(self, *args, **kwargs):
        return await self._chat.ainvoke(*args, **kwargs)
    
    def invoke(self, *args, **kwargs):
        return self._chat.invoke(*args, **kwargs)


async def run_agent(url: str, goal: str, model: str = "gpt-4o"):
    """Run the browser agent with the given goal."""
    
    print(f"\n🌐 Starting Local Browser Agent")
    print(f"📍 URL: {url or 'New browser session'}")
    print(f"🎯 Goal: {goal}")
    print(f"🤖 Model: {model}")
    print("-" * 50)
    
    # Initialize the LLM
    # Use ChatBrowserUse if BROWSER_USE_API_KEY is set, otherwise use OpenAI wrapper
    if os.getenv("BROWSER_USE_API_KEY") and HAS_CHAT_BROWSER_USE:
        print("📡 Using Browser-Use Cloud LLM")
        llm = ChatBrowserUse()
    else:
        print("📡 Using OpenAI LLM")
        llm = BrowserUseLLM(model=model, temperature=0)
    
    # Prepare the full task
    if url:
        task = f"Go to {url} and then: {goal}"
    else:
        task = goal
    
    # Create the agent
    agent = Agent(
        task=task,
        llm=llm,
    )
    
    try:
        result = await agent.run()
        print("\n" + "=" * 50)
        print("✅ Task completed!")
        print("=" * 50)
        
        # Print result
        if result:
            print(f"\n📋 Result: {result}")
        
        return result
        
    except Exception as e:
        print(f"\n❌ Error: {e}")
        import traceback
        traceback.print_exc()
        raise


def main():
    parser = argparse.ArgumentParser(
        description="Run browser automation tasks with AI",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
  python local_agent.py --url "https://google.com" --goal "Search for Python tutorials"
  python local_agent.py --goal "Go to amazon.com and find wireless headphones under $50"
  python local_agent.py --url "https://github.com" --goal "Find the browser-use repository"

Environment Variables:
  OPENAI_API_KEY - Required for using OpenAI models
  BROWSER_USE_API_KEY - Optional, for using Browser-Use Cloud (get free credits at cloud.browser-use.com)
        """
    )
    
    parser.add_argument(
        "--url",
        type=str,
        default="",
        help="Starting URL (optional, can be included in goal)"
    )
    
    parser.add_argument(
        "--goal",
        type=str,
        required=True,
        help="The task goal in natural language"
    )
    
    parser.add_argument(
        "--model",
        type=str,
        default="gpt-4o",
        help="OpenAI model to use (default: gpt-4o)"
    )
    
    args = parser.parse_args()
    
    # Check for API key
    if not os.getenv("OPENAI_API_KEY") and not os.getenv("BROWSER_USE_API_KEY"):
        print("❌ Error: No API key found")
        print("   Set OPENAI_API_KEY in your .env file:")
        print("   export OPENAI_API_KEY='sk-your-key-here'")
        print("\n   Or get free Browser-Use credits at cloud.browser-use.com")
        sys.exit(1)
    
    # Run the agent
    asyncio.run(run_agent(
        url=args.url,
        goal=args.goal,
        model=args.model
    ))


if __name__ == "__main__":
    main()
