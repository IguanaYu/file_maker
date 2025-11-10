"""Utilities for constructing prompts used to query LLMs."""
from __future__ import annotations

import json
from textwrap import dedent
from typing import Dict

from models import BlockType, TemplateBlock

from .data_access import resolve_bindings


def build_prompt_for_block(block: TemplateBlock, context_data: Dict[str, object]) -> str:
    """Construct an instruction prompt for the provided block.

    Parameters
    ----------
    block:
        The template block currently being generated.
    context_data:
        Business data dictionary made available to the prompt.
    """

    resolved_data = resolve_bindings(context_data, block.data_bindings)
    constraint_json = json.dumps(block.constraints, ensure_ascii=False, indent=2) if block.constraints else "{}"
    data_json = json.dumps(resolved_data, ensure_ascii=False, indent=2)

    if block.block_type == BlockType.TITLE:
        return dedent(
            f"""
            你是一名负责润色检验报告标题的专业写作者。
            模板说明: {block.template_description}
            已知业务数据 (不要修改其中的关键事实):
            {data_json}
            约束条件:
            {constraint_json}

            请在不更改核心信息（例如设备名称、年份、地点等）的前提下，对标题进行轻微润色。
            保持正式、专业的语气，并确保输出只包含最终标题文本，不要添加任何额外说明。
            """
        ).strip()

    if block.block_type == BlockType.SECTION_CONTENT:
        return dedent(
            f"""
            你是一名负责撰写检验报告章节的专业写作者。
            模板说明: {block.template_description}
            已知业务数据:
            {data_json}
            约束条件:
            {constraint_json}

            请根据上述资料撰写一段正式、准确的报告正文。严格遵循以下要求：
            1. 覆盖模板说明中提到的要点。
            2. 使用正式、客观的语言。
            3. 不要编造不存在的标准或数据，若资料中没有的信息请保持沉默。
            4. 输出为连续的自然段文本，不要使用项目符号或额外标题。
            """
        ).strip()

    raise ValueError(f"Prompt builder does not support block type: {block.block_type}")
