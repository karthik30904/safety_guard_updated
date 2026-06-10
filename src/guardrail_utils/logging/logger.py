"""Central logging utilities for guardrail runtime events.

The package uses Python's standard logging module only so applications can
route guardrail events into their own logging stack without adapter glue.
"""

from __future__ import annotations

import logging
import sys
from typing import Any


def get_logger(name: str = "guardrail_utils") -> logging.Logger:
    """Return a configured package logger.

    A default stdout handler keeps examples useful, while ``propagate=False``
    avoids duplicate logs in notebooks and agent runners that import repeatedly.
    """
    logger = logging.getLogger(name)
    if not logger.handlers:
        handler = logging.StreamHandler(sys.stdout)
        formatter = logging.Formatter(
            "%(asctime)s %(levelname)s [%(name)s] %(message)s",
            datefmt="%Y-%m-%d %H:%M:%S",
        )
        handler.setFormatter(formatter)
        logger.addHandler(handler)
    logger.setLevel(logging.INFO)
    logger.propagate = False
    return logger


def log_policy_event(event: str, **fields: Any) -> None:
    """Log structured policy events in a stable key/value format."""
    logger = get_logger("guardrail_utils.policy")
    payload = " ".join(f"{key}={value}" for key, value in fields.items())
    logger.info("%s %s", event, payload)


def log_exception(event: str, exc: Exception, **fields: Any) -> None:
    """Log recoverable guardrail exceptions without leaking full user content."""
    logger = get_logger("guardrail_utils.exceptions")
    payload = " ".join(f"{key}={value}" for key, value in fields.items())
    logger.exception("%s error=%s %s", event, exc.__class__.__name__, payload)
