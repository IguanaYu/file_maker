"""将报告渲染为便于检视的纯文本。"""
from __future__ import annotations

from typing import List

from models import ReportDocument

from .base import ReportExporter


class PlainTextExporter(ReportExporter):
    """输出包含块编号、正文与表格的纯文本。"""

    def export(self, document: ReportDocument) -> str:
        lines: List[str] = [f"报告模板: {document.template_id}", ""]
        for index, result in enumerate(document.results, start=1):
            lines.append(f"[{index}] 块 ID: {result.block_id}")
            if result.content:
                lines.append(result.content)
            if result.table_data:
                lines.append("表格数据:")
                for row in result.table_data:
                    row_repr = ", ".join(f"{column}: {value}" for column, value in row.items())
                    lines.append(f"  - {row_repr}")
            lines.append("")
        return "\n".join(lines).strip()
