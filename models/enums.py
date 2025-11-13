"""报告生成流程中使用的枚举类型。"""
from __future__ import annotations

from enum import Enum


class BlockType(str, Enum):
    """模板中支持的块类型。"""

    TITLE = "TITLE"
    SECTION_CONTENT = "SECTION_CONTENT"
    TABLE = "TABLE"


class GenerationStrategy(str, Enum):
    """块内容的生成策略。"""

    FIXED = "FIXED"
    TEMPLATE_FILL = "TEMPLATE_FILL"
    LLM = "LLM"
