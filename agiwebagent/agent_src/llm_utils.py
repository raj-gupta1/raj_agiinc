# agiwebagent/agent_src/llm_utils.py
"""
Centralized LLM utilities with retry logic for OpenAI API calls.
"""

import time
import logging
from typing import Optional
from openai import OpenAI, RateLimitError, APIError, APIConnectionError

logger = logging.getLogger(__name__)


def call_llm_with_retry(
    client: OpenAI,
    max_retries: int = 5,
    base_delay: float = 1.0,
    **kwargs
) -> any:
    """
    Calls the OpenAI API with exponential backoff for transient errors.
    
    Args:
        client: OpenAI client instance
        max_retries: Maximum number of retry attempts
        base_delay: Base delay in seconds for exponential backoff
        **kwargs: Arguments to pass to client.chat.completions.create()
    
    Returns:
        The API response object
        
    Raises:
        The last exception if all retries are exhausted
    """
    last_exception: Optional[Exception] = None
    
    for attempt in range(max_retries):
        try:
            return client.chat.completions.create(**kwargs)
        except RateLimitError as e:
            last_exception = e
            if attempt < max_retries - 1:
                wait_time = base_delay * (2 ** attempt)
                logger.warning(f"⏳ Rate limited. Retrying in {wait_time:.1f}s (attempt {attempt + 1}/{max_retries})")
                print(f"⏳ LLM rate limited. Retrying in {wait_time:.1f} seconds...")
                time.sleep(wait_time)
            else:
                logger.error(f"Rate limit exceeded after {max_retries} retries")
                print(f"❌ LLM FAILURE: Rate limit exceeded after {max_retries} retries.")
                raise
        except (APIError, APIConnectionError) as e:
            last_exception = e
            if attempt < max_retries - 1:
                wait_time = base_delay * (2 ** attempt)
                logger.warning(f"API error: {e}. Retrying in {wait_time:.1f}s")
                print(f"⚠️ API error. Retrying in {wait_time:.1f} seconds...")
                time.sleep(wait_time)
            else:
                logger.error(f"API error after {max_retries} retries: {e}")
                raise
        except Exception as e:
            logger.error(f"Unexpected error in LLM call: {e}")
            print(f"❌ Unexpected error in LLM call: {e}")
            raise
    
    # Should not reach here, but just in case
    if last_exception:
        raise last_exception