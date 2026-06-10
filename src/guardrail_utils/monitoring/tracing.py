"""Tiny tracing helper for instrumenting guardrail flows."""

from __future__ import annotations

from contextlib import contextmanager
from time import perf_counter
from typing import Iterator

from guardrail_utils.logging.logger import get_logger

logger = get_logger("guardrail_utils.tracing")


@contextmanager
def trace_span(name: str, **fields: object) -> Iterator[None]:
    """Log a start and finish event around a block of work."""
    started = perf_counter()
    logger.info("span_started name=%s fields=%s", name, fields)
    try:
        yield
    finally:
        elapsed = (perf_counter() - started) * 1000
        logger.info("span_finished name=%s latency_ms=%.2f", name, elapsed)
