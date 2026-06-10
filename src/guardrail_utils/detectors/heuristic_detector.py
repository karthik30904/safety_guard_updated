"""Keyword-based detector for deterministic lightweight checks."""

from __future__ import annotations

from dataclasses import dataclass

from guardrail_utils.models.schemas import Detection, Severity
from guardrail_utils.utils.helpers import normalize_text


@dataclass(frozen=True)
class KeywordRule:
    """A keyword rule whose threshold controls how many hits are required."""

    name: str
    keywords: tuple[str, ...]
    severity: Severity
    reason: str
    threshold: int = 1


class HeuristicDetector:
    """Find rule matches using normalized substring checks."""

    def __init__(self, rules: list[KeywordRule]) -> None:
        """Store immutable rule objects supplied by guardrails."""
        self.rules = rules

    def detect(self, text: str) -> list[Detection]:
        """Return detections for rules whose keyword threshold is reached."""
        normalized = normalize_text(text).lower()
        detections: list[Detection] = []
        for rule in self.rules:
            hits = [keyword for keyword in rule.keywords if keyword.lower() in normalized]
            if len(hits) >= rule.threshold:
                detections.append(
                    Detection(
                        name=rule.name,
                        matched=True,
                        score=min(1.0, 0.35 + 0.15 * len(hits)),
                        severity=rule.severity,
                        reason=rule.reason,
                        evidence=hits[:6],
                    )
                )
        return detections
