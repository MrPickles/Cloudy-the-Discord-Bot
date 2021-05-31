import logging
from textwrap import dedent
from typing import List

import openai


logger = logging.getLogger(__name__)

react_prompt = dedent(
    """
    description: a red button that say stop
    code: <button style={{color: 'white', backgroundColor: 'red'}}>Stop</button>
    description: a blue box that contains 3 yellow circles with red borders
    code: <div style={{backgroundColor: 'blue', padding: 20}}><div style={{backgroundColor: 'yellow', border: '5px solid red', borderRadius: '50%', padding: 20, width: 100, height: 100}}></div><div style={{backgroundColor: 'yellow', borderWidth: 1, border: '5px solid red', borderRadius: '50%', padding: 20, width: 100, height: 100}}></div><div style={{backgroundColor: 'yellow', borderWidth: 1, border: '5px solid red', borderRadius: '50%', padding: 20, width: 100, height: 100}}></div></div>
    description:
"""
).rstrip()

def engines() -> List[str]:
    res = openai.Engine.list()
    logger.info(res)
    return [engine["id"] for engine in res["data"]]

def complete(msg: str) -> str:
    prompt = dedent(
        f"""
        The following is a conversation with an AI assistant. The assistant is helpful, creative, clever, and very friendly.

        Human: Hello, who are you?
        AI: I am an AI created by OpenAI. How can I help you today?
        Human: {msg}
        AI:
        """
    ).rstrip()
    res = openai.Completion.create(
        engine="davinci",
        prompt=prompt,
        max_tokens=150,
        temperature=0.9,
        presence_penalty=0.6,
        stop=["\n", "HUMAN:", "AI:"]
    )
    logger.info(res)
    return res["choices"][0]["text"]
