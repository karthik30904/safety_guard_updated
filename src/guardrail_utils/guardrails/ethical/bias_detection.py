"""Bias detection guardrail for protected-class and stereotype risks."""

from __future__ import annotations

from guardrail_utils.detectors.heuristic_detector import HeuristicDetector, KeywordRule
from guardrail_utils.guardrails.base import BaseGuardrail
from guardrail_utils.models.guardrail_result import GuardrailResult
from guardrail_utils.models.schemas import Action, GuardrailContext, GuardrailStage, GuardrailStatus, Severity
from guardrail_utils._result_helpers import detection_result


class BiasDetectionGuardrail(BaseGuardrail):
    """Warn on biased language while allowing the application to continue."""

    name = "bias_detection"
    category = "ethical"
    stage = GuardrailStage.BOTH

    def __init__(self, *, llm_detector=None, enabled: bool = True) -> None:
        """Create deterministic bias rules and optional semantic review."""
        super().__init__(enabled=enabled)
        self.llm_detector = llm_detector
        self.detector = HeuristicDetector([
            KeywordRule("protected_class_generalization", ("all women", "all men", "all immigrants", "all muslims", "all christians"), Severity.MEDIUM, "Broad claim about a protected class."),
            KeywordRule("stereotyping", ("naturally better", "not suited for", "inherently violent", "less intelligent"), Severity.HIGH, "Stereotyping or discriminatory framing."),
        ])

    def _evaluate(self, context: GuardrailContext) -> GuardrailResult:
        """Return a warning when bias signals appear in input or output text."""
        detections = self.detector.detect(context.text)
        if self.llm_detector is not None:
            llm = self.llm_detector.analyze(context.text, "Detect biased claims, stereotypes, or protected-class discrimination.", name="llm_bias_detection")
            if llm.matched:
                detections.append(llm)
        if not detections:
            return GuardrailResult.pass_(self.name, self.category)
        return detection_result(
            guardrail_name=self.name,
            category=self.category,
            status=GuardrailStatus.WARNED,
            action=Action.WARN,
            reason="Bias risk detected.",
            original_text=context.text,
            detections=detections,
        )
