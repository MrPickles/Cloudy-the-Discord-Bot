import logging
from typing import List

import openai
from openai.error import OpenAIError

import db

logger = logging.getLogger(__name__)


# This file contains wrappers for all OpenAI API calls.

def engines() -> List[str]:
    """Fetches all available engines for GPT-3."""
    try:
        res = openai.Engine.list()
        logger.info(res)
        return [engine["id"] for engine in res["data"]]
    except OpenAIError as e:
        logger.error(e)
        raise e


def complete(
    prompt: str,
    stop_tokens: List[str] = None,
    max_tokens=150,
) -> str:
    """Uses GPT-3 to complete the provided prompt."""
    try:
        stop = stop_tokens + ["\n"] if stop_tokens is not None else ["\n"]
        res = openai.Completion.create(
            engine="davinci",
            prompt=prompt,
            max_tokens=max_tokens,
            temperature=0.9,
            presence_penalty=0.6,
            stop=stop,
        )
        logger.info(res)
        db.increment_gpt_completions()
        return res["choices"][0]["text"]
    except OpenAIError as e:
        logger.error(e)
        raise e
