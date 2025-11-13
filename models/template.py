"""描述报告模板结构的数据模型。"""
from __future__ import annotations

from dataclasses import dataclass, field
from typing import Any, Dict, List, Optional

from .enums import BlockType, GenerationStrategy


@dataclass(slots=True)
class TemplateBlock:
    """定义模板中的单个块。"""

    block_id: str
    block_type: BlockType
    template_description: str
    generation_strategy: GenerationStrategy
    data_bindings: Dict[str, str] = field(default_factory=dict)
    constraints: Dict[str, str] = field(default_factory=dict)
    template_text: Optional[str] = None
    table_columns: Optional[List[Dict[str, Any]]] = None
    row_data_source: Optional[str] = None


@dataclass(slots=True)
class ReportTemplate:
    """完整报告模板的配置。"""

    template_id: str
    name: str
    blocks: List[TemplateBlock]
