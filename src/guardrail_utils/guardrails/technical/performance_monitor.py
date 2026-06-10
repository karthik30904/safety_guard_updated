"""Passive performance metadata guardrail."""

from __future__ import annotations

from guardrail_utils.guardrails.base import BaseGuardrail
from guardrail_utils.models.guardrail_result import GuardrailResult
from guardrail_utils.models.schemas import GuardrailContext, GuardrailStage
from guardrail_utils.utils.helpers import estimate_tokens


class PerformanceMonitorGuardrail(BaseGuardrail):
    """Attach size and token estimates without affecting policy decisions."""

    name = "performance_monitor"
    category = "technical"
    stage = GuardrailStage.BOTH

    def _evaluate(self, context: GuardrailContext) -> GuardrailResult:
        """Return a pass result enriched with lightweight performance metadata."""
        result = GuardrailResult.pass_(self.name, self.category)
        result.metadata = {
            "chars": len(context.text or ""),
            "estimated_tokens": estimate_tokens(context.text),
            "stage": context.stage.value,
        }
        return result
