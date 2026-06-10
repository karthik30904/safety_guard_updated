"""Telemetry sink built on the package logger."""

from __future__ import annotations

from guardrail_utils.logging.logger import get_logger
from guardrail_utils.models.policy_result import PolicyResult

logger = get_logger("guardrail_utils.telemetry")


class TelemetrySink:
    """Emit log-based telemetry without requiring an external backend."""

    def emit(self, event_name: str, payload: dict[str, object]) -> None:
        """Emit a named telemetry event."""
        logger.info("telemetry event=%s payload=%s", event_name, payload)

    def emit_policy_result(self, result: PolicyResult) -> None:
        """Emit the compact summary for a completed policy result."""
        self.emit("guardrail_policy_result", result.summary())
