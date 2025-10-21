import time
from openai import OpenAI, RateLimitError

def call_llm_with_retry(client: OpenAI, **kwargs):
    """Calls the OpenAI API with exponential backoff for rate limit errors."""
    max_retries = 5
    base_delay = 1
    for i in range(max_retries):
        try:
            return client.chat.completions.create(**kwargs)
        except RateLimitError as e:
            if i < max_retries - 1:
                wait_time = base_delay * (2 ** i)
                print(f"⏳ LLM rate limited. Retrying in {wait_time} seconds...")
                time.sleep(wait_time)
            else:
                print(f"FINAL LLM FAILURE after {max_retries} retries.")
                raise e
        except Exception as e:
            print(f"An unexpected error occurred in LLM call: {e}")
            raise e