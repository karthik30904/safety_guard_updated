"""Configuration exports (shim to new core.config location)."""

from guardrail_utils.core.config import DEFAULT_SETTINGS, GuardrailSettings

__all__ = ["DEFAULT_SETTINGS", "GuardrailSettings"]
