# Architecture

## Package Structure

```
guardrail_utils/
├── core/                    # Core guardrail components
│   ├── config/             # Configuration and settings
│   ├── models/             # Pydantic schemas and result types
│   ├── detectors/          # Detection primitives
│   ├── policies/           # Policy resolution engines
│   └── utils/              # Utility helpers
│
├── client/                 # LLM provider clients
│   ├── base_client.py      # Abstract base class
│   ├── openai_client.py    # OpenAI implementation
│   ├── azure_openai_client.py
│   ├── bedrock_client.py   # AWS Bedrock support
│   └── factory.py          # Client factory
│
├── guardrails/             # Concrete guardrail implementations
│   ├── base.py             # BaseGuardrail abstract class
│   ├── semantic.py         # LLM-backed semantic guardrails
│   ├── ethical/            # Toxicity, bias, fairness, moderation
│   ├── security/           # PII, prompt injection, jailbreak, hallucination
│   └── technical/          # Input/output validation, performance monitoring
│
├── engine/                 # High-level orchestration
│   ├── guardrail_engine.py # Main public API
│   ├── pipeline.py         # Sequential guardrail execution
│   └── middleware.py       # Integration middleware
│
├── detectors/              # Detection implementations
│   ├── llm_detector.py     # LLM-based classification
│   ├── regex_detector.py   # Pattern matching
│   ├── heuristic_detector.py
│   └── embedding_detector.py
│
└── models/                 # Pydantic models (shims to core)
    ├── guardrail_result.py
    ├── policy_result.py
    └── schemas.py
```

## Data Flow

### 1. **Input Stage**
- User input → `GuardrailEngine.validate_input()`
- `GuardrailPipeline.run()` with `GuardrailStage.INPUT`
- Active guardrails evaluated sequentially

### 2. **Processing**
- Each guardrail:
  - Receives `GuardrailContext` (text + metadata)
  - Runs detector (heuristic, regex, embedding, or LLM)
  - Returns `GuardrailResult` (status, action, severity, detections)
- Sanitization flows forward (if `Action.REDACT` or `Action.REWRITE`)

### 3. **Policy Resolution**
- `PolicyManager.resolve()` collapses guardrail results
- Computes risk score and final action (`ALLOW`, `WARN`, `BLOCK`)
- Returns `PolicyResult` (allowed, status, final_text)

### 4. **Output Stage**
- Similar to input, but `GuardrailStage.OUTPUT`
- Used for LLM response validation

## Key Components

### `GuardrailEngine`
High-level orchestrator. Combines:
- `GuardrailPipeline` – sequential guardrail execution
- `PolicyManager` – result aggregation
- `GuardrailSettings` – configuration

```python
engine = GuardrailEngine(llm_client=client, settings=settings)
result = engine.validate_input("text")
```

### `BaseGuardrail`
Abstract class for all guardrails. Subclasses implement:
- `_evaluate()` – synchronous evaluation
- `_aevaluate()` – async evaluation
- `supports(stage)` – declare input/output/both

### Detectors
Primitive classification engines:
- **LLMDetector** – LLM-based classification with configurable rubric
- **RegexDetector** – Pattern matching (PII, SQL injection, etc.)
- **HeuristicDetector** – Rule-based heuristics
- **EmbeddingDetector** – Semantic similarity matching (planned)

### `PolicyManager`
Aggregates guardrail results into one decision:
- Evaluates triggered guardrails
- Computes risk score (via `RiskScorer`)
- Determines final action (`BLOCK`, `REDACT`, `REWRITE`, `WARN`, `ALLOW`)
- Returns `PolicyResult`

## Model Types

### `GuardrailResult`
Single guardrail evaluation outcome:
```python
GuardrailResult(
    guardrail_name="pii_detection",
    status=GuardrailStatus.MODIFIED,
    action=Action.REDACT,
    severity=Severity.HIGH,
    sanitized_text="Contact me at [REDACTED]",
    detections=[Detection(...)]
)
```

### `PolicyResult`
Aggregate policy decision:
```python
PolicyResult(
    allowed=True,
    status=GuardrailStatus.MODIFIED,
    action=Action.REDACT,
    final_text="Contact me at [REDACTED]",
    triggered_guardrails=["pii_detection"]
)
```

## Configuration Hierarchy

1. **Package defaults** – `GuardrailSettings` with sensible defaults
2. **Engine config** – overrides at `GuardrailEngine` instantiation
3. **Runtime context** – per-request metadata (`user_id`, `session_id`, etc.)

## Public API

All user-facing classes and types are exported from the root `guardrail_utils` module:

```python
from guardrail_utils import (
    GuardrailEngine,
    GuardrailResult,
    PolicyResult,
    Action,
    Severity,
    GuardrailStatus,
    SemanticPromptInjectionGuardrail,
    OpenAIClient,
)
```
