"""Typed data models for structured antenna measurement data."""
from __future__ import annotations

from dataclasses import dataclass, field
from typing import Dict, List, Tuple

import numpy as np

# Type alias for a single CSV row (list of strings)
Row = List[str]

# Type alias for frequency entry: (0-based global row index, raw frequency string)
FreqEntry = Tuple[int, str]


@dataclass(frozen=True)
class BlockSlice:
    """A contiguous slice of CSV rows belonging to one keyword block."""

    data: List[Row]
    start_row: int  # 0-based index into the original CSV


@dataclass
class ParsedCSV:
    """Structured output of CSVParser (Actions 1–9)."""

    file_path: str
    encoding: str
    col_a_keywords: Dict[str, List[int]] = field(default_factory=dict)
    col_b_after_all: Dict[str, List[int]] = field(default_factory=dict)
    blocks: Dict[str, BlockSlice] = field(default_factory=dict)
    all_sub_headers: Dict[str, List[str]] = field(default_factory=dict)
    all_sub_frequencies: Dict[str, List[FreqEntry]] = field(default_factory=dict)
    block_frequencies: Dict[str, List[FreqEntry]] = field(default_factory=dict)


@dataclass
class CutPlaneSet:
    """25-point closed 2D cut planes for one frequency (Action 13)."""

    frequency: str
    H: Dict[str, np.ndarray]   # EPHI   -> {"XZ", "YZ", "XY"}
    V: Dict[str, np.ndarray]   # ETHETA -> {"XZ", "YZ", "XY"}


@dataclass
class AntennaMeasurement:
    """Final analysis result consumed by exporters."""

    file_path: str
    encoding: str
    matrices: Dict[str, Dict[str, np.ndarray]] = field(default_factory=dict)
    cut_planes: Dict[str, CutPlaneSet] = field(default_factory=dict)