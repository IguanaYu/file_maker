"""Core engine responsible for generating reports from templates."""
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
    """Generate a report document by combining templates, data, and an LLM."""

    def __init__(self, llm_client: LLMClient) -> None:
        self._llm_client = llm_client

    def generate(self, template: ReportTemplate, context_data: Dict[str, Any]) -> ReportDocument:
        """Generate a report document according to the provided template."""

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

            raise ValueError(f"Unsupported block type encountered: {block.block_type}")

        return document

    def _generate_title(self, block: TemplateBlock, context_data: Dict[str, Any]) -> str:
        """Generate content for a title block based on its strategy."""

        if block.generation_strategy == GenerationStrategy.FIXED:
            if not block.template_text:
                raise ValueError(f"Block {block.block_id} requires template_text for FIXED strategy.")
            return block.template_text

        if block.generation_strategy == GenerationStrategy.TEMPLATE_FILL:
            if not block.template_text:
                raise ValueError(
                    f"Block {block.block_id} requires template_text for TEMPLATE_FILL strategy."
                )
            bindings = resolve_bindings(context_data, block.data_bindings)
            return block.template_text.format(**{k: v if v is not None else "" for k, v in bindings.items()})

        if block.generation_strategy == GenerationStrategy.LLM:
            prompt = build_prompt_for_block(block, context_data)
            return self._llm_client.generate_text(prompt)

        raise ValueError(f"Unsupported generation strategy for title: {block.generation_strategy}")

    def _generate_section(self, block: TemplateBlock, context_data: Dict[str, Any]) -> str:
        """Generate content for a section block, typically via an LLM."""

        if block.generation_strategy == GenerationStrategy.LLM:
            prompt = build_prompt_for_block(block, context_data)
            return self._llm_client.generate_text(prompt)

        if block.generation_strategy == GenerationStrategy.TEMPLATE_FILL:
            if not block.template_text:
                raise ValueError(
                    f"Block {block.block_id} requires template_text for TEMPLATE_FILL strategy."
                )
            bindings = resolve_bindings(context_data, block.data_bindings)
            return block.template_text.format(**{k: v if v is not None else "" for k, v in bindings.items()})

        if block.generation_strategy == GenerationStrategy.FIXED:
            if not block.template_text:
                raise ValueError(f"Block {block.block_id} requires template_text for FIXED strategy.")
            return block.template_text

        raise ValueError(f"Unsupported generation strategy for section: {block.generation_strategy}")

    def _generate_table(self, block: TemplateBlock, context_data: Dict[str, Any]) -> List[Dict[str, Any]]:
        """Construct table rows using configured columns and context data."""

        if not block.row_data_source:
            raise ValueError(f"Block {block.block_id} requires row_data_source for table generation.")
        if not block.table_columns:
            raise ValueError(f"Block {block.block_id} requires table_columns for table generation.")

        rows = resolve_data_path(context_data, block.row_data_source)
        if not isinstance(rows, list):
            raise ValueError(
                f"Row data source for block {block.block_id} must resolve to a list; got {type(rows).__name__}."
            )

        table_rows: List[Dict[str, Any]] = []
        for row in rows:
            if not isinstance(row, dict):
                raise ValueError(
                    f"Row entries for block {block.block_id} must be dictionaries; got {type(row).__name__}."
                )
            rendered_row: Dict[str, Any] = {}
            for column in block.table_columns:
                header = column.get("header")
                field_name = column.get("field")
                if header is None or field_name is None:
                    raise ValueError(
                        f"Column definitions must include 'header' and 'field' keys: {column!r}."
                    )
                value = row.get(field_name)
                unit = column.get("unit")
                rendered_row[header] = f"{value} {unit}".strip() if unit and value is not None else value
            table_rows.append(rendered_row)

        return table_rows
