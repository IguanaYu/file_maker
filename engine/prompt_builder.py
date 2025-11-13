"""构建提交给 LLM 的指令提示。"""
from __future__ import annotations

import json
from textwrap import dedent
from typing import Dict, List

from models import BlockType, TemplateBlock

from .data_access import resolve_bindings
from prompt_tokens import (
    CONSTRAINTS_END,
    CONSTRAINTS_START,
    CONTEXT_END,
    CONTEXT_START,
    METADATA_END,
    METADATA_START,
)


def build_prompt_for_block(block: TemplateBlock, context_data: Dict[str, object]) -> str:
    """针对指定模板块构造一段 LLM 指令。"""

    resolved_data = resolve_bindings(context_data, block.data_bindings)
    data_json = json.dumps(resolved_data, ensure_ascii=False, indent=2)
    constraint_json = (
        json.dumps(block.constraints, ensure_ascii=False, indent=2) if block.constraints else "{}"
    )
    metadata_json = json.dumps(
        {
            "block_id": block.block_id,
            "block_type": block.block_type.value,
            "template_description": block.template_description,
        },
        ensure_ascii=False,
        indent=2,
    )

    guidelines: List[str]
    if block.block_type == BlockType.TITLE:
        guidelines = [
            "不要修改设备名称、年份、地点等核心事实。",
            "保持正式、专业、简洁的语气，不使用标点装饰。",
            "只输出最终标题文本，不添加解释或额外符号。",
        ]
    elif block.block_type == BlockType.SECTION_CONTENT:
        guidelines = [
            "完整覆盖模板说明中列出的要点。",
            "结合业务数据撰写 1-2 个自然段，文字客观严谨。",
            "严禁编造缺失的信息，若无数据则保持沉默。",
            "不使用项目符号、小标题或与正文无关的说明。",
        ]
    else:
        raise ValueError(f"暂不支持的块类型: {block.block_type}")

    guidelines_text = "\n".join(f"{index}. {text}" for index, text in enumerate(guidelines, start=1))

    prompt = dedent(
        f"""
        你是一名负责撰写检验 / 产品报告的专业写作者，请根据以下信息输出中文内容。

        元数据:
        {METADATA_START}
        {metadata_json}
        {METADATA_END}

        业务数据:
        {CONTEXT_START}
        {data_json}
        {CONTEXT_END}

        约束条件:
        {CONSTRAINTS_START}
        {constraint_json}
        {CONSTRAINTS_END}

        写作要求:
        {guidelines_text}
        """
    ).strip()

    return prompt
