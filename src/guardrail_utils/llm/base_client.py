"""Base client contract for LLM providers.

Guardrails only need a tiny chat-classification surface. Keeping this contract
small makes the package plug-and-play across agents, RAG stacks, and workflow
engines without coupling the core runtime to any one provider SDK.
"""

from __future__ import annotations

import asyncio
from abc import ABC, abstractmethod
from typing import Any


class BaseLLMClient(ABC):
    """Provider-neutral chat client used by ``LLMDetector``."""

    def __init__(self, *, model: str, temperature: float = 0.0, max_tokens: int = 300, **kwargs: Any) -> None:
        """Store common generation settings shared by classifier clients."""
        self.model = model
        self.temperature = temperature
        self.max_tokens = max_tokens
        self.options = kwargs

    @abstractmethod
    def generate(self, messages: list[dict[str, Any]]) -> str:
        """Return the assistant text for a list of chat-style messages."""

    async def agenerate(self, messages: list[dict[str, Any]]) -> str:
        """Default async bridge for SDKs that only expose sync calls."""
        return await asyncio.to_thread(self.generate, messages)
