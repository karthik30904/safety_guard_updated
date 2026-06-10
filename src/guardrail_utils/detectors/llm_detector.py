"""LLM-backed classification adapter used by semantic guardrails."""

from __future__ import annotations

import asyncio
import json
from typing import Any, Protocol

from guardrail_utils.logging.logger import log_exception, log_policy_event
from guardrail_utils.models.schemas import Detection, Severity
from guardrail_utils.utils.helpers import clamp_score


class LLMClient(Protocol):
    """Minimal chat-client protocol accepted by ``LLMDetector``."""

    def generate(self, messages: list[dict[str, Any]]) -> str:
        """Return a JSON classification string for the supplied chat messages."""
        ...

    async def agenerate(self, messages: list[dict[str, Any]]) -> str:
        """Asynchronously return a JSON classification string."""
        ...


class LLMDetector:
    """Adapter around any chat-style client. Falls back cleanly when no client is supplied."""

    def __init__(self, client: LLMClient | None = None, *, enabled: bool = True) -> None:
        self.client = client
        self.enabled = enabled

    def analyze(self, text: str, rubric: str, *, name: str) -> Detection:
        if not self.enabled or self.client is None:
            log_policy_event("llm_guardrail_skipped", name=name, enabled=self.enabled, has_client=self.client is not None)
            return Detection(name=name, matched=False, reason="LLM detector disabled or no client configured.")
        try:
            raw = self.client.generate(self._messages(text, rubric))
        except Exception as exc:
            log_exception("llm_guardrail_failed", exc, name=name)
            return Detection(
                name=name,
                matched=False,
                reason="LLM detector failed during classification.",
                metadata={"detector": "llm", "client_error": True},
            )
        return self._parse(raw, name)

    async def aanalyze(self, text: str, rubric: str, *, name: str) -> Detection:
        if not self.enabled or self.client is None:
            log_policy_event("llm_guardrail_skipped", name=name, enabled=self.enabled, has_client=self.client is not None)
            return Detection(name=name, matched=False, reason="LLM detector disabled or no client configured.")
        try:
            if hasattr(self.client, "agenerate"):
                raw = await self.client.agenerate(self._messages(text, rubric))
            else:
                raw = await asyncio.to_thread(self.client.generate, self._messages(text, rubric))
        except Exception as exc:
            log_exception("llm_guardrail_failed", exc, name=name)
            return Detection(
                name=name,
                matched=False,
                reason="LLM detector failed during classification.",
                metadata={"detector": "llm", "client_error": True},
            )
        return self._parse(raw, name)

    def _messages(self, text: str, rubric: str) -> list[dict[str, str]]:
        """Build a narrow classifier prompt to keep provider clients reusable."""
        return [
            {
                "role": "system",
                "content": (
                    "You are a strict AI safety classifier. Return only JSON with keys: "
                    "matched, score, severity, reason, evidence."
                ),
            },
            {"role": "user", "content": f"Rubric:\n{rubric}\n\nText:\n{text}"},
        ]

    def _parse(self, raw: str, name: str) -> Detection:
        try:
            payload = json.loads(raw)
            severity = Severity(str(payload.get("severity", "info")).lower())
            detection = Detection(
                name=name,
                matched=bool(payload.get("matched", False)),
                score=clamp_score(float(payload.get("score", 0.0))),
                severity=severity,
                reason=str(payload.get("reason", "")),
                evidence=[str(item) for item in payload.get("evidence", [])][:5],
                metadata={"detector": "llm"},
            )
            log_policy_event(
                "llm_guardrail_decision",
                name=name,
                matched=detection.matched,
                severity=detection.severity.value,
                score=detection.score,
            )
            return detection
        except Exception:
            log_policy_event("llm_guardrail_parse_error", name=name)
            return Detection(
                name=name,
                matched=False,
                score=0.0,
                severity=Severity.INFO,
                reason="LLM detector returned unparsable output.",
                evidence=[raw[:200]],
                metadata={"detector": "llm", "parse_error": True},
            )
