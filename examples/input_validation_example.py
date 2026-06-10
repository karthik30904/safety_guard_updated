"""Run input validation guardrails against a simple prompt."""

from __future__ import annotations

import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1] / "src"))

from guardrail_utils import GuardrailEngine


def main() -> None:
    """Print the input-validation decision for a normalized prompt."""
    engine = GuardrailEngine()
    engine.only("input_validation")
    result = engine.validate_input("   Hello,\n\nplease summarize this.   ")
    print(result.summary())
    print(result.final_text)


if __name__ == "__main__":
    main()
