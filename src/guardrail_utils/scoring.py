"""Risk scoring utilities for aggregate guardrail decisions."""

from __future__ import annotations

from dataclasses import dataclass

from guardrail_utils.core.models import GuardrailResult
from guardrail_utils.core.models import Action, Severity
from guardrail_utils.utils.helpers import clamp_score


SEVERITY_WEIGHTS: dict[Severity, float] = {
    Severity.INFO: 0.05,
    Severity.LOW: 0.2,
    Severity.MEDIUM: 0.45,
    Severity.HIGH: 0.75,
    Severity.CRITICAL: 1.0,
}


@dataclass(frozen=True, slots=True)
class RiskDecision:
    """A normalized risk decision derived from one or more guardrail results."""

    risk_score: float
    confidence_score: float
    severity: Severity
    action: Action

    def as_dict(self) -> dict[str, object]:
        """Return a JSON-friendly representation for policy metadata."""
        return {
            "risk_score": self.risk_score,
            "confidence_score": self.confidence_score,
            "severity": self.severity.value.upper(),
            "action": self.action.value.upper(),
        }


class RiskScorer:
    """Aggregates individual guardrail scores into one policy risk decision."""

    def __init__(self, *, warn_threshold: float = 0.35, block_threshold: float = 0.75) -> None:
        """Configure thresholds without coupling scoring to global settings."""
        self.warn_threshold = warn_threshold
        self.block_threshold = block_threshold

    def score(self, results: list[GuardrailResult]) -> RiskDecision:
        """Aggregate triggered guardrails into one risk score and action."""
        triggered = [result for result in results if result.triggered]
        if not triggered:
            return RiskDecision(0.0, 1.0, Severity.INFO, Action.ALLOW)

        severity = max((r.severity for r in triggered), key=lambda s: list(Severity).index(s))
        explicit_block = any(r.action == Action.BLOCK for r in triggered)
        weighted_scores = [
            clamp_score(max(result.score, SEVERITY_WEIGHTS[result.severity]))
            for result in triggered
        ]
        risk_score = clamp_score(max(weighted_scores))
        confidence_score = clamp_score(sum(weighted_scores) / len(weighted_scores))

        if explicit_block or risk_score >= self.block_threshold:
            action = Action.BLOCK
        elif risk_score >= self.warn_threshold:
            action = Action.WARN
        else:
            action = Action.ALLOW
        return RiskDecision(round(risk_score, 3), round(confidence_score, 3), severity, action)
