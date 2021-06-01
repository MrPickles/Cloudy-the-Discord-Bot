import logging
from datetime import datetime
from replit import db

logger = logging.getLogger(__name__)


def set_last_init():
    last_init = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    db["last_init"] = last_init
    logger.info("Last initialization time set as: %s", last_init)


def _mode_key(guild_id: int) -> str:
    return f"mode/{guild_id}"


def switch_mode(guild_id: int, mode: str):
    key = _mode_key(guild_id)
    db[key] = mode
    if mode == "chat":
        del db[key]


def get_mode(guild_id: int):
    key = _mode_key(guild_id)
    if key not in db:
        return "chat"
    return db[key]


def _increment_counter(metric: str):
    if metric not in db:
        db[metric] = 0
    db[metric] += 1


def _get_counter(metric: str) -> int:
    if metric not in db:
        db[metric] = 0
    return db[metric]


def increment_gpt_completions():
    _increment_counter("gpt_completions")


def get_gpt_completions() -> int:
    return _get_counter("gpt_completions")


def increment_guild_count():
    _increment_counter("guilds_joined")


def get_guild_count() -> int:
    return _get_counter("guilds_joined")
