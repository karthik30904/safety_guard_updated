"""Result model returned by each individual guardrail."""

from __future__ import annotations

from typing import Any

from pydantic import BaseModel, Field

from guardrail_utils.models.schemas import Action, Detection, GuardrailStatus, Severity


class GuardrailResult(BaseModel):
    """Stable public result shape for one guardrail evaluation."""

    guardrail_name: str
    category: str
    status: GuardrailStatus = GuardrailStatus.PASSED
    action: Action = Action.ALLOW
    severity: Severity = Severity.INFO
    score: float = 0.0
    reason: str = ""
    original_text: str | None = None
    sanitized_text: str | None = None
    detections: list[Detection] = Field(default_factory=list)
    latency_ms: float = 0.0
    metadata: dict[str, Any] = Field(default_factory=dict)

    @property
    def triggered(self) -> bool:
        """Return whether the guardrail produced a non-pass action."""
        return self.status != GuardrailStatus.PASSED or self.action != Action.ALLOW

    @classmethod
    def pass_(cls, guardrail_name: str, category: str, latency_ms: float = 0.0) -> "GuardrailResult":
        """Build the canonical pass result used across the package."""
        return cls(
            guardrail_name=guardrail_name,
            category=category,
            latency_ms=latency_ms,
            reason="No violation detected.",
        )
