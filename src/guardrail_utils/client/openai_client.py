"""OpenAI chat client for semantic guardrails."""

from __future__ import annotations

from typing import Any

from guardrail_utils.client.base_client import BaseLLMClient


class OpenAIClient(BaseLLMClient):
    """Small wrapper around the official OpenAI Python SDK."""

    def __init__(self, *, model: str = "gpt-4.1-mini", api_key: str | None = None, **kwargs: Any) -> None:
        """Create an OpenAI client without importing the SDK at package import time."""
        super().__init__(model=model, **kwargs)
        try:
            from openai import OpenAI
        except ImportError as exc:
            raise ImportError("Install OpenAI support with `pip install guardrail-utils[openai]`.") from exc
        self.client = OpenAI(api_key=api_key)

    def generate(self, messages: list[dict[str, Any]]) -> str:
        """Call OpenAI chat completions and return the first message content."""
        response = self.client.chat.completions.create(
            model=self.model,
            messages=messages,
            temperature=self.temperature,
            max_tokens=self.max_tokens,
        )
        return response.choices[0].message.content or ""
