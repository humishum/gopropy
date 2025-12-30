"""GoPro camera model configurations and metadata specifications.

This module contains model-specific configurations for different GoPro cameras,
based on the official GPMF Parser documentation:
https://github.com/gopro/gpmf-parser

Each model inherits from its predecessor and adds/removes FourCC codes
and metadata capabilities.
"""

from dataclasses import dataclass, field
from typing import Dict, List, Optional, Set
import logging

logger = logging.getLogger(__name__)


@dataclass
class ModelConfig:
    """Configuration for a specific GoPro model.

    Attributes:
        name: Internal model identifier (e.g., "HERO10_BLACK")
        display_name: Human-readable model name
        firmware_version: Minimum firmware version for this config
        release_year: Year the model was released
        axis_order: Dict mapping FourCC codes to axis label lists
        supported_fourccs: Complete set of FourCC codes this model supports
        added_fourccs: FourCC codes added in this model (vs predecessor)
        removed_fourccs: FourCC codes removed in this model
        changed_fourccs: Dict of FourCC codes with changed behavior/description
        notes: Additional notes about this model
        inherits_from: Parent model name for inheritance
    """

    name: str
    display_name: str
    firmware_version: str
    release_year: int

    # Axis ordering for multi-dimensional sensors
    axis_order: Dict[str, List[str]] = field(default_factory=dict)

    # FourCC codes supported by this model
    supported_fourccs: Set[str] = field(default_factory=set)

    # FourCC codes added in this model (relative to previous)
    added_fourccs: Set[str] = field(default_factory=set)

    # FourCC codes removed in this model
    removed_fourccs: Set[str] = field(default_factory=set)

    # FourCC codes with changed behavior
    changed_fourccs: Dict[str, str] = field(default_factory=dict)

    # Additional metadata and notes
    notes: str = ""

    # Parent model (for inheritance)
    inherits_from: Optional[str] = None


# =============================================================================
# Model Configurations (based on GPMF Parser documentation)
# =============================================================================

# Hero5 Black and Session - Base configuration
# Source: https://github.com/gopro/gpmf-parser#hero5-black-and-session
HERO5_BLACK = ModelConfig(
    name="HERO5_BLACK",
    display_name="Hero5 Black",
    firmware_version="v2.0",
    release_year=2016,
    axis_order={
        # Documented axis order: Z, X, Y for IMU sensors
        "ACCL": ["z", "x", "y"],
        "GYRO": ["z", "x", "y"],
        # GPS5 is not XYZ axes, it's: lat, lon, alt, 2D speed, 3D speed
        "GPS5": ["lat", "lon", "alt", "speed_2d", "speed_3d"],
        "WRGB": ["r", "g", "b"],
    },
    supported_fourccs={
        # Core metadata
        "DEVC",
        "DVID",
        "DVNM",
        "STRM",
        "STNM",
        "RMRK",
        "SCAL",
        "SIUN",
        "UNIT",
        "TYPE",
        "TSMP",
        "TIMO",
        "EMPT",
        # Sensor data
        "ACCL",  # 3-axis accelerometer (m/s²)
        "GYRO",  # 3-axis gyroscope (rad/s)
        "GPS5",  # GPS: lat, lon, alt, 2D speed, 3D speed
        "GPSU",  # GPS acquisition time
        "GPSF",  # GPS fix (0=no lock, 2=2D lock, 3=3D lock)
        "GPSP",  # GPS positional accuracy (DOP)
        # Camera settings
        "SHUT",  # Exposure time (s)
        "WBAL",  # White balance (Kelvin)
        "WRGB",  # White balance RGB gains
        "ISOE",  # Sensor ISO
        # Other
        "MAGN",  # Magnetometer (µT) - if present
    },
    notes="Base model with Z,X,Y axis order for accelerometer and gyroscope (documented)",
)

HERO5_SESSION = ModelConfig(
    name="HERO5_SESSION",
    display_name="Hero5 Session",
    firmware_version="v2.0",
    release_year=2016,
    axis_order={
        "ACCL": ["z", "x", "y"],
        "GYRO": ["z", "x", "y"],
    },
    supported_fourccs=HERO5_BLACK.supported_fourccs.copy(),
    notes="Same metadata structure as Hero5 Black",
)

# Hero6 Black v1.6
# Source: https://github.com/gopro/gpmf-parser#hero6-black-v16
HERO6_BLACK = ModelConfig(
    name="HERO6_BLACK",
    display_name="Hero6 Black",
    firmware_version="v1.6",
    release_year=2017,
    inherits_from="HERO5_BLACK",
    axis_order={
        # Inherits Z, X, Y from Hero5
    },
    added_fourccs={
        "FACE",  # Face detection (added but not fully documented until Hero10)
        "FCNM",  # Face name
    },
    notes="Adds early face detection support",
)

# Hero7 Black v1.8
# Source: https://github.com/gopro/gpmf-parser#hero7-black-v18
HERO7_BLACK = ModelConfig(
    name="HERO7_BLACK",
    display_name="Hero7 Black",
    firmware_version="v1.8",
    release_year=2018,
    inherits_from="HERO6_BLACK",
    axis_order={
        # Inherits Z, X, Y from Hero5
    },
    added_fourccs={
        "YAVG",  # Luma (Y) average over the frame
        "HUES",  # Hue statistics
        "UNIF",  # Image uniformity
        "SCEN",  # Scene classification (in probabilities)
        "SROT",  # Sensor Read Out Time (ms)
    },
    notes="Adds image analysis metadata: scene classification, uniformity, luma stats",
)

# Hero8 Black v1.8
# Source: https://github.com/gopro/gpmf-parser#hero8-black-v18
HERO8_BLACK = ModelConfig(
    name="HERO8_BLACK",
    display_name="Hero8 Black",
    firmware_version="v1.8",
    release_year=2019,
    inherits_from="HERO7_BLACK",
    axis_order={
        # Inherits Z, X, Y for ACCL, GYRO
        # Quaternion sensors use w, x, y, z (scalar-first, verified via data analysis)
        "CORI": ["w", "x", "y", "z"],  # Camera orientation quaternion
        "IORI": ["w", "x", "y", "z"],  # Image orientation quaternion
        "GRAV": ["x", "y", "z"],  # Gravity vector (standard x, y, z)
        "AALP": ["rms", "peak"],  # Audio levels (RMS, peak)
    },
    added_fourccs={
        "CORI",  # Camera ORIentation (quaternion)
        "IORI",  # Image ORIentation (quaternion)
        "GRAV",  # GRAVity vector
        "WNDM",  # WiND Measurement (m/s)
        "MWET",  # Microphone WET detection
        "AALP",  # Audio levels (RMS, peak)
    },
    notes="Major addition: camera orientation (CORI), image orientation (IORI), gravity vector",
)

# Hero9 Black v1.8
# Source: https://github.com/gopro/gpmf-parser#hero9-black-v18
HERO9_BLACK = ModelConfig(
    name="HERO9_BLACK",
    display_name="Hero9 Black",
    firmware_version="v1.8",
    release_year=2020,
    inherits_from="HERO8_BLACK",
    axis_order={
        # Inherits all from Hero8
        "GPS9": [
            "lat",
            "lon",
            "alt",
            "speed_2d",
            "speed_3d",
            "days",
            "secs",
            "dop",
            "fix",
        ],
    },
    added_fourccs={
        "GPS9",  # Enhanced GPS with 9 fields (vs GPS5 with 5 fields)
        "MSKP",  # Main video frame SKiP
        "LSKP",  # Low res video frame SKiP
    },
    notes="Adds GPS9 with improved precision (lat, lon, alt, 2D spd, 3D spd, days, secs, DOP, fix)",
)

# Hero10 Black v1.8
# Source: https://github.com/gopro/gpmf-parser#hero10-black-v18
HERO10_BLACK = ModelConfig(
    name="HERO10_BLACK",
    display_name="Hero10 Black",
    firmware_version="v1.8",
    release_year=2021,
    inherits_from="HERO9_BLACK",
    axis_order={
        # Inherits all from Hero9
    },
    added_fourccs={
        # Face detection v4 improvements
        "FACS",  # Face detection confidence/data
    },
    changed_fourccs={
        "FACE": "Enhanced face detection v4 with confidence, ID, boxes, smile, blink data",
    },
    notes="Enhanced face detection capabilities, 5.3K video support",
)

# Hero11 Black v1.8
# Source: https://github.com/gopro/gpmf-parser#hero11-black-v18
HERO11_BLACK = ModelConfig(
    name="HERO11_BLACK",
    display_name="Hero11 Black",
    firmware_version="v1.8",
    release_year=2022,
    inherits_from="HERO10_BLACK",
    axis_order={
        # Inherits all from Hero10
    },
    added_fourccs={
        # Add any Hero11-specific FourCC codes from docs
    },
    notes="8:7 sensor format, improved stabilization",
)

# Hero12 Black v1.8
# Source: https://github.com/gopro/gpmf-parser#hero12-black-v18
HERO12_BLACK = ModelConfig(
    name="HERO12_BLACK",
    display_name="Hero12 Black",
    firmware_version="v1.8",
    release_year=2023,
    inherits_from="HERO11_BLACK",
    axis_order={
        # Inherits all from Hero11
    },
    added_fourccs={
        # Add any Hero12-specific FourCC codes from docs
    },
    notes="HDR video, improved battery life",
)

# Hero13 Black v1.8
# Source: https://github.com/gopro/gpmf-parser#hero13-black-v18
HERO13_BLACK = ModelConfig(
    name="HERO13_BLACK",
    display_name="Hero13 Black",
    firmware_version="v1.8",
    release_year=2024,
    inherits_from="HERO12_BLACK",
    axis_order={
        # Inherits all from Hero12
    },
    added_fourccs={
        # Add any Hero13-specific FourCC codes from docs
    },
    notes="Latest model with enhanced features",
)

# Generic/Unknown model fallback
GENERIC = ModelConfig(
    name="GENERIC",
    display_name="Generic GoPro",
    firmware_version="unknown",
    release_year=2016,
    axis_order={
        # Use standard X, Y, Z ordering as fallback
        "ACCL": ["x", "y", "z"],
        "GYRO": ["x", "y", "z"],
        "CORI": ["w", "x", "y", "z"],  # Quaternions are w-first (scalar-first)
        "IORI": ["w", "x", "y", "z"],  # Quaternions are w-first (scalar-first)
        "GRAV": ["x", "y", "z"],
        "GPS5": ["lat", "lon", "alt", "speed_2d", "speed_3d"],
        "GPS9": [
            "lat",
            "lon",
            "alt",
            "speed_2d",
            "speed_3d",
            "days",
            "secs",
            "dop",
            "fix",
        ],
        "WRGB": ["r", "g", "b"],
        "AALP": ["rms", "peak"],
    },
    supported_fourccs=HERO5_BLACK.supported_fourccs.copy(),
    notes="Fallback configuration for unknown models - uses standard axis ordering",
)

# Model registry
GOPRO_MODELS_BASE = {
    "HERO5_BLACK": HERO5_BLACK,
    "HERO5_SESSION": HERO5_SESSION,
    "HERO6_BLACK": HERO6_BLACK,
    "HERO7_BLACK": HERO7_BLACK,
    "HERO8_BLACK": HERO8_BLACK,
    "HERO9_BLACK": HERO9_BLACK,
    "HERO10_BLACK": HERO10_BLACK,
    "HERO11_BLACK": HERO11_BLACK,
    "HERO12_BLACK": HERO12_BLACK,
    "HERO13_BLACK": HERO13_BLACK,
    "GENERIC": GENERIC,
}

# Alias mappings for easier user input
MODEL_ALIASES = {
    "HERO5": "HERO5_BLACK",
    "HERO6": "HERO6_BLACK",
    "HERO7": "HERO7_BLACK",
    "HERO8": "HERO8_BLACK",
    "HERO9": "HERO9_BLACK",
    "HERO10": "HERO10_BLACK",
    "HERO11": "HERO11_BLACK",
    "HERO12": "HERO12_BLACK",
    "HERO13": "HERO13_BLACK",
    "H5": "HERO5_BLACK",
    "H6": "HERO6_BLACK",
    "H7": "HERO7_BLACK",
    "H8": "HERO8_BLACK",
    "H9": "HERO9_BLACK",
    "H10": "HERO10_BLACK",
    "H11": "HERO11_BLACK",
    "H12": "HERO12_BLACK",
    "H13": "HERO13_BLACK",
}


# =============================================================================
# Helper Functions
# =============================================================================


def build_model_config(model_name: str) -> ModelConfig:
    """Build complete model config including inherited features.

    Args:
        model_name: Model identifier (e.g., "HERO10_BLACK")

    Returns:
        Complete ModelConfig with all inherited features
    """
    if model_name not in GOPRO_MODELS_BASE:
        logger.warning(f"Unknown model '{model_name}', using GENERIC config")
        model_name = "GENERIC"

    config = GOPRO_MODELS_BASE[model_name]

    # Create a copy to avoid modifying the base config
    built_config = ModelConfig(
        name=config.name,
        display_name=config.display_name,
        firmware_version=config.firmware_version,
        release_year=config.release_year,
        axis_order=config.axis_order.copy() if config.axis_order else {},
        supported_fourccs=config.supported_fourccs.copy()
        if config.supported_fourccs
        else set(),
        added_fourccs=config.added_fourccs.copy() if config.added_fourccs else set(),
        removed_fourccs=config.removed_fourccs.copy()
        if config.removed_fourccs
        else set(),
        changed_fourccs=config.changed_fourccs.copy() if config.changed_fourccs else {},
        notes=config.notes,
        inherits_from=config.inherits_from,
    )

    # Build inheritance chain
    if config.inherits_from:
        parent = build_model_config(config.inherits_from)

        # Merge supported FourCC codes
        built_config.supported_fourccs = (
            parent.supported_fourccs | built_config.added_fourccs
        ) - built_config.removed_fourccs

        # Inherit axis_order where not overridden
        for fourcc, axes in parent.axis_order.items():
            if fourcc not in built_config.axis_order:
                built_config.axis_order[fourcc] = axes
    else:
        # Base model - supported_fourccs is already complete
        pass

    return built_config


def detect_model_from_metadata(gpmf_samples: List) -> Optional[str]:
    """Detect GoPro model from GPMF metadata.

    Attempts to identify the camera model using:
    1. DVNM (Device Name) field
    2. Firmware version (FIRM field)
    3. FourCC signature matching (presence of specific codes)

    Args:
        gpmf_samples: List of parsed GPMF samples

    Returns:
        Model identifier string (e.g., "HERO10_BLACK") or None if unknown
    """
    device_name = None
    firmware = None
    available_fourccs = set()

    # Extract metadata
    def extract_from_samples(samples):
        nonlocal device_name, firmware
        for sample in samples:
            if sample.fourcc == "DVNM":
                device_name = sample.data
            elif sample.fourcc == "FIRM":
                firmware = sample.data
            available_fourccs.add(sample.fourcc)

            # Recursively check nested structures
            if sample.type_code == "\0" and isinstance(sample.data, list):
                extract_from_samples(sample.data)

    extract_from_samples(gpmf_samples)

    # Priority 1: Direct device name matching
    if device_name:
        device_name_lower = device_name.lower()

        if "hero13" in device_name_lower or "hero 13" in device_name_lower:
            return "HERO13_BLACK"
        elif "hero12" in device_name_lower or "hero 12" in device_name_lower:
            return "HERO12_BLACK"
        elif "hero11" in device_name_lower or "hero 11" in device_name_lower:
            return "HERO11_BLACK"
        elif "hero10" in device_name_lower or "hero 10" in device_name_lower:
            return "HERO10_BLACK"
        elif "hero9" in device_name_lower or "hero 9" in device_name_lower:
            return "HERO9_BLACK"
        elif "hero8" in device_name_lower or "hero 8" in device_name_lower:
            return "HERO8_BLACK"
        elif "hero7" in device_name_lower or "hero 7" in device_name_lower:
            return "HERO7_BLACK"
        elif "hero6" in device_name_lower or "hero 6" in device_name_lower:
            return "HERO6_BLACK"
        elif "hero5" in device_name_lower or "hero 5" in device_name_lower:
            if "session" in device_name_lower:
                return "HERO5_SESSION"
            return "HERO5_BLACK"

    # Priority 2: FourCC signature matching
    # Check for presence of model-specific FourCC codes
    if "GPS9" in available_fourccs:
        # GPS9 was added in Hero9
        if "FACS" in available_fourccs:
            return "HERO10_BLACK"  # Or newer
        return "HERO9_BLACK"
    elif "CORI" in available_fourccs and "IORI" in available_fourccs:
        # Orientation quaternions added in Hero8
        return "HERO8_BLACK"
    elif "SCEN" in available_fourccs or "UNIF" in available_fourccs:
        # Scene classification added in Hero7
        return "HERO7_BLACK"
    elif "FACE" in available_fourccs:
        # Face detection added in Hero6
        return "HERO6_BLACK"
    elif "GPS5" in available_fourccs or "ACCL" in available_fourccs:
        # Base telemetry from Hero5
        return "HERO5_BLACK"

    # Could not determine model
    logger.warning("Could not detect GoPro model from metadata")
    return None


def get_model_config(model_name: Optional[str] = None) -> ModelConfig:
    """Get model configuration, resolving aliases and building inheritance.

    Args:
        model_name: Model identifier, alias, or None for GENERIC

    Returns:
        Complete ModelConfig
    """
    if model_name is None:
        return build_model_config("GENERIC")

    # Resolve alias
    model_name = model_name.upper()
    if model_name in MODEL_ALIASES:
        model_name = MODEL_ALIASES[model_name]

    return build_model_config(model_name)


def list_supported_models() -> List[str]:
    """Get list of all supported model identifiers.

    Returns:
        List of model names
    """
    return sorted([name for name in GOPRO_MODELS_BASE.keys() if name != "GENERIC"])


def get_model_info(model_name: str) -> Dict:
    """Get human-readable information about a model.

    Args:
        model_name: Model identifier

    Returns:
        Dict with model information
    """
    config = get_model_config(model_name)
    return {
        "name": config.name,
        "display_name": config.display_name,
        "release_year": config.release_year,
        "firmware_version": config.firmware_version,
        "notes": config.notes,
        "num_supported_fourccs": len(config.supported_fourccs),
        "inherits_from": config.inherits_from,
    }
