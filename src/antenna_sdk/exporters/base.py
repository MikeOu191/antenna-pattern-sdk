"""Exporter interface — Open/Closed Principle."""
from abc import ABC, abstractmethod
from pathlib import Path

from ..models import AntennaMeasurement


class BaseExporter(ABC):
    """Abstract base class for all data exporters."""

    @abstractmethod
    def export(self, data: AntennaMeasurement, output_path: Path) -> Path:
        """
        Persist `data` to `output_path`.

        Args:
            data: The analyzed antenna measurement data.
            output_path: The target file path to save the exported data.

        Returns:
            The path to the successfully written file.
        """
        raise NotImplementedError("Subclasses must implement the export method.")