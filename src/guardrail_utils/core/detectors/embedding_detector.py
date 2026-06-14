"""Lightweight embedding-like detector for example similarity checks."""

from __future__ import annotations

import math
from collections import Counter

from guardrail_utils.models.schemas import Detection, Severity


class EmbeddingDetector:
    """Lightweight semantic adapter placeholder using token cosine similarity.

    Production users can replace ``embed`` with a real embedding provider without
    changing guardrail interfaces.
    """

    def __init__(self, unsafe_examples: dict[str, list[str]] | None = None) -> None:
        """Store example groups without requiring an external embedding service."""
        self.unsafe_examples = unsafe_examples or {}

    def detect(self, text: str, *, threshold: float = 0.72) -> list[Detection]:
        """Return detections when token cosine similarity crosses threshold."""
        detections: list[Detection] = []
        text_vec = self.embed(text)
        for name, examples in self.unsafe_examples.items():
            best = max((self._cosine(text_vec, self.embed(example)) for example in examples), default=0.0)
            if best >= threshold:
                detections.append(
                    Detection(
                        name=name,
                        matched=True,
                        score=best,
                        severity=Severity.MEDIUM,
                        reason="Semantic similarity to configured unsafe example.",
                    )
                )
        return detections

    def embed(self, text: str) -> Counter[str]:
        """Represent text as token counts so the detector stays dependency-free."""
        return Counter((text or "").lower().split())

    def _cosine(self, left: Counter[str], right: Counter[str]) -> float:
        """Compute cosine similarity between sparse token-count vectors."""
        common = set(left) & set(right)
        numerator = sum(left[t] * right[t] for t in common)
        left_norm = math.sqrt(sum(v * v for v in left.values()))
        right_norm = math.sqrt(sum(v * v for v in right.values()))
        if not left_norm or not right_norm:
            return 0.0
        return numerator / (left_norm * right_norm)
