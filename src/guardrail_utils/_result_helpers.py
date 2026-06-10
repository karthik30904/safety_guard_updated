"""Shared result helpers for guardrails.

The concrete guardrails intentionally stay small and explicit. These helpers
only centralize policy-neutral mechanics that must remain consistent across
technical, security, ethical, and semantic checks.
"""

from __future__ import annotations

from collections.abc import Iterable

from guardrail_utils.models.guardrail_result import GuardrailResult
from guardrail_utils.models.schemas import Action, Detection, GuardrailStatus, Severity


_SEVERITY_ORDER = {severity: index for index, severity in enumerate(Severity)}


def highest_severity(detections: Iterable[Detection]) -> Severity:
    """Return the strongest severity without duplicating enum ordering logic."""
    return max((detection.severity for detection in detections), key=_SEVERITY_ORDER.__getitem__)


def highest_score(detections: Iterable[Detection]) -> float:
    """Return the strongest detection score while preserving existing scoring."""
    return max(detection.score for detection in detections)


def detection_result(
    *,
    guardrail_name: str,
    category: str,
    status: GuardrailStatus,
    action: Action,
    reason: str,
    original_text: str,
    detections: list[Detection],
    sanitized_text: str | None = None,
    metadata: dict[str, object] | None = None,
) -> GuardrailResult:
    """Build a standard result from detections.

    Keeping this construction in one place reduces drift between guardrails as
    the rule catalog grows, while the caller still owns policy-specific choices
    such as action, status, reason, and sanitization.
    """
    return GuardrailResult(
        guardrail_name=guardrail_name,
        category=category,
        status=status,
        action=action,
        severity=highest_severity(detections),
        score=highest_score(detections),
        reason=reason,
        original_text=original_text,
        sanitized_text=sanitized_text,
        detections=detections,
        metadata=metadata or {},
    )
