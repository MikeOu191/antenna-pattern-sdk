"""Domain-specific exceptions for the Antenna Pattern SDK."""


class AntennaSDKError(Exception):
    """Base exception class for all SDK errors."""


class EncodingDetectionError(AntennaSDKError):
    """Raised when no supported encoding can decode the CSV file."""


class CSVFormatError(AntennaSDKError):
    """Raised when the CSV file is malformed or unreadable."""


class BlockNotFoundError(AntennaSDKError):
    """Raised when required keyword blocks (Theta/Phi/Total/All) are missing."""