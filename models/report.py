"""Models representing generated report results."""
from __future__ import annotations

from dataclasses import dataclass, field
from typing import Dict, List, Optional


@dataclass(slots=True)
class ReportBlockResult:
    """Result for a single report block once generated."""

    block_id: str
    content: Optional[str] = None
    table_data: Optional[List[Dict[str, object]]] = None


@dataclass(slots=True)
class ReportDocument:
    """Intermediate representation of a generated report."""

    template_id: str
    results: List[ReportBlockResult] = field(default_factory=list)

    def add_result(self, result: ReportBlockResult) -> None:
        """Append a block result to the document in order."""

        self.results.append(result)
