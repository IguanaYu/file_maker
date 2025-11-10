"""Dummy LLM client useful for local development and testing."""
from __future__ import annotations

from typing import Final

from .base import LLMClient


class DummyLLMClient(LLMClient):
    """Return predictable responses without performing network calls."""

    PREFIX: Final[str] = "[DUMMY LLM OUTPUT]\n"

    def generate_text(self, prompt: str) -> str:
        """Echo the prompt with a prefix to simulate generation."""

        return f"{self.PREFIX}{prompt.strip()}"
