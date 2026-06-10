# Security Guardrails

This folder contains guardrails for attacks, sensitive data, jailbreaks, prompt injection, and hallucination risk.

## Files

- `prompt_injection.py` combines keyword and regex detectors for instruction override, system prompt exfiltration, role smuggling, and tool abuse.
- `jailbreak_detection.py` catches known jailbreak patterns and can also use an injected LLM detector for semantic classification.
- `pii_detection.py` identifies and optionally redacts emails, phone numbers, SSNs, card-like values, and secret-like tokens.
- `hallucination_detection.py` evaluates unsupported output claims against retrieval context, citations, and optional LLM analysis.

## Flow

Input security guardrails run after basic input validation. Output security guardrails run after assistant responses are generated. Results are aggregated by the policy engine into a final action.

## Extension Points

New security detectors should reuse `RegexDetector`, `HeuristicDetector`, or `LLMDetector` when possible. For provider-specific semantic checks, use the `llm_guardrails` package and inject the detector through the engine.
