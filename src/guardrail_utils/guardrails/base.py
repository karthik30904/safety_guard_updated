"""Base contract shared by every guardrail implementation."""

from __future__ import annotations

import asyncio
from abc import ABC, abstractmethod
from time import perf_counter

from guardrail_utils.models.guardrail_result import GuardrailResult
from guardrail_utils.models.schemas import GuardrailContext, GuardrailStage


class BaseGuardrail(ABC):
    """Small synchronous/asynchronous guardrail interface.

    Subclasses implement ``_evaluate`` only; this base class owns timing and the
    stage/enabled gate so every guardrail reports latency consistently.
    """

    name: str = "base"
    category: str = "generic"
    stage: GuardrailStage = GuardrailStage.BOTH

    def __init__(self, *, enabled: bool = True) -> None:
        """Create a guardrail that can be disabled without removing it."""
        self.enabled = enabled

    def supports(self, stage: GuardrailStage) -> bool:
        """Return whether this guardrail should run for the requested stage."""
        return self.enabled and (self.stage in {GuardrailStage.BOTH, stage})

    def evaluate(self, context: GuardrailContext) -> GuardrailResult:
        """Evaluate synchronously and attach measured latency."""
        started = perf_counter()
        result = self._evaluate(context)
        result.latency_ms = (perf_counter() - started) * 1000
        return result

    async def aevaluate(self, context: GuardrailContext) -> GuardrailResult:
        """Evaluate asynchronously and attach measured latency."""
        started = perf_counter()
        result = await self._aevaluate(context)
        result.latency_ms = (perf_counter() - started) * 1000
        return result

    @abstractmethod
    def _evaluate(self, context: GuardrailContext) -> GuardrailResult:
        """Implement guardrail-specific policy logic in subclasses."""
        ...

    async def _aevaluate(self, context: GuardrailContext) -> GuardrailResult:
        """Default async bridge for guardrails that only implement sync logic."""
        return await asyncio.to_thread(self._evaluate, context)
