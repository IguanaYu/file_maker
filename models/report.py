"""描述生成后报告结果的数据模型。"""
from __future__ import annotations

from dataclasses import dataclass, field
from typing import Dict, List, Optional


@dataclass(slots=True)
class ReportBlockResult:
    """单个块的生成结果。"""

    block_id: str
    content: Optional[str] = None
    table_data: Optional[List[Dict[str, object]]] = None


@dataclass(slots=True)
class ReportDocument:
    """完整报告的中间表示形式。"""

    template_id: str
    results: List[ReportBlockResult] = field(default_factory=list)

    def add_result(self, result: ReportBlockResult) -> None:
        """按顺序追加块结果。"""

        self.results.append(result)
