"""报告导出器抽象基类。"""
from __future__ import annotations

from abc import ABC, abstractmethod

from models import ReportDocument


class ReportExporter(ABC):
    """负责将报告文档转换成某种可输出的格式。"""

    @abstractmethod
    def export(self, document: ReportDocument) -> str:
        """返回序列化后的报告内容。"""

        raise NotImplementedError
