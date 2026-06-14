"""Small dependency-free helper functions used across guardrails."""

from __future__ import annotations

import re
from hashlib import sha256


def normalize_text(text: str) -> str:
    """Normalize whitespace so downstream rules see stable input."""
    return re.sub(r"\s+", " ", text or "").strip()


def estimate_tokens(text: str) -> int:
    """Estimate token usage cheaply for telemetry and examples."""
    return max(1, len(text or "") // 4)


def stable_hash(text: str) -> str:
    """Return a short stable hash suitable for non-sensitive correlation IDs."""
    return sha256((text or "").encode("utf-8")).hexdigest()[:16]


def clamp_score(value: float) -> float:
    """Keep risk scores in the public 0..1 range."""
    return max(0.0, min(1.0, value))
