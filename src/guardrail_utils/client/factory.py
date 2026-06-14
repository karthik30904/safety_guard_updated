"""Factory for creating configured LLM clients by provider name."""

from __future__ import annotations

from typing import Any

from guardrail_utils.client.azure_openai_client import AzureOpenAIClient
from guardrail_utils.client.bedrock_client import BedrockClient
from guardrail_utils.client.base_client import BaseLLMClient
from guardrail_utils.client.openai_client import OpenAIClient


class LLMFactory:
    """Create provider clients from stable string identifiers."""

    _PROVIDERS = {
        "openai": OpenAIClient,
        "azure": AzureOpenAIClient,
        "azure_openai": AzureOpenAIClient,
        "bedrock": BedrockClient,
        "aws_bedrock": BedrockClient,
    }

    @classmethod
    def create(cls, provider: str, **kwargs: Any) -> BaseLLMClient:
        """Return an LLM client for ``openai``, ``azure_openai``, or ``bedrock``."""
        key = provider.strip().lower()
        if key not in cls._PROVIDERS:
            supported = ", ".join(sorted(cls._PROVIDERS))
            raise ValueError(f"Unsupported LLM provider '{provider}'. Supported providers: {supported}.")
        return cls._PROVIDERS[key](**kwargs)
