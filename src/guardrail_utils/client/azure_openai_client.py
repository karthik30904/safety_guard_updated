"""Azure OpenAI chat client for semantic guardrails."""

from __future__ import annotations

from typing import Any

from guardrail_utils.client.base_client import BaseLLMClient


class AzureOpenAIClient(BaseLLMClient):
    """Wrapper around Azure OpenAI chat completions."""

    def __init__(
        self,
        *,
        model: str = "gpt-4.1-mini",
        azure_endpoint: str | None = None,
        api_key: str | None = None,
        api_version: str = "2024-10-21",
        **kwargs: Any,
    ) -> None:
        """Create an Azure OpenAI client using deployment name as ``model``."""
        super().__init__(model=model, **kwargs)
        try:
            from openai import AzureOpenAI
        except ImportError as exc:
            raise ImportError("Install Azure OpenAI support with `pip install guardrail-utils[azure]`.") from exc
        self.client = AzureOpenAI(azure_endpoint=azure_endpoint, api_key=api_key, api_version=api_version)

    def generate(self, messages: list[dict[str, Any]]) -> str:
        """Call Azure OpenAI chat completions and return message content."""
        response = self.client.chat.completions.create(
            model=self.model,
            messages=messages,
            temperature=self.temperature,
            max_tokens=self.max_tokens,
        )
        return response.choices[0].message.content or ""
