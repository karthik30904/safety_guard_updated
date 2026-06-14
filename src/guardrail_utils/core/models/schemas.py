"""Pydantic schemas shared by guardrails, policies, and examples."""

from __future__ import annotations

from enum import Enum
from typing import Any

from pydantic import BaseModel, Field


class GuardrailStage(str, Enum):
    """Pipeline stage where a guardrail can run."""

    INPUT = "input"
    OUTPUT = "output"
    BOTH = "both"


class GuardrailStatus(str, Enum):
    """Outcome status for an individual guardrail or aggregate policy result."""

    PASSED = "passed"
    WARNED = "warned"
    BLOCKED = "blocked"
    MODIFIED = "modified"


class Severity(str, Enum):
    """Normalized severity scale used for scoring and policy decisions."""

    INFO = "info"
    LOW = "low"
    MEDIUM = "medium"
    HIGH = "high"
    CRITICAL = "critical"


class Action(str, Enum):
    """Policy action requested by a guardrail or final policy result."""

    ALLOW = "allow"
    WARN = "warn"
    BLOCK = "block"
    REDACT = "redact"
    REWRITE = "rewrite"
    ESCALATE = "escalate"


class Detection(BaseModel):
    """A single matched signal emitted by a detector."""

    name: str
    matched: bool = False
    score: float = 0.0
    severity: Severity = Severity.INFO
    reason: str = ""
    evidence: list[str] = Field(default_factory=list)
    metadata: dict[str, Any] = Field(default_factory=dict)


class GuardrailContext(BaseModel):
    """Runtime context passed to each guardrail evaluation."""

    stage: GuardrailStage
    text: str
    original_text: str | None = None
    user_id: str | None = None
    session_id: str | None = None
    retrieval_context: list[str] = Field(default_factory=list)
    citations: list[str] = Field(default_factory=list)
    metadata: dict[str, Any] = Field(default_factory=dict)

    def fork(self, *, text: str | None = None, stage: GuardrailStage | None = None) -> "GuardrailContext":
        """Return a copied context when prior guardrails sanitize the text."""
        data = self.model_dump()
        if text is not None:
            data["text"] = text
        if stage is not None:
            data["stage"] = stage
        return GuardrailContext(**data)
