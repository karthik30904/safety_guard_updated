"""Chainlit testing demo for guardrail decisions and logs."""

from __future__ import annotations

import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1] / "src"))

from guardrail_utils import GuardrailEngine

engine = GuardrailEngine()


def _format_result(label: str, result: object) -> str:
    """Format a policy result for a compact Chainlit message."""
    summary = result.summary()
    lines = [
        f"{label}",
        f"allowed: {summary['allowed']}",
        f"action: {summary['action']}",
        f"severity: {summary['severity']}",
        f"risk_score: {result.metadata.get('risk_score')}",
        f"confidence_score: {result.metadata.get('confidence_score')}",
        f"triggered_guardrails: {', '.join(result.triggered_guardrails) or 'none'}",
    ]
    for guardrail_result in result.results:
        if guardrail_result.triggered:
            lines.append(
                f"- {guardrail_result.guardrail_name}: {guardrail_result.reason} "
                f"(score={guardrail_result.score}, action={guardrail_result.action.value})"
            )
    return "\n".join(lines)


try:
    import chainlit as cl
except ImportError:
    cl = None


if cl is not None:

    @cl.on_message
    async def on_message(message: "cl.Message") -> None:
        """Validate user input, echo a demo response, then validate output."""
        input_result = await engine.arun_input_guardrails(message.content)
        await cl.Message(content=_format_result("Input guardrails", input_result)).send()
        if not input_result.allowed:
            await cl.Message(content=input_result.final_text).send()
            return

        response = f"Demo agent received: {input_result.final_text}"
        output_result = await engine.arun_output_guardrails(response)
        await cl.Message(content=response).send()
        await cl.Message(content=_format_result("Output guardrails", output_result)).send()


def main() -> None:
    """Explain how to run the interactive Chainlit demo."""
    if cl is None:
        print("Install Chainlit support with `pip install guardrail-utils[chainlit]`.")
        return
    print("Run: chainlit run examples/chainlit_demo.py")


if __name__ == "__main__":
    main()
