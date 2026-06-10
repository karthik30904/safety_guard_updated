"""Configuration settings for guardrail policy behavior."""

from __future__ import annotations

import json
from dataclasses import dataclass, field
from pathlib import Path
from typing import Any


@dataclass(slots=True)
class GuardrailSettings:
    """Runtime settings that keep policy thresholds explicit and portable."""

    fail_fast: bool = True
    redact_pii: bool = True
    enable_llm_guardrails: bool = True
    hallucination_min_confidence: float = 0.55
    warn_threshold: float = 0.35
    block_threshold: float = 0.75
    max_input_chars: int = 12000
    max_output_chars: int = 20000
    blocked_response: str = "Request blocked by guardrail policy."
    enabled_guardrails: set[str] = field(default_factory=set)
    disabled_guardrails: set[str] = field(default_factory=set)

    @classmethod
    def from_file(cls, path: str | Path) -> "GuardrailSettings":
        """Load policy settings from a JSON or simple YAML file."""
        config_path = Path(path)
        data = _load_mapping(config_path)
        allowed_fields = set(cls.__dataclass_fields__)
        normalized: dict[str, Any] = {}
        for key, value in data.items():
            if key not in allowed_fields:
                continue
            if key in {"enabled_guardrails", "disabled_guardrails"}:
                normalized[key] = set(value or [])
            else:
                normalized[key] = value
        return cls(**normalized)


DEFAULT_SETTINGS = GuardrailSettings()


def _load_mapping(path: Path) -> dict[str, Any]:
    """Load a mapping from JSON, PyYAML, or the built-in tiny YAML parser."""
    raw = path.read_text(encoding="utf-8")
    if path.suffix.lower() == ".json":
        payload = json.loads(raw)
    else:
        try:
            import yaml  # type: ignore[import-untyped]
        except ImportError:
            payload = _parse_minimal_yaml(raw)
        else:
            payload = yaml.safe_load(raw) or {}
    if not isinstance(payload, dict):
        raise ValueError(f"Policy config must be a mapping: {path}")
    return payload


def _parse_minimal_yaml(raw: str) -> dict[str, Any]:
    """Tiny YAML fallback for common key/value and list policy files."""
    data: dict[str, Any] = {}
    current_key: str | None = None
    for line in raw.splitlines():
        stripped = line.strip()
        if not stripped or stripped.startswith("#"):
            continue
        if stripped.startswith("-") and current_key:
            data.setdefault(current_key, []).append(stripped[1:].strip())
            continue
        if ":" not in stripped:
            continue
        key, value = stripped.split(":", 1)
        current_key = key.strip()
        value = value.strip()
        if value == "":
            data[current_key] = []
        elif value.lower() in {"true", "false"}:
            data[current_key] = value.lower() == "true"
        else:
            try:
                data[current_key] = int(value)
            except ValueError:
                try:
                    data[current_key] = float(value)
                except ValueError:
                    data[current_key] = value.strip('"')
    return data
