import logging
import os
import sys
from textwrap import dedent

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
        print(
            dedent(
                f"""
                Please provide a token to run the bot. See the README for more details.
    
                - If you're running this as a REPL, fork this repository and set the $TOKEN environment variable.
    
                - If you'd like to try out the live bot, invite Cloudy to your Discord server via the following link: {fixtures.auth_url}
    
                - If you're just browsing, check out the README for a demo. ;)
                """
            )
        )
        sys.exit(1)

    # Load the OpenAI API key.
    # Unlike the bot token, the OpenAI API key is a soft dependency.
    openai.api_key = os.getenv("OPENAI_API_KEY")
    if openai.api_key is None:
        logger.warning("Missing OpenAI API key! Bot actions that depend on GPT-3 may not work properly.")
        print("Note: Cloudy did not receive an OpenAI API key. The bot will still run, but expect degraded performance.")

    # Load the Etherscan API key.    
    # This is also a soft dependency.
    etherscan_api_key = os.getenv("ETHERSCAN_API_KEY")
    if etherscan_api_key is None:
        logger.warning("Missing Etherscan API key! Bot actions pertaining to Ethereum may not work properly.")
        print("Note: Cloudy did not receive an Etherscan API key. The bot will still run, but expect degraded performance.")

    # Instantiate and run the bot.
    bot = Cloudy(etherscan_api_key=etherscan_api_key)
    bot.run(token)


if __name__ == "__main__":
    main()
