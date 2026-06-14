"""Sequential and async execution pipeline for configured guardrails."""

from __future__ import annotations

import asyncio
from time import perf_counter

from guardrail_utils.core.config import GuardrailSettings
from guardrail_utils.guardrails.base import BaseGuardrail
from guardrail_utils.logging.logger import get_logger
from guardrail_utils.core.models import GuardrailResult, PolicyResult
from guardrail_utils.core.models import Action, GuardrailContext, GuardrailStage
from guardrail_utils.policies.policy_manager import PolicyManager

logger = get_logger("guardrail_utils.pipeline")


class GuardrailPipeline:
    """Run active guardrails for a specific input or output stage."""

    def __init__(
        self,
        guardrails: list[BaseGuardrail],
        *,
        policy_manager: PolicyManager | None = None,
        settings: GuardrailSettings | None = None,
    ) -> None:
        """Keep guardrail execution policy separate from guardrail definitions."""
        self.guardrails = guardrails
        self.settings = settings or GuardrailSettings()
        self.policy_manager = policy_manager or PolicyManager(self.settings)

    def run(self, text: str, stage: GuardrailStage, **context_fields: object) -> PolicyResult:
        """Run guardrails sequentially so sanitization flows into later checks."""
        started = perf_counter()
        context = GuardrailContext(stage=stage, text=text, original_text=text, **context_fields)
        current_text = text
        results: list[GuardrailResult] = []
        for guardrail in self._active_guardrails(stage):
            result = guardrail.evaluate(context.fork(text=current_text))
            results.append(result)
            self._log_result(result)
            if result.sanitized_text is not None:
                current_text = result.sanitized_text
            if self.settings.fail_fast and result.action == Action.BLOCK:
                break
        latency_ms = (perf_counter() - started) * 1000
        return self.policy_manager.resolve(original_text=text, current_text=current_text, results=results, latency_ms=latency_ms)

    async def arun(self, text: str, stage: GuardrailStage, **context_fields: object) -> PolicyResult:
        """Async sequential execution with the same semantics as ``run``."""
        started = perf_counter()
        context = GuardrailContext(stage=stage, text=text, original_text=text, **context_fields)
        current_text = text
        results: list[GuardrailResult] = []
        for guardrail in self._active_guardrails(stage):
            result = await guardrail.aevaluate(context.fork(text=current_text))
            results.append(result)
            self._log_result(result)
            if result.sanitized_text is not None:
                current_text = result.sanitized_text
            if self.settings.fail_fast and result.action == Action.BLOCK:
                break
        latency_ms = (perf_counter() - started) * 1000
        return self.policy_manager.resolve(original_text=text, current_text=current_text, results=results, latency_ms=latency_ms)

    async def arun_parallel_observe(self, text: str, stage: GuardrailStage, **context_fields: object) -> PolicyResult:
        """Run all guardrails concurrently for observability-heavy flows."""
        started = perf_counter()
        context = GuardrailContext(stage=stage, text=text, original_text=text, **context_fields)
        active = self._active_guardrails(stage)
        results = await asyncio.gather(*(guardrail.aevaluate(context) for guardrail in active))
        for result in results:
            self._log_result(result)
        latency_ms = (perf_counter() - started) * 1000
        return self.policy_manager.resolve(original_text=text, current_text=text, results=list(results), latency_ms=latency_ms)

    def _active_guardrails(self, stage: GuardrailStage) -> list[BaseGuardrail]:
        """Filter by settings first, then by each guardrail's declared stage."""
        active = []
        for guardrail in self.guardrails:
            if guardrail.name in self.settings.disabled_guardrails:
                continue
            if self.settings.enabled_guardrails and guardrail.name not in self.settings.enabled_guardrails:
                continue
            if guardrail.supports(stage):
                active.append(guardrail)
        return active

    def _log_result(self, result: GuardrailResult) -> None:
        if result.triggered:
            logger.warning(
                "guardrail_triggered name=%s action=%s severity=%s score=%.3f reason=%s latency_ms=%.2f",
                result.guardrail_name,
                result.action.value,
                result.severity.value,
                result.score,
                result.reason,
                result.latency_ms,
            )
        else:
            logger.info("guardrail_passed name=%s latency_ms=%.2f", result.guardrail_name, result.latency_ms)
