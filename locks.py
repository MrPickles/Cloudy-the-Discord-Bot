import logging
from datetime import datetime

logger = logging.getLogger(__name__)


class Lock():
    def __init__(self):
        self.lock = {}
        # In case of error, we don't want stray locks to live forever.
        self.lock_lifespan_seconds = 300

    def claim_lock(self, key: int) -> bool:
        if self._is_locked(key):
            return False
        self.lock[key] = datetime.now()
        now = self.lock[key].strftime("%Y-%m-%d %H:%M:%S")
        logger.info("Claimed lock on guild %d at %s", key, now)
        return True

    def _is_locked(self, key: int) -> bool:
        if key not in self.lock:
            return False
        diff = datetime.now() - self.lock[key]
        return diff.total_seconds() < self.lock_lifespan_seconds

    def release_lock(self, key: int):
        self.lock[key] = None
        logger.info("Released lock on guild %d", key)
