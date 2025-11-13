"""对接阿里云百炼 API 的 LLM 客户端实现。"""
from __future__ import annotations

import json
from dataclasses import dataclass
from typing import Any, Dict, Optional
from urllib import error, request

from .base import LLMClient


@dataclass(slots=True)
class BailianConfig:
    """调用百炼 API 所需的配置项。"""

    api_key: str
    endpoint: str
    model: str
    timeout: Optional[float] = 30.0


class BailianLLMClient(LLMClient):
    """通过 HTTPS 与百炼 API 通信的客户端。"""

    def __init__(self, config: BailianConfig) -> None:
        self._config = config
        self._opener = request.build_opener()

    def generate_text(self, prompt: str) -> str:
        """向百炼 API 发送 Prompt 并返回生成结果。"""

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
            message = f"百炼 API 请求失败: {exc.code} {exc.reason} - {detail}"
            raise RuntimeError(message) from exc
        except error.URLError as exc:  # pragma: no cover - network I/O
            raise RuntimeError(f"百炼 API 请求错误: {exc.reason}") from exc

        data = json.loads(response_body)
        text = self._extract_text(data)
        if not text:
            raise RuntimeError(f"百炼 API 响应中未包含文本结果: {data!r}")
        return text.strip()

    @staticmethod
    def _extract_text(payload: Dict[str, Any]) -> Optional[str]:
        """从百炼响应中提取文本字段。"""

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

        # 兼容形如 {"text": "..."} 的极简结构。
        if isinstance(payload.get("text"), str):
            return payload["text"]

        return None
