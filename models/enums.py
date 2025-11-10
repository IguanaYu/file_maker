"""Enumerations used across the report generation system."""
from __future__ import annotations

from enum import Enum


class BlockType(str, Enum):
    """Types of blocks that compose a report template."""

    TITLE = "TITLE"
    SECTION_CONTENT = "SECTION_CONTENT"
    TABLE = "TABLE"


class GenerationStrategy(str, Enum):
    """Strategies describing how block content should be produced."""

    FIXED = "FIXED"
    TEMPLATE_FILL = "TEMPLATE_FILL"
    LLM = "LLM"
