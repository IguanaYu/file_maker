"""Data models describing templates for report generation."""
from __future__ import annotations

from dataclasses import dataclass, field
from typing import Any, Dict, List, Optional

from .enums import BlockType, GenerationStrategy


@dataclass(slots=True)
class TemplateBlock:
    """Describe an individual block inside a report template."""

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
    """Template configuration for a full report."""

    template_id: str
    name: str
    blocks: List[TemplateBlock]
