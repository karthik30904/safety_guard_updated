# Ethical Guardrails

This folder contains moderation, toxicity, bias, and fairness checks.

## Files

- `toxicity_detection.py` catches harassment, profanity, hate, and violent toxic language using deterministic rules plus optional LLM analysis.
- `moderation.py` blocks dangerous self-harm, weapons, and cyber-abuse requests.
- `bias_detection.py` detects protected-class generalizations and stereotypes.
- `fairness_detection.py` identifies unfair or exclusionary treatment signals.

## Flow

Ethical guardrails can run on both user input and model output. Deterministic checks execute first; semantic LLM checks can then add context-sensitive classification.

## Extension Points

Use this folder for policy categories that are mostly about harm, fairness, and responsible AI behavior. Keep rule names specific so downstream logs and dashboards remain useful.
