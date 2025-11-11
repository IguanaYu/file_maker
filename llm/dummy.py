"""Dummy LLM client useful for local development and testing."""
from __future__ import annotations

import json
from typing import Any, Dict, Final

from prompt_tokens import (
    CONSTRAINTS_END,
    CONSTRAINTS_START,
    CONTEXT_END,
    CONTEXT_START,
    METADATA_END,
    METADATA_START,
)

from .base import LLMClient


class DummyLLMClient(LLMClient):
    """Return deterministic yet human-like responses without network calls."""

    _FALLBACK_PREFIX: Final[str] = "[DUMMY LLM OUTPUT]"

    def generate_text(self, prompt: str) -> str:
        """Generate lightweight Chinese text for supported block types."""

        metadata = self._extract_json(prompt, METADATA_START, METADATA_END)
        context = self._extract_json(prompt, CONTEXT_START, CONTEXT_END)
        constraints = self._extract_json(prompt, CONSTRAINTS_START, CONSTRAINTS_END)

        block_type = ""
        if isinstance(metadata, dict):
            block_type = metadata.get("block_type", "")

        if block_type == "TITLE":
            return self._render_title(context)

        if block_type == "SECTION_CONTENT":
            description = ""
            if isinstance(metadata, dict):
                description = metadata.get("template_description", "")
            return self._render_section(context, constraints, description)

        return f"{self._FALLBACK_PREFIX} {prompt.strip()}"

    @staticmethod
    def _extract_json(prompt: str, start_token: str, end_token: str) -> Dict[str, Any]:
        start_index = prompt.find(start_token)
        end_index = prompt.find(end_token)
        if start_index == -1 or end_index == -1 or end_index <= start_index:
            return {}
        json_chunk = prompt[start_index + len(start_token) : end_index].strip()
        if not json_chunk:
            return {}
        try:
            return json.loads(json_chunk)
        except json.JSONDecodeError:
            return {}

    @staticmethod
    def _render_title(context: Dict[str, Any]) -> str:
        device_name = context.get("device_name") or context.get("device_type") or "设备"
        inspection_year = context.get("inspection_year")

        if inspection_year and device_name:
            return f"{inspection_year}年{device_name}检验报告"

        if device_name:
            return f"{device_name}检验报告"

        return "年度检验报告"

    @staticmethod
    def _render_section(
        context: Dict[str, Any], constraints: Dict[str, Any], description: str
    ) -> str:
        device_name = context.get("device_name") or "该设备"
        device_type = context.get("device_type")
        inspection_year = context.get("inspection_year")
        usage_summary = context.get("usage_summary")

        device_label = device_name
        if device_type:
            device_label = f"{device_name}（{device_type}）"

        sentences = []
        if inspection_year:
            sentences.append(
                f"{inspection_year}年，{device_label}保持受控运行状态，整体性能稳定可靠。"
            )
        else:
            sentences.append(f"{device_label}保持受控运行状态，整体性能稳定可靠。")

        if usage_summary:
            sentences.append(usage_summary.rstrip("。") + "。")

        if description:
            sentences.append(f"本次检验聚焦于：{description.strip('。')}。")
        else:
            sentences.append("本次检验以运行安全、性能稳定及维护执行情况为重点。")

        if constraints.get("max_words"):
            sentences.append("综合分析显示，该设备可持续支撑后续生产需求，建议保持既定维护频次。")

        return "".join(sentences)
