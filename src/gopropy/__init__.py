"""GoPro Telemetry Parser for Python

A Python library for extracting and analyzing telemetry data from GoPro MP4 files.
"""

__version__ = "0.1.0"

from typing import Optional

from .extractor import extract_gpmf_stream
from .parser import GPMFParser
from .telemetry import GoProTelemetry
from .models import (
    ModelConfig,
    get_model_config,
    list_supported_models,
    detect_model_from_metadata,
)

__all__ = [
    "extract_gpmf_stream",
    "GPMFParser",
    "GoProTelemetry",
    "ModelConfig",
    "get_model_config",
    "list_supported_models",
    "detect_model_from_metadata",
]


def load(filepath: str, model: Optional[str] = None) -> "GoProTelemetry":
    """Load telemetry data from a GoPro MP4 file.

    Args:
        filepath: Path to the GoPro MP4 file
        model: GoPro model identifier (e.g., 'HERO10', 'HERO7_BLACK').
               If None, attempts to auto-detect from video metadata.
               Supported models: HERO5-HERO13 (Black/Session variants)

    Returns:
        GoProTelemetry object with parsed sensor data

    Example:
        >>> import gopropy
        >>> # Auto-detect model (recommended)
        >>> telemetry = gopropy.load("GOPR0001.MP4")
        >>>
        >>> # Manual model specification
        >>> telemetry = gopropy.load("GOPR0001.MP4", model="HERO10")
        >>>
        >>> # Access sensor streams
        >>> df = telemetry.to_dataframe()
        >>> accel = telemetry.get_stream("ACCL")
        >>>
        >>> # List supported models
        >>> models = gopropy.list_supported_models()
    """
    return GoProTelemetry.from_file(filepath, model=model)
