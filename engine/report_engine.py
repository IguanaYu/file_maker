"""结合模板、数据与 LLM 生成报告的核心引擎。"""
from __future__ import annotations

from typing import Any, Dict, List

from llm import LLMClient
from models import (
    BlockType,
    GenerationStrategy,
    ReportBlockResult,
    ReportDocument,
    ReportTemplate,
    TemplateBlock,
)

from .data_access import resolve_bindings, resolve_data_path
from .prompt_builder import build_prompt_for_block


class ReportEngine:
    """负责根据模板、业务数据与 LLM 生成完整报告。"""

    def __init__(self, llm_client: LLMClient) -> None:
        self._llm_client = llm_client

    def generate(self, template: ReportTemplate, context_data: Dict[str, Any]) -> ReportDocument:
        """按照模板定义依次生成各个块。"""

        document = ReportDocument(template_id=template.template_id)
        for block in template.blocks:
            if block.block_type == BlockType.TABLE:
                table_data = self._generate_table(block, context_data)
                document.add_result(ReportBlockResult(block_id=block.block_id, table_data=table_data))
                continue

            if block.block_type == BlockType.TITLE:
                content = self._generate_title(block, context_data)
                document.add_result(ReportBlockResult(block_id=block.block_id, content=content))
                continue

            if block.block_type == BlockType.SECTION_CONTENT:
                content = self._generate_section(block, context_data)
                document.add_result(ReportBlockResult(block_id=block.block_id, content=content))
                continue

            raise ValueError(f"发现不支持的块类型: {block.block_type}")

        return document

    def _generate_title(self, block: TemplateBlock, context_data: Dict[str, Any]) -> str:
        """根据配置生成标题内容。"""

        if block.generation_strategy == GenerationStrategy.FIXED:
            if not block.template_text:
                raise ValueError(f"块 {block.block_id} 使用 FIXED 策略时必须提供 template_text。")
            return block.template_text

        if block.generation_strategy == GenerationStrategy.TEMPLATE_FILL:
            if not block.template_text:
                raise ValueError(f"块 {block.block_id} 使用 TEMPLATE_FILL 策略时必须提供 template_text。")
            bindings = resolve_bindings(context_data, block.data_bindings)
            return block.template_text.format(**{k: v if v is not None else "" for k, v in bindings.items()})

        if block.generation_strategy == GenerationStrategy.LLM:
            prompt = build_prompt_for_block(block, context_data)
            return self._llm_client.generate_text(prompt)

        raise ValueError(f"标题块 {block.block_id} 使用了不支持的生成策略: {block.generation_strategy}")

    def _generate_section(self, block: TemplateBlock, context_data: Dict[str, Any]) -> str:
        """生成正文内容，通常依赖 LLM。"""

        if block.generation_strategy == GenerationStrategy.LLM:
            prompt = build_prompt_for_block(block, context_data)
            return self._llm_client.generate_text(prompt)

        if block.generation_strategy == GenerationStrategy.TEMPLATE_FILL:
            if not block.template_text:
                raise ValueError(f"块 {block.block_id} 使用 TEMPLATE_FILL 策略时必须提供 template_text。")
            bindings = resolve_bindings(context_data, block.data_bindings)
            return block.template_text.format(**{k: v if v is not None else "" for k, v in bindings.items()})

        if block.generation_strategy == GenerationStrategy.FIXED:
            if not block.template_text:
                raise ValueError(f"块 {block.block_id} 使用 FIXED 策略时必须提供 template_text。")
            return block.template_text

        raise ValueError(f"正文块 {block.block_id} 使用了不支持的生成策略: {block.generation_strategy}")

    def _generate_table(self, block: TemplateBlock, context_data: Dict[str, Any]) -> List[Dict[str, Any]]:
        """根据列配置与上下文数据构建表格行。"""

        if not block.row_data_source:
            raise ValueError(f"表格块 {block.block_id} 必须配置 row_data_source。")
        if not block.table_columns:
            raise ValueError(f"表格块 {block.block_id} 必须配置 table_columns。")

        rows = resolve_data_path(context_data, block.row_data_source)
        if not isinstance(rows, list):
            raise ValueError(f"块 {block.block_id} 的 row_data_source 必须解析为列表，当前为 {type(rows).__name__}。")

        table_rows: List[Dict[str, Any]] = []
        for row in rows:
            if not isinstance(row, dict):
                raise ValueError(f"表格块 {block.block_id} 的每行必须是字典，当前为 {type(row).__name__}。")
            rendered_row: Dict[str, Any] = {}
            for column in block.table_columns:
                header = column.get("header")
                field_name = column.get("field")
                if header is None or field_name is None:
                    raise ValueError(f"表格列定义必须包含 header 与 field 字段: {column!r}")
                value = row.get(field_name)
                unit = column.get("unit")
                rendered_row[header] = f"{value} {unit}".strip() if unit and value is not None else value
            table_rows.append(rendered_row)

        return table_rows
