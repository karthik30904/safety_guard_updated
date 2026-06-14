"""Aggregate policy result returned to applications and agents."""

from __future__ import annotations

from pydantic import BaseModel, Field

from guardrail_utils.models.guardrail_result import GuardrailResult
from guardrail_utils.models.schemas import Action, GuardrailStatus, Severity


class PolicyResult(BaseModel):
    """Stable public decision shape after all active guardrails run."""

    allowed: bool = True
    status: GuardrailStatus = GuardrailStatus.PASSED
    action: Action = Action.ALLOW
    severity: Severity = Severity.INFO
    final_text: str
    results: list[GuardrailResult] = Field(default_factory=list)
    triggered_guardrails: list[str] = Field(default_factory=list)
    latency_ms: float = 0.0
    token_usage: int = 0
    metadata: dict[str, object] = Field(default_factory=dict)

    def summary(self) -> dict[str, object]:
        """Return a compact log-safe summary for telemetry."""
        return {
            "allowed": self.allowed,
            "status": self.status.value,
            "action": self.action.value,
            "severity": self.severity.value,
            "triggered_guardrails": self.triggered_guardrails,
            "latency_ms": self.latency_ms,
            "token_usage": self.token_usage,
        }
