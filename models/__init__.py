"""数据模型的集中导出入口。"""
from .enums import BlockType, GenerationStrategy
from .report import ReportBlockResult, ReportDocument
from .template import ReportTemplate, TemplateBlock

__all__ = [
    "BlockType",
    "GenerationStrategy",
    "ReportBlockResult",
    "ReportDocument",
    "ReportTemplate",
    "TemplateBlock",
]
