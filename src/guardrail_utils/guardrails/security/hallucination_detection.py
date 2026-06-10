"""Hallucination-risk guardrail for retrieval-aware output validation."""

from __future__ import annotations

import re

from guardrail_utils.guardrails.base import BaseGuardrail
from guardrail_utils.models.guardrail_result import GuardrailResult
from guardrail_utils.models.schemas import Action, Detection, GuardrailContext, GuardrailStage, GuardrailStatus, Severity
from guardrail_utils._result_helpers import detection_result, highest_score


class HallucinationDetectionGuardrail(BaseGuardrail):
    """Warn when output appears unsupported by supplied retrieval context."""

    name = "hallucination_detection"
    category = "security"
    stage = GuardrailStage.OUTPUT

    def __init__(self, *, min_confidence: float = 0.55, llm_detector=None, enabled: bool = True) -> None:
        """Configure support matching and optional semantic hallucination review."""
        super().__init__(enabled=enabled)
        self.min_confidence = min_confidence
        self.llm_detector = llm_detector

    def _evaluate(self, context: GuardrailContext) -> GuardrailResult:
        """Combine retrieval heuristics, citation checks, and optional LLM review."""
        detections: list[Detection] = []
        unsupported = self._unsupported_claims(context.text, context.retrieval_context)
        if unsupported:
            detections.append(Detection(
                name="unsupported_claims",
                matched=True,
                score=min(1.0, 0.35 + len(unsupported) * 0.1),
                severity=Severity.MEDIUM,
                reason="Output contains claims not directly supported by retrieval context.",
                evidence=unsupported[:5],
            ))
        if context.citations and not self._citations_appear(context.text, context.citations):
            detections.append(Detection(name="citation_mismatch", matched=True, score=0.6, severity=Severity.MEDIUM, reason="Provided citations were not referenced in the output."))
        if self.llm_detector is not None:
            llm_detection = self.llm_detector.analyze(
                context.text,
                "Score hallucination risk. Consider unsupported facts, fabricated citations, and overconfident claims.",
                name="llm_hallucination_detection",
            )
            if llm_detection.matched:
                detections.append(llm_detection)
        if not detections:
            return GuardrailResult.pass_(self.name, self.category)
        score = highest_score(detections)
        return detection_result(
            guardrail_name=self.name,
            category=self.category,
            status=GuardrailStatus.WARNED,
            action=Action.WARN,
            reason="Hallucination risk detected.",
            original_text=context.text,
            detections=detections,
            metadata={"confidence": round(1 - score, 2)},
        )

    def _unsupported_claims(self, text: str, retrieval_context: list[str]) -> list[str]:
        """Return long factual-looking sentences weakly supported by context."""
        claims = [s.strip() for s in re.split(r"(?<=[.!?])\s+", text or "") if len(s.split()) >= 8]
        if not retrieval_context:
            risky = [claim for claim in claims if re.search(r"\b(always|never|guaranteed|studies show|according to|as of)\b", claim, re.I)]
            return risky
        corpus = " ".join(retrieval_context).lower()
        unsupported = []
        for claim in claims:
            keywords = [w.lower() for w in re.findall(r"\b[A-Za-z][A-Za-z0-9-]{4,}\b", claim)]
            if keywords and sum(1 for word in keywords if word in corpus) / len(keywords) < self.min_confidence:
                unsupported.append(claim)
        return unsupported

    def _citations_appear(self, text: str, citations: list[str]) -> bool:
        """Check whether any declared citation appears in the response text."""
        lowered = text.lower()
        return any(citation.lower() in lowered for citation in citations)
