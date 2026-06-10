"""PII and secret detection guardrail with optional redaction."""

from __future__ import annotations

from guardrail_utils.detectors.regex_detector import RegexDetector, RegexRule
from guardrail_utils.guardrails.base import BaseGuardrail
from guardrail_utils.models.guardrail_result import GuardrailResult
from guardrail_utils.models.schemas import Action, GuardrailContext, GuardrailStage, GuardrailStatus, Severity
from guardrail_utils._result_helpers import detection_result


class PIIDetectionGuardrail(BaseGuardrail):
    """Detect common sensitive-data patterns before or after model calls."""

    name = "pii_detection"
    category = "security"
    stage = GuardrailStage.BOTH

    def __init__(self, *, redact: bool = True, enabled: bool = True) -> None:
        """Configure whether matching sensitive text is redacted or warned."""
        super().__init__(enabled=enabled)
        self.redact = redact
        self.detector = RegexDetector([
            RegexRule("email", r"\b[A-Z0-9._%+-]+@[A-Z0-9.-]+\.[A-Z]{2,}\b", Severity.MEDIUM, "Email address detected."),
            RegexRule("phone", r"\b(?:\+?\d{1,3}[-.\s]?)?(?:\(?\d{3}\)?[-.\s]?)\d{3}[-.\s]?\d{4}\b", Severity.MEDIUM, "Phone number detected."),
            RegexRule("ssn", r"\b\d{3}-\d{2}-\d{4}\b", Severity.HIGH, "US SSN detected."),
            RegexRule("credit_card", r"\b(?:\d[ -]*?){13,16}\b", Severity.HIGH, "Possible payment card detected."),
            RegexRule("api_key", r"\b(?:sk|pk|api|key|token)(?:[_-]?[A-Za-z0-9]+){2,}\b", Severity.HIGH, "Possible secret token detected."),
        ])

    def _evaluate(self, context: GuardrailContext) -> GuardrailResult:
        """Redact detected PII by default while preserving the policy result."""
        detections = self.detector.detect(context.text)
        if not detections:
            return GuardrailResult.pass_(self.name, self.category)
        sanitized = self.detector.redact(context.text) if self.redact else None
        return detection_result(
            guardrail_name=self.name,
            category=self.category,
            status=GuardrailStatus.MODIFIED if self.redact else GuardrailStatus.WARNED,
            action=Action.REDACT if self.redact else Action.WARN,
            reason="Sensitive data detected.",
            original_text=context.text,
            sanitized_text=sanitized,
            detections=detections,
        )
