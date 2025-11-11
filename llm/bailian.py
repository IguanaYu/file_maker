"""Client implementation targeting the Bailian large language model API."""
from __future__ import annotations

import json
from dataclasses import dataclass
from typing import Any, Dict, Optional
from urllib import error, request

from .base import LLMClient


@dataclass(slots=True)
class BailianConfig:
    """Configuration values required to connect to the Bailian API."""

    api_key: str
    endpoint: str
    model: str
    timeout: Optional[float] = 30.0


class BailianLLMClient(LLMClient):
    """LLM client that communicates with the Bailian API over HTTPS."""

    def __init__(self, config: BailianConfig) -> None:
        self._config = config
        self._opener = request.build_opener()

    def generate_text(self, prompt: str) -> str:
        """Send the prompt to the Bailian API and return generated text."""

        payload = {
            "model": self._config.model,
            "input": {
                "prompt": prompt,
            },
        }
        data = json.dumps(payload, ensure_ascii=False).encode("utf-8")

        req = request.Request(
            self._config.endpoint,
            data=data,
            headers={
                "Content-Type": "application/json",
                "Authorization": f"Bearer {self._config.api_key}",
            },
            method="POST",
        )

        try:
            with self._opener.open(req, timeout=self._config.timeout) as resp:
                response_body = resp.read().decode("utf-8")
        except error.HTTPError as exc:  # pragma: no cover - network I/O
            detail = exc.read().decode("utf-8", errors="ignore")
            message = f"Bailian API request failed: {exc.code} {exc.reason} - {detail}"
            raise RuntimeError(message) from exc
        except error.URLError as exc:  # pragma: no cover - network I/O
            raise RuntimeError(f"Bailian API request error: {exc.reason}") from exc

        data = json.loads(response_body)
        text = self._extract_text(data)
        if not text:
            raise RuntimeError(f"Bailian API response did not include text output: {data!r}")
        return text.strip()

    @staticmethod
    def _extract_text(payload: Dict[str, Any]) -> Optional[str]:
        """Extract textual content from a generic Bailian response."""

        output = payload.get("output")
        if isinstance(output, dict):
            text = output.get("text")
            if isinstance(text, str) and text.strip():
                return text

            choices = output.get("choices")
            if isinstance(choices, list):
                for choice in choices:
                    if not isinstance(choice, dict):
                        continue
                    if isinstance(choice.get("text"), str):
                        return choice["text"]
                    message = choice.get("message") or choice.get("messages")
                    if isinstance(message, dict):
                        content = message.get("content")
                        if isinstance(content, str):
                            return content
                        if isinstance(content, list):
                            for item in content:
                                if isinstance(item, dict) and isinstance(item.get("text"), str):
                                    return item["text"]

        # Fallback for simplified responses (e.g., {"text": "..."}).
        if isinstance(payload.get("text"), str):
            return payload["text"]

        return None
