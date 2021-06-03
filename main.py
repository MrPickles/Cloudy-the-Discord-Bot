import os
import sys
import logging

import openai

from bot import Cloudy
from util import fixtures

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


def main():
    print("Welcome! You are running Cloudy, the Discord bot! ☁️ 🤖")

    # Fetch the Discord bot token.
    token = os.getenv("TOKEN")
    if token is None:
        logger.error("Missing bot token!")
        print("Please provide a token to run the bot. See the README for more details.")
        print("\t- If you're running this as a REPL, fork this repository and set the $TOKEN environment variable.")
        print(f"\t- To try out the live version, invite the bot to your Discord server via the following link: {fixtures.auth_url}")
        sys.exit(1)

    # Load the OpenAI API key.
    # Unlike the bot token, the OpenAI API key is a soft dependency.
    openai.api_key = os.getenv("OPENAI_API_KEY")
    if openai.api_key is None:
        logger.warning("Missing OpenAI API key! Bot actions that depend on GPT-3 may not work properly.")

    # Instantiate and run the bot.
    bot = Cloudy(command_prefix="!")
    bot.run(token)


if __name__ == "__main__":
    main()
