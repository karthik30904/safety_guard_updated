"""Plug-and-play AI guardrails for agent systems."""

from guardrail_utils.engine.guardrail_engine import GuardrailEngine
from guardrail_utils.engine.middleware import GuardrailMiddleware
from guardrail_utils.engine.pipeline import GuardrailPipeline
from guardrail_utils.guardrails.ethical.toxicity_detection import ToxicityDetectionGuardrail
from guardrail_utils.guardrails.security.hallucination_detection import HallucinationDetectionGuardrail
from guardrail_utils.guardrails.security.jailbreak_detection import JailbreakDetectionGuardrail
from guardrail_utils.guardrails.security.pii_detection import PIIDetectionGuardrail
from guardrail_utils.guardrails.security.prompt_injection import PromptInjectionGuardrail
from guardrail_utils.llm import AzureOpenAIClient, BaseLLMClient, BedrockClient, LLMFactory, OpenAIClient
from guardrail_utils.llm_guardrails import (
    LLMGuardrail,
    SemanticBiasGuardrail,
    SemanticHallucinationGuardrail,
    SemanticJailbreakGuardrail,
    SemanticModerationGuardrail,
    SemanticPromptInjectionGuardrail,
    SemanticResponseSafetyGuardrail,
    SemanticToxicityGuardrail,
)
from guardrail_utils.models.guardrail_result import GuardrailResult
from guardrail_utils.models.policy_result import PolicyResult
from guardrail_utils.models.schemas import (
    Action,
    Detection,
    GuardrailContext,
    GuardrailStage,
    GuardrailStatus,
    Severity,
)
from guardrail_utils.scoring import RiskDecision, RiskScorer

ToxicityGuardrail = ToxicityDetectionGuardrail

__all__ = [
    "Action",
    "Detection",
    "GuardrailContext",
    "GuardrailEngine",
    "GuardrailMiddleware",
    "GuardrailPipeline",
    "GuardrailResult",
    "GuardrailStage",
    "GuardrailStatus",
    "HallucinationDetectionGuardrail",
    "JailbreakDetectionGuardrail",
    "AzureOpenAIClient",
    "BaseLLMClient",
    "BedrockClient",
    "LLMFactory",
    "LLMGuardrail",
    "OpenAIClient",
    "PIIDetectionGuardrail",
    "PolicyResult",
    "PromptInjectionGuardrail",
    "RiskDecision",
    "RiskScorer",
    "SemanticBiasGuardrail",
    "SemanticHallucinationGuardrail",
    "SemanticJailbreakGuardrail",
    "SemanticModerationGuardrail",
    "SemanticPromptInjectionGuardrail",
    "SemanticResponseSafetyGuardrail",
    "SemanticToxicityGuardrail",
    "Severity",
    "ToxicityDetectionGuardrail",
    "ToxicityGuardrail",
]
