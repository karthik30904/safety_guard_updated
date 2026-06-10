"""Coverage for LLM factory, logging helpers, and runnable examples."""

from __future__ import annotations

import importlib.util
import runpy
from pathlib import Path

import pytest

from guardrail_utils.llm.base_client import BaseLLMClient
from guardrail_utils.llm.factory import LLMFactory
from guardrail_utils.logging.logger import get_logger, log_policy_event


def test_factory_rejects_unknown_provider() -> None:
    """Unknown providers should fail with a clear ValueError."""
    with pytest.raises(ValueError):
        LLMFactory.create("unknown")


def test_base_client_requires_generate() -> None:
    """Base client should enforce implementation of provider generation."""
    with pytest.raises(TypeError):
        BaseLLMClient(model="demo")


def test_logging_helpers_emit(capsys: pytest.CaptureFixture[str]) -> None:
    """Central logging helpers should emit standard log records."""
    get_logger("guardrail_utils.policy")
    log_policy_event("test_event", action="allow")
    assert "test_event" in capsys.readouterr().out


@pytest.mark.parametrize(
    "example_name",
    [
        "input_validation_example.py",
        "output_validation_example.py",
        "prompt_injection_example.py",
        "jailbreak_example.py",
        "toxicity_example.py",
        "llm_guardrail_example.py",
    ],
)
def test_examples_run(example_name: str, capsys: pytest.CaptureFixture[str]) -> None:
    """Examples should execute as standalone scripts without credentials."""
    examples_dir = Path(__file__).resolve().parents[1] / "examples"
    runpy.run_path(str(examples_dir / example_name), run_name="__main__")
    assert capsys.readouterr().out


def test_chainlit_demo_imports_without_chainlit() -> None:
    """The Chainlit demo should import even when Chainlit is not installed."""
    examples_dir = Path(__file__).resolve().parents[1] / "examples"
    spec = importlib.util.spec_from_file_location("chainlit_demo", examples_dir / "chainlit_demo.py")
    assert spec is not None
    module = importlib.util.module_from_spec(spec)
    assert spec.loader is not None
    spec.loader.exec_module(module)
    assert hasattr(module, "main")
