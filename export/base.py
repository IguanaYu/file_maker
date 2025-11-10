"""Abstract interfaces for exporting generated reports."""
from __future__ import annotations

from abc import ABC, abstractmethod

from models import ReportDocument


class ReportExporter(ABC):
    """Convert report documents into serialized representations."""

    @abstractmethod
    def export(self, document: ReportDocument) -> str:
        """Return a serialized representation of the report document."""

        raise NotImplementedError
