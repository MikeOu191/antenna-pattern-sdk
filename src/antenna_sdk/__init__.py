"""Antenna Pattern SDK — public API."""
from .exceptions import (
    AntennaSDKError,
    EncodingDetectionError,
    CSVFormatError,
    BlockNotFoundError,
)
from .models import BlockSlice, ParsedCSV, CutPlaneSet, AntennaMeasurement
from .parser import CSVParser
from .analyzer import PatternAnalyzer

__version__ = "0.1.0"
__all__ = [
    "CSVParser",
    "PatternAnalyzer",
    "ParsedCSV",
    "BlockSlice",
    "CutPlaneSet",
    "AntennaMeasurement",
    "AntennaSDKError",
    "EncodingDetectionError",
    "CSVFormatError",
    "BlockNotFoundError",
]