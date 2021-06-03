import logging
from datetime import datetime

logger = logging.getLogger(__name__)


class Lock():
    """A simple non-blocking mutex implementation.

    Since the bot's handlers run as coroutines while the API calls will block,
    we can make API calls claim a keyed lock per server, such that one single
    server cannot spam API calls.
    """
    def __init__(self):
        self.lock = {}
        # In case of error, we don't want stray locks to live forever.
        self.lock_lifespan_seconds = 300

    def claim_lock(self, key: int) -> bool:
        """Claims a lock on a given key. Returns whether the claim succeeded."""
        if self._is_locked(key):
            return False
        self.lock[key] = datetime.now()
        now = self.lock[key].strftime("%Y-%m-%d %H:%M:%S")
        logger.info("Claimed lock on %d at %s", key, now)
        return True

    def release_lock(self, key: int):
        """Releases the lock on a given key."""
        self.lock[key] = datetime.utcfromtimestamp(0)
        logger.info("Released lock on %d", key)

    def _is_locked(self, key: int) -> bool:
        if key not in self.lock:
            return False
        diff = datetime.now() - self.lock[key]
        return diff.total_seconds() < self.lock_lifespan_seconds
