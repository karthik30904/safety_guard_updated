"""AWS Bedrock runtime client for semantic guardrails."""

from __future__ import annotations

import json
from typing import Any

from guardrail_utils.llm.base_client import BaseLLMClient


class BedrockClient(BaseLLMClient):
    """Small Bedrock Converse API wrapper."""

    def __init__(self, *, model: str = "anthropic.claude-3-haiku-20240307-v1:0", region_name: str | None = None, **kwargs: Any) -> None:
        """Create a Bedrock runtime client without requiring boto3 for all users."""
        super().__init__(model=model, **kwargs)
        try:
            import boto3
        except ImportError as exc:
            raise ImportError("Install Bedrock support with `pip install guardrail-utils[bedrock]`.") from exc
        self.client = boto3.client("bedrock-runtime", region_name=region_name)

    def generate(self, messages: list[dict[str, Any]]) -> str:
        """Call Bedrock Converse and return the first text block."""
        system = [m["content"] for m in messages if m.get("role") == "system"]
        user_messages = [
            {"role": "user" if m.get("role") != "assistant" else "assistant", "content": [{"text": str(m.get("content", ""))}]}
            for m in messages
            if m.get("role") != "system"
        ]
        response = self.client.converse(
            modelId=self.model,
            system=[{"text": "\n".join(system)}] if system else [],
            messages=user_messages,
            inferenceConfig={"temperature": self.temperature, "maxTokens": self.max_tokens},
        )
        content = response.get("output", {}).get("message", {}).get("content", [])
        if content and "text" in content[0]:
            return str(content[0]["text"])
        return json.dumps(response)
