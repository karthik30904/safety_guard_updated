"""Regex-based detector for structured patterns such as PII."""

from __future__ import annotations

import re
from dataclasses import dataclass

from guardrail_utils.models.schemas import Detection, Severity


@dataclass(frozen=True)
class RegexRule:
    """A compiled-at-use regex policy rule with severity metadata."""

    name: str
    pattern: str
    severity: Severity
    reason: str
    flags: int = re.IGNORECASE | re.MULTILINE


class RegexDetector:
    """Run regex rules and optionally redact matching spans."""

    def __init__(self, rules: list[RegexRule]) -> None:
        """Store regex rules in caller-defined order for stable redaction."""
        self.rules = rules

    def detect(self, text: str) -> list[Detection]:
        """Return one detection per regex rule that matched the text."""
        detections: list[Detection] = []
        for rule in self.rules:
            matches = [m.group(0)[:80] for m in re.finditer(rule.pattern, text or "", rule.flags)]
            if matches:
                detections.append(
                    Detection(
                        name=rule.name,
                        matched=True,
                        score=min(1.0, 0.45 + 0.15 * len(matches)),
                        severity=rule.severity,
                        reason=rule.reason,
                        evidence=matches[:5],
                    )
                )
        return detections

    def redact(self, text: str, replacement: str = "[REDACTED]") -> str:
        """Apply every configured regex replacement in stable order."""
        redacted = text
        for rule in self.rules:
            redacted = re.sub(rule.pattern, replacement, redacted, flags=rule.flags)
        return redacted
