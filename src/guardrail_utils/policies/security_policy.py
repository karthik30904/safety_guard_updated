"""Compatibility security policy wrapper around ``PolicyManager``."""

from __future__ import annotations

from guardrail_utils.config.settings import GuardrailSettings
from guardrail_utils.policies.policy_manager import PolicyManager


class SecurityPolicy(PolicyManager):
    """Backward-compatible specialization for security policy imports."""

    def __init__(self, settings: GuardrailSettings | None = None) -> None:
        """Initialize using the shared policy manager implementation."""
        super().__init__(settings=settings)
