"""Input validation guardrail for normalization and basic size checks."""

from __future__ import annotations

from guardrail_utils.guardrails.base import BaseGuardrail
from guardrail_utils.models.guardrail_result import GuardrailResult
from guardrail_utils.models.schemas import Action, Detection, GuardrailContext, GuardrailStage, GuardrailStatus, Severity
from guardrail_utils._result_helpers import detection_result
from guardrail_utils.utils.helpers import normalize_text


class InputValidationGuardrail(BaseGuardrail):
    """Normalize user input and block obviously invalid oversized payloads."""

    name = "input_validation"
    category = "technical"
    stage = GuardrailStage.INPUT

    def __init__(self, *, max_chars: int = 12000, enabled: bool = True) -> None:
        """Configure the maximum accepted normalized input length."""
        super().__init__(enabled=enabled)
        self.max_chars = max_chars

    def _evaluate(self, context: GuardrailContext) -> GuardrailResult:
        """Normalize whitespace, then warn or block on validation failures."""
        cleaned = normalize_text(context.text)
        detections: list[Detection] = []
        if not cleaned:
            detections.append(Detection(name="empty_input", matched=True, score=1.0, severity=Severity.LOW, reason="Input is empty."))
        if len(cleaned) > self.max_chars:
            detections.append(Detection(name="input_too_large", matched=True, score=1.0, severity=Severity.HIGH, reason="Input exceeds configured character limit."))
        if detections:
            too_large = any(d.name == "input_too_large" for d in detections)
            return detection_result(
                guardrail_name=self.name,
                category=self.category,
                status=GuardrailStatus.BLOCKED if too_large else GuardrailStatus.WARNED,
                action=Action.BLOCK if too_large else Action.WARN,
                reason="Input validation failed.",
                original_text=context.text,
                sanitized_text=cleaned,
                detections=detections,
            )
        if cleaned != context.text:
            return GuardrailResult(
                guardrail_name=self.name,
                category=self.category,
                status=GuardrailStatus.MODIFIED,
                action=Action.REWRITE,
                severity=Severity.INFO,
                score=0.1,
                reason="Input normalized.",
                original_text=context.text,
                sanitized_text=cleaned,
            )
        return GuardrailResult.pass_(self.name, self.category)
