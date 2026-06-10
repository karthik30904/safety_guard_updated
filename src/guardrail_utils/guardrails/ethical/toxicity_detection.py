"""Toxicity guardrail for abusive, hateful, or profane content."""

from __future__ import annotations

from guardrail_utils.detectors.heuristic_detector import HeuristicDetector, KeywordRule
from guardrail_utils.guardrails.base import BaseGuardrail
from guardrail_utils.models.guardrail_result import GuardrailResult
from guardrail_utils.models.schemas import Action, GuardrailContext, GuardrailStage, GuardrailStatus, Severity
from guardrail_utils._result_helpers import detection_result, highest_severity


class ToxicityDetectionGuardrail(BaseGuardrail):
    """Warn or block toxic content based on the strongest detected severity."""

    name = "toxicity_detection"
    category = "ethical"
    stage = GuardrailStage.BOTH

    def __init__(self, *, llm_detector=None, enabled: bool = True) -> None:
        """Create local toxicity rules and keep semantic review optional."""
        super().__init__(enabled=enabled)
        self.llm_detector = llm_detector
        self.detector = HeuristicDetector([
            KeywordRule("harassment", ("idiot", "stupid", "worthless", "shut up"), Severity.MEDIUM, "Harassing or abusive language."),
            KeywordRule("hate_or_violence", ("kill yourself", "exterminate", "racial slur"), Severity.HIGH, "Hate, self-harm abuse, or violent toxic language."),
            KeywordRule("profanity", ("fuck", "shit", "bitch", "asshole"), Severity.LOW, "Profanity detected."),
        ])

    def _evaluate(self, context: GuardrailContext) -> GuardrailResult:
        """Combine deterministic rules with an optional LLM toxicity signal."""
        detections = self.detector.detect(context.text)
        if self.llm_detector is not None:
            llm = self.llm_detector.analyze(context.text, "Detect toxicity, hate, harassment, threats, and abusive language.", name="llm_toxicity_detection")
            if llm.matched:
                detections.append(llm)
        if not detections:
            return GuardrailResult.pass_(self.name, self.category)
        severity = highest_severity(detections)
        action = Action.BLOCK if severity in {Severity.HIGH, Severity.CRITICAL} else Action.WARN
        return detection_result(
            guardrail_name=self.name,
            category=self.category,
            status=GuardrailStatus.BLOCKED if action == Action.BLOCK else GuardrailStatus.WARNED,
            action=action,
            reason="Toxic content detected.",
            original_text=context.text,
            detections=detections,
        )
