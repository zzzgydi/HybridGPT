import os
import openai
from dotenv import load_dotenv
from typing import Optional
from hybrid.logger import logger

load_dotenv(verbose=True)

# openai.api_base = os.getenv("OPENAI_API_BASE")
openai.api_key = os.getenv("OPENAI_API_KEY")


def llm_chat(messages: list[dict], temperature=0.5, max_tokens: Optional[int] = None):
    response = openai.ChatCompletion.create(
        model="gpt-3.5-turbo",
        messages=messages,
        temperature=temperature,
        max_tokens=max_tokens,
    )

    usage = response["usage"]
    logger.debug(
        f"OpenAI Usage: prompt {usage['prompt_tokens']}, completion {usage['completion_tokens']}, total {usage['total_tokens']}"
    )

    return response["choices"][0]["message"]["content"]
