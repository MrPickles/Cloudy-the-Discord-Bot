import logging
from datetime import datetime
from replit import db

from util import fixtures

logger = logging.getLogger(__name__)

# This file provides an abstraction layer on top of the repl.it database.


def set_last_init():
    """Persists the timestamp when the bot was last instantiated."""
    last_init = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    db["last_init"] = last_init
    logger.info("Last initialization time set as: %s", last_init)


def switch_mode(guild_id: int, mode: str):
    """Changes the bot's behavior mode for a given Discord server."""
    key = _mode_key(guild_id)
    db[key] = mode
    if mode == fixtures.chat:
        del db[key]


def get_mode(guild_id: int):
    """Fetches the bot's behavior mode for a given Discord server."""
    key = _mode_key(guild_id)
    if key not in db:
        return fixtures.chat
    return db[key]


def increment_gpt_completions():
    """Increments the number of times the bot has called upon GPT-3."""
    _increment_counter("gpt_completions")


def get_gpt_completions() -> int:
    """Fetches the number of times the bot has called upon GPT-3."""
    return _get_counter("gpt_completions")


def increment_guild_count():
    """Increments the number of times the bot has joined a new Discord server."""
    _increment_counter("guilds_joined")


def get_guild_count() -> int:
    """Fetches the number of times the bot has joined a new Discord server."""
    return _get_counter("guilds_joined")


def _mode_key(guild_id: int) -> str:
    """Returns the formatted key representing a server's interaction mode."""
    return f"mode/{guild_id}"


def _increment_counter(metric: str):
    """Increments the value counter for an arbitrary key."""
    if metric not in db:
        db[metric] = 0
    db[metric] += 1


def _get_counter(metric: str) -> int:
    """Fetches the value counter for an arbitrary key."""
    if metric not in db:
        db[metric] = 0
    return db[metric]
