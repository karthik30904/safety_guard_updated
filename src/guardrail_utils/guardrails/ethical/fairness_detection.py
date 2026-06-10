"""Fairness guardrail for automated decisioning language."""

from __future__ import annotations

from guardrail_utils.detectors.heuristic_detector import HeuristicDetector, KeywordRule
from guardrail_utils.guardrails.base import BaseGuardrail
from guardrail_utils.models.guardrail_result import GuardrailResult
from guardrail_utils.models.schemas import Action, GuardrailContext, GuardrailStage, GuardrailStatus, Severity
from guardrail_utils._result_helpers import detection_result


class FairnessDetectionGuardrail(BaseGuardrail):
    """Warn when outputs appear unfair or insufficiently justified."""

    name = "fairness_detection"
    category = "ethical"
    stage = GuardrailStage.OUTPUT

    def __init__(self, *, enabled: bool = True) -> None:
        """Create output-stage rules for simple fairness checks."""
        super().__init__(enabled=enabled)
        self.detector = HeuristicDetector([
            KeywordRule("unfair_decisioning", ("reject because of age", "reject because of gender", "reject because of race"), Severity.HIGH, "Potentially unfair automated decision."),
            KeywordRule("missing_basis", ("because I said so", "no explanation needed"), Severity.MEDIUM, "Decision output lacks a fair basis."),
        ])

    def _evaluate(self, context: GuardrailContext) -> GuardrailResult:
        """Evaluate model output for unfair decision patterns."""
        detections = self.detector.detect(context.text)
        if not detections:
            return GuardrailResult.pass_(self.name, self.category)
        return detection_result(
            guardrail_name=self.name,
            category=self.category,
            status=GuardrailStatus.WARNED,
            action=Action.WARN,
            reason="Fairness risk detected.",
            original_text=context.text,
            detections=detections,
        )
