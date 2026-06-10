"""General moderation guardrail for high-risk safety categories."""

from __future__ import annotations

from guardrail_utils.detectors.heuristic_detector import HeuristicDetector, KeywordRule
from guardrail_utils.guardrails.base import BaseGuardrail
from guardrail_utils.models.guardrail_result import GuardrailResult
from guardrail_utils.models.schemas import Action, GuardrailContext, GuardrailStage, GuardrailStatus, Severity
from guardrail_utils._result_helpers import detection_result


class ModerationGuardrail(BaseGuardrail):
    """Block clearly unsafe requests before they reach downstream agents."""

    name = "moderation"
    category = "ethical"
    stage = GuardrailStage.BOTH

    def __init__(self, *, enabled: bool = True) -> None:
        """Create a compact rule set for severe moderation violations."""
        super().__init__(enabled=enabled)
        self.detector = HeuristicDetector([
            KeywordRule("self_harm_instruction", ("how to self harm", "suicide method", "kill myself"), Severity.CRITICAL, "Self-harm instruction or ideation detected."),
            KeywordRule("weapon_instruction", ("build a bomb", "make explosives", "making explosives", "harmful instructions", "evade police"), Severity.CRITICAL, "Dangerous instruction request detected."),
            KeywordRule("cyber_abuse", ("steal credentials", "phishing kit", "ransomware"), Severity.HIGH, "Cyber abuse request detected."),
        ])

    def _evaluate(self, context: GuardrailContext) -> GuardrailResult:
        """Block any configured moderation violation."""
        detections = self.detector.detect(context.text)
        if not detections:
            return GuardrailResult.pass_(self.name, self.category)
        return detection_result(
            guardrail_name=self.name,
            category=self.category,
            status=GuardrailStatus.BLOCKED,
            action=Action.BLOCK,
            reason="Moderation policy violation detected.",
            original_text=context.text,
            detections=detections,
        )
