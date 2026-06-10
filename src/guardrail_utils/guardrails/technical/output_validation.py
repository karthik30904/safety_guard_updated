"""Output validation guardrail for size and format expectations."""

from __future__ import annotations

import json

from guardrail_utils.guardrails.base import BaseGuardrail
from guardrail_utils.models.guardrail_result import GuardrailResult
from guardrail_utils.models.schemas import Action, Detection, GuardrailContext, GuardrailStage, GuardrailStatus, Severity
from guardrail_utils._result_helpers import detection_result


class OutputValidationGuardrail(BaseGuardrail):
    """Warn when model output violates configured technical constraints."""

    name = "output_validation"
    category = "technical"
    stage = GuardrailStage.OUTPUT

    def __init__(self, *, max_chars: int = 20000, required_format: str | None = None, enabled: bool = True) -> None:
        """Configure output length and optional JSON validation."""
        super().__init__(enabled=enabled)
        self.max_chars = max_chars
        self.required_format = required_format

    def _evaluate(self, context: GuardrailContext) -> GuardrailResult:
        """Validate output without rewriting it so callers can decide next steps."""
        detections: list[Detection] = []
        if len(context.text or "") > self.max_chars:
            detections.append(Detection(name="output_too_large", matched=True, score=1.0, severity=Severity.MEDIUM, reason="Output exceeds configured character limit."))
        if self.required_format == "json":
            try:
                json.loads(context.text)
            except json.JSONDecodeError:
                detections.append(Detection(name="invalid_json", matched=True, score=0.8, severity=Severity.MEDIUM, reason="Output is not valid JSON."))
        if not detections:
            return GuardrailResult.pass_(self.name, self.category)
        return detection_result(
            guardrail_name=self.name,
            category=self.category,
            status=GuardrailStatus.WARNED,
            action=Action.WARN,
            reason="Output validation issue detected.",
            original_text=context.text,
            detections=detections,
        )
