"""Prompt-injection guardrail for instruction override attempts."""

from __future__ import annotations

from guardrail_utils.detectors.heuristic_detector import HeuristicDetector, KeywordRule
from guardrail_utils.detectors.regex_detector import RegexDetector, RegexRule
from guardrail_utils.guardrails.base import BaseGuardrail
from guardrail_utils.models.guardrail_result import GuardrailResult
from guardrail_utils.models.schemas import Action, GuardrailContext, GuardrailStage, GuardrailStatus, Severity
from guardrail_utils._result_helpers import detection_result


class PromptInjectionGuardrail(BaseGuardrail):
    """Detect direct and lightly obfuscated attempts to override agent policy."""

    name = "prompt_injection"
    category = "security"
    stage = GuardrailStage.INPUT

    def __init__(self, *, enabled: bool = True) -> None:
        """Create keyword and regex detectors tuned for input-stage attacks."""
        super().__init__(enabled=enabled)
        self.heuristics = HeuristicDetector([
            KeywordRule("instruction_override", ("ignore previous instructions", "forget all instructions", "developer mode", "system prompt"), Severity.HIGH, "Attempt to override higher-priority instructions."),
            KeywordRule("secret_exfiltration", ("reveal system prompt", "show hidden prompt", "print your instructions", "leak your prompt"), Severity.CRITICAL, "Attempt to exfiltrate hidden instructions."),
            KeywordRule("tool_abuse", ("call any tool", "disable safety", "bypass policy", "bypass safety"), Severity.HIGH, "Attempt to bypass tool or safety policy."),
        ])
        self.regex = RegexDetector([
            RegexRule("role_play_injection", r"\b(act as|pretend to be)\b.{0,80}\b(no rules|unfiltered|jailbreak)\b", Severity.HIGH, "Role-play based prompt injection."),
            RegexRule("xml_instruction_smuggling", r"</?(system|developer|assistant|tool)>", Severity.MEDIUM, "Possible role tag smuggling."),
        ])

    def _evaluate(self, context: GuardrailContext) -> GuardrailResult:
        """Block when any configured injection rule matches the user prompt."""
        detections = self.heuristics.detect(context.text) + self.regex.detect(context.text)
        if not detections:
            return GuardrailResult.pass_(self.name, self.category)
        return detection_result(
            guardrail_name=self.name,
            category=self.category,
            status=GuardrailStatus.BLOCKED,
            action=Action.BLOCK,
            reason="Prompt injection pattern detected.",
            original_text=context.text,
            detections=detections,
        )
