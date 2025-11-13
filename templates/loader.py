"""从 JSON 文件加载报告模板。"""
from __future__ import annotations

import json
from pathlib import Path
from typing import Any, Dict

from models import BlockType, GenerationStrategy, ReportTemplate, TemplateBlock


def load_report_template_from_json(path: str | Path) -> ReportTemplate:
    """读取并解析指定路径的模板定义。"""

    path = Path(path)
    data: Dict[str, Any] = json.loads(path.read_text(encoding="utf-8"))

    blocks = []
    for block_data in data.get("blocks", []):
        block = TemplateBlock(
            block_id=block_data["block_id"],
            block_type=BlockType(block_data["block_type"]),
            template_description=block_data.get("template_description", ""),
            generation_strategy=GenerationStrategy(block_data.get("generation_strategy", "LLM")),
            data_bindings=block_data.get("data_bindings", {}),
            constraints=block_data.get("constraints", {}),
            template_text=block_data.get("template_text"),
            table_columns=block_data.get("table_columns"),
            row_data_source=block_data.get("row_data_source"),
        )
        blocks.append(block)

    return ReportTemplate(
        template_id=data.get("template_id", path.stem),
        name=data.get("name", path.stem),
        blocks=blocks,
    )
