"""Abstract base class describing an LLM client interface."""
from __future__ import annotations

from abc import ABC, abstractmethod


class LLMClient(ABC):
    """Client capable of generating text from prompts."""

    @abstractmethod
    def generate_text(self, prompt: str) -> str:
        """Generate text according to the provided prompt."""

        raise NotImplementedError
