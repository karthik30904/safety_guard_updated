"""Middleware helpers for wrapping agent callables and graph nodes."""

from __future__ import annotations

from typing import Callable

from guardrail_utils.engine.guardrail_engine import GuardrailEngine
from guardrail_utils.core.models import PolicyResult


class GuardrailMiddleware:
    """Small adapter layer around ``GuardrailEngine`` for agent frameworks."""

    def __init__(self, engine: GuardrailEngine) -> None:
        """Store the engine used by wrappers and nodes."""
        self.engine = engine

    def wrap(self, agent_call: Callable[[str], str]) -> Callable[[str], PolicyResult]:
        """Wrap a string-in/string-out callable with guardrail protection."""
        def guarded(user_input: str) -> PolicyResult:
            return self.engine.protect_agent(agent_call, user_input)

        return guarded

    def as_node(self, name: str = "guardrails") -> object:
        """Return a minimal graph-style node for state-dict workflows."""
        engine = self.engine

        class GuardrailNode:
            def __init__(self) -> None:
                self.name = name

            def run(self, state: dict[str, object]) -> dict[str, object]:
                result = engine.run_input_guardrails(str(state.get("input", "")))
                return {**state, "input": result.final_text, "guardrail_result": result}

        return GuardrailNode()
