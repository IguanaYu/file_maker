"""LLM 客户端的抽象基类。"""
from __future__ import annotations

from abc import ABC, abstractmethod


class LLMClient(ABC):
    """负责根据 Prompt 生成文本的客户端接口。"""

    @abstractmethod
    def generate_text(self, prompt: str) -> str:
        """根据 Prompt 返回生成结果。"""

        raise NotImplementedError
