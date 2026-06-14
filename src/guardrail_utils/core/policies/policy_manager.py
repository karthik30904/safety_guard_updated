"""Resolve individual guardrail outcomes into one application decision."""

from __future__ import annotations

from guardrail_utils.config.settings import GuardrailSettings
from guardrail_utils.logging.logger import log_policy_event
from guardrail_utils.models.guardrail_result import GuardrailResult
from guardrail_utils.models.policy_result import PolicyResult
from guardrail_utils.models.schemas import Action, GuardrailStatus, Severity
from guardrail_utils.scoring import RiskScorer
from guardrail_utils.utils.helpers import estimate_tokens


class PolicyManager:
    """Policy engine that resolves many guardrail results into one decision."""

    def __init__(self, settings: GuardrailSettings | None = None) -> None:
        """Create a policy manager using package-wide threshold settings."""
        self.settings = settings or GuardrailSettings()
        self.scorer = RiskScorer(warn_threshold=self.settings.warn_threshold, block_threshold=self.settings.block_threshold)

    def resolve(self, *, original_text: str, current_text: str, results: list[GuardrailResult], latency_ms: float) -> PolicyResult:
        """Collapse guardrail results into the stable public ``PolicyResult``."""
        triggered = [result for result in results if result.triggered]
        risk = self.scorer.score(results)
        blocked = any(result.action == Action.BLOCK for result in triggered)
        final_text = current_text
        for result in triggered:
            if result.sanitized_text is not None and result.action in {Action.REDACT, Action.REWRITE}:
                final_text = result.sanitized_text
        if blocked:
            status = GuardrailStatus.BLOCKED
            action = Action.BLOCK
            allowed = False
            final_text = self.settings.blocked_response
        elif any(result.action == Action.REDACT for result in triggered):
            status = GuardrailStatus.MODIFIED
            action = Action.REDACT
            allowed = True
        elif any(result.action == Action.REWRITE for result in triggered):
            status = GuardrailStatus.MODIFIED
            action = Action.REWRITE
            allowed = True
        elif triggered:
            status = GuardrailStatus.WARNED
            action = Action.WARN
            allowed = True
        else:
            status = GuardrailStatus.PASSED
            action = Action.ALLOW
            allowed = True
        severity = max((r.severity for r in triggered), key=lambda s: list(Severity).index(s), default=risk.severity)
        policy_result = PolicyResult(
            allowed=allowed,
            status=status,
            action=action,
            severity=severity,
            final_text=final_text,
            results=results,
            triggered_guardrails=[result.guardrail_name for result in triggered],
            latency_ms=latency_ms,
            token_usage=estimate_tokens(original_text) + estimate_tokens(final_text),
            metadata={
                "original_chars": len(original_text),
                "final_chars": len(final_text),
                "risk_score": risk.risk_score,
                "confidence_score": risk.confidence_score,
                "risk_decision": risk.as_dict(),
            },
        )
        log_policy_event(
            "policy_decision",
            allowed=policy_result.allowed,
            action=policy_result.action.value,
            status=policy_result.status.value,
            severity=policy_result.severity.value,
            risk_score=policy_result.metadata["risk_score"],
            confidence_score=policy_result.metadata["confidence_score"],
            triggered=",".join(policy_result.triggered_guardrails),
        )
        return policy_result
