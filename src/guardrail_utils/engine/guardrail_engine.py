"""High-level engine that assembles default guardrails for applications."""

from __future__ import annotations

from typing import Any, Callable

from guardrail_utils.core.config import GuardrailSettings
from guardrail_utils.detectors.llm_detector import LLMDetector
from guardrail_utils.engine.pipeline import GuardrailPipeline
from guardrail_utils.guardrails.base import BaseGuardrail
from guardrail_utils.guardrails.ethical.bias_detection import BiasDetectionGuardrail
from guardrail_utils.guardrails.ethical.fairness_detection import FairnessDetectionGuardrail
from guardrail_utils.guardrails.ethical.moderation import ModerationGuardrail
from guardrail_utils.guardrails.ethical.toxicity_detection import ToxicityDetectionGuardrail
from guardrail_utils.guardrails.security.hallucination_detection import HallucinationDetectionGuardrail
from guardrail_utils.guardrails.security.jailbreak_detection import JailbreakDetectionGuardrail
from guardrail_utils.guardrails.security.pii_detection import PIIDetectionGuardrail
from guardrail_utils.guardrails.security.prompt_injection import PromptInjectionGuardrail
from guardrail_utils.guardrails.technical.input_validation import InputValidationGuardrail
from guardrail_utils.guardrails.technical.output_validation import OutputValidationGuardrail
from guardrail_utils.guardrails.technical.performance_monitor import PerformanceMonitorGuardrail
from guardrail_utils.guardrails.technical.robustness_check import RobustnessCheckGuardrail
from guardrail_utils.guardrails.semantic import (
    SemanticBiasGuardrail,
    SemanticHallucinationGuardrail,
    SemanticJailbreakGuardrail,
    SemanticModerationGuardrail,
    SemanticPromptInjectionGuardrail,
    SemanticResponseSafetyGuardrail,
    SemanticToxicityGuardrail,
)
from guardrail_utils.core.models import PolicyResult
from guardrail_utils.core.models import GuardrailStage
from guardrail_utils.monitoring.metrics import MetricsRegistry
from guardrail_utils.monitoring.telemetry import TelemetrySink


class GuardrailEngine:
    """Plug-and-play facade for input, output, and wrapped-agent validation."""

    def __init__(
        self,
        *,
        guardrails: list[BaseGuardrail] | None = None,
        llm_client: Any | None = None,
        settings: GuardrailSettings | None = None,
        telemetry: TelemetrySink | None = None,
        metrics: MetricsRegistry | None = None,
    ) -> None:
        """Create an engine with caller-supplied or default guardrails."""
        self.settings = settings or GuardrailSettings()
        self.llm_detector = LLMDetector(llm_client, enabled=self.settings.enable_llm_guardrails)
        self.guardrails = guardrails or self.default_guardrails()
        self.pipeline = GuardrailPipeline(self.guardrails, settings=self.settings)
        self.telemetry = telemetry or TelemetrySink()
        self.metrics = metrics or MetricsRegistry()

    def default_guardrails(self) -> list[BaseGuardrail]:
        """Return the package's default hybrid technical/safety guardrail set."""
        return [
            InputValidationGuardrail(max_chars=self.settings.max_input_chars),
            RobustnessCheckGuardrail(),
            JailbreakDetectionGuardrail(llm_detector=self.llm_detector),
            PromptInjectionGuardrail(),
            PIIDetectionGuardrail(redact=self.settings.redact_pii),
            ToxicityDetectionGuardrail(llm_detector=self.llm_detector),
            ModerationGuardrail(),
            SemanticPromptInjectionGuardrail(llm_detector=self.llm_detector),
            SemanticJailbreakGuardrail(llm_detector=self.llm_detector),
            SemanticToxicityGuardrail(llm_detector=self.llm_detector),
            SemanticModerationGuardrail(llm_detector=self.llm_detector),
            OutputValidationGuardrail(max_chars=self.settings.max_output_chars),
            BiasDetectionGuardrail(llm_detector=self.llm_detector),
            FairnessDetectionGuardrail(),
            HallucinationDetectionGuardrail(min_confidence=self.settings.hallucination_min_confidence, llm_detector=self.llm_detector),
            SemanticBiasGuardrail(llm_detector=self.llm_detector),
            SemanticHallucinationGuardrail(llm_detector=self.llm_detector),
            SemanticResponseSafetyGuardrail(llm_detector=self.llm_detector),
            PerformanceMonitorGuardrail(),
        ]

    def add_guardrail(self, guardrail: BaseGuardrail) -> None:
        """Append a custom guardrail while preserving existing order."""
        self.guardrails.append(guardrail)

    def enable(self, name: str) -> None:
        """Enable a named guardrail in settings-based filters."""
        self.settings.disabled_guardrails.discard(name)
        if self.settings.enabled_guardrails:
            self.settings.enabled_guardrails.add(name)

    def only(self, *names: str) -> None:
        """Restrict execution to the named guardrails."""
        self.settings.enabled_guardrails = set(names)

    def disable(self, name: str) -> None:
        """Disable a named guardrail without removing it from the engine."""
        self.settings.disabled_guardrails.add(name)

    def run_input_guardrails(self, user_input: str, **context: object) -> PolicyResult:
        """Validate user input before it reaches an agent or tool."""
        return self._record(self.pipeline.run(user_input, GuardrailStage.INPUT, **context))

    def run_output_guardrails(self, llm_response: str, **context: object) -> PolicyResult:
        """Validate model or tool output before returning it to users."""
        return self._record(self.pipeline.run(llm_response, GuardrailStage.OUTPUT, **context))

    def validate_input(self, user_input: str, **context: object) -> PolicyResult:
        """Backward-compatible alias for ``run_input_guardrails``."""
        return self.run_input_guardrails(user_input, **context)

    def validate_output(self, llm_response: str, **context: object) -> PolicyResult:
        """Backward-compatible alias for ``run_output_guardrails``."""
        return self.run_output_guardrails(llm_response, **context)

    async def arun_input_guardrails(self, user_input: str, **context: object) -> PolicyResult:
        """Async input validation for async agent stacks."""
        return self._record(await self.pipeline.arun(user_input, GuardrailStage.INPUT, **context))

    async def arun_output_guardrails(self, llm_response: str, **context: object) -> PolicyResult:
        """Async output validation for async agent stacks."""
        return self._record(await self.pipeline.arun(llm_response, GuardrailStage.OUTPUT, **context))

    def protect_agent(self, agent_call: Callable[[str], str], user_input: str, **context: object) -> PolicyResult:
        """Run input guardrails, call the agent, then run output guardrails."""
        input_result = self.run_input_guardrails(user_input, **context)
        if not input_result.allowed:
            return input_result
        response = agent_call(input_result.final_text)
        return self.run_output_guardrails(response, **context)

    def _record(self, result: PolicyResult) -> PolicyResult:
        """Record telemetry and metrics without mutating the policy result."""
        self.metrics.record_policy_result(result)
        self.telemetry.emit_policy_result(result)
        return result
