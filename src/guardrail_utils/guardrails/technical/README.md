# Technical Guardrails

This folder contains deterministic checks that protect the shape, size, and operational reliability of text moving through the framework.

## Files

- `input_validation.py` normalizes user input, rejects empty prompts when configured, and blocks oversized prompts before downstream work runs.
- `output_validation.py` checks assistant responses for length and optional structured output requirements such as JSON.
- `performance_monitor.py` records operational signals that help teams notice slow or costly guardrail execution.
- `robustness_check.py` detects malformed, repeated, or suspiciously noisy text patterns.

## Flow

Technical guardrails usually run early in the pipeline. They are deterministic, cheap, and provider-independent, so they are the first layer before policy rules and semantic LLM classifiers.

## Extension Points

Add another `BaseGuardrail` implementation when a new format, protocol, schema, or runtime constraint needs to be enforced. Keep these checks fast and deterministic whenever possible.
