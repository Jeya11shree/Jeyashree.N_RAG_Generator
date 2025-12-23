"""Logging, timers, helpers, token estimates."""

import logging
import time


def get_logger(name=__name__):
    logging.basicConfig(level=logging.INFO, format="%(asctime)s %(levelname)s %(message)s")
    return logging.getLogger(name)


def now_ts():
    return time.time()


def estimate_tokens(text: str) -> int:
    """Rough token estimate: 1 token ~= 4 chars on average."""
    if not text:
        return 0
    return max(1, len(text) // 4)

