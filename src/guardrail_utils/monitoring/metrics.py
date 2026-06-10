"""In-memory metrics primitives for lightweight runtime observability."""

from __future__ import annotations

from collections import Counter
from dataclasses import dataclass, field
from time import perf_counter

from guardrail_utils.models.policy_result import PolicyResult


@dataclass
class MetricsRegistry:
    """Collect simple counters and latency samples for guardrail calls."""

    counters: Counter[str] = field(default_factory=Counter)
    latencies_ms: list[float] = field(default_factory=list)

    def record_policy_result(self, result: PolicyResult) -> None:
        """Update counters from a completed policy result."""
        self.counters["requests"] += 1
        self.counters[f"action.{result.action.value}"] += 1
        self.counters[f"status.{result.status.value}"] += 1
        for name in result.triggered_guardrails:
            self.counters[f"guardrail.{name}.triggered"] += 1
        self.latencies_ms.append(result.latency_ms)

    def snapshot(self) -> dict[str, object]:
        """Return a JSON-friendly metrics snapshot."""
        avg = sum(self.latencies_ms) / len(self.latencies_ms) if self.latencies_ms else 0.0
        return {"counters": dict(self.counters), "avg_latency_ms": round(avg, 2)}


class Timer:
    """Context manager for ad hoc latency measurements in examples/tests."""

    def __enter__(self) -> "Timer":
        """Start timing and return the timer instance."""
        self.started = perf_counter()
        self.elapsed_ms = 0.0
        return self

    def __exit__(self, *_: object) -> None:
        """Stop timing and store elapsed milliseconds."""
        self.elapsed_ms = (perf_counter() - self.started) * 1000
