"""Run output validation guardrails against an invalid JSON response."""

from __future__ import annotations

import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1] / "src"))

from guardrail_utils.engine.pipeline import GuardrailPipeline
from guardrail_utils.guardrails.technical.output_validation import OutputValidationGuardrail
from guardrail_utils.models.schemas import GuardrailStage


def main() -> None:
    """Print the output-validation decision for required JSON output."""
    pipeline = GuardrailPipeline([OutputValidationGuardrail(required_format="json")])
    result = pipeline.run("not-json", GuardrailStage.OUTPUT)
    print(result.summary())


if __name__ == "__main__":
    main()
