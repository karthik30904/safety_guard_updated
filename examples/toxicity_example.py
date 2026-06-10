"""Demonstrate toxicity detection."""

from __future__ import annotations

import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1] / "src"))

from guardrail_utils import GuardrailEngine


def main() -> None:
    """Print triggered guardrails for toxic language."""
    engine = GuardrailEngine()
    engine.only("toxicity_detection")
    result = engine.validate_input("That answer is stupid.")
    print(result.summary())
    print(result.triggered_guardrails)


if __name__ == "__main__":
    main()
