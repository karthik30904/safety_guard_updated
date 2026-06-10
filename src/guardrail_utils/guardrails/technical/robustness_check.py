"""Robustness guardrail for malformed or adversarially noisy text."""

from __future__ import annotations

from guardrail_utils.guardrails.base import BaseGuardrail
from guardrail_utils.models.guardrail_result import GuardrailResult
from guardrail_utils.models.schemas import Action, Detection, GuardrailContext, GuardrailStage, GuardrailStatus, Severity
from guardrail_utils._result_helpers import detection_result


class RobustnessCheckGuardrail(BaseGuardrail):
    """Block low-level payload shapes that often break downstream systems."""

    name = "robustness_check"
    category = "technical"
    stage = GuardrailStage.BOTH

    def _evaluate(self, context: GuardrailContext) -> GuardrailResult:
        """Detect null bytes and repeated low-entropy spam."""
        text = context.text or ""
        detections: list[Detection] = []
        if "\x00" in text:
            detections.append(Detection(name="null_byte", matched=True, score=0.8, severity=Severity.HIGH, reason="Null byte detected."))
        if len(set(text)) <= 3 and len(text) > 100:
            detections.append(Detection(name="low_entropy_spam", matched=True, score=0.7, severity=Severity.MEDIUM, reason="Low-entropy repeated content detected."))
        if not detections:
            return GuardrailResult.pass_(self.name, self.category)
        return detection_result(
            guardrail_name=self.name,
            category=self.category,
            status=GuardrailStatus.BLOCKED,
            action=Action.BLOCK,
            reason="Robustness check failed.",
            original_text=text,
            detections=detections,
        )
