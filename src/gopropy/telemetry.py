"""High-level API for GoPro telemetry data."""

import numpy as np
import pandas as pd
from pathlib import Path
from typing import Dict, List, Optional, Any
from dataclasses import dataclass
import logging

from .extractor import extract_gpmf_stream
from .parser import GPMFParser
from .models import ModelConfig, get_model_config, detect_model_from_metadata

logger = logging.getLogger(__name__)


@dataclass
class SensorStream:
    """Represents a single sensor data stream."""

    name: str
    data: np.ndarray
    timestamps: np.ndarray
    units: Optional[str] = None
    scale: Optional[float] = None
    metadata: Dict[str, Any] = None
    model_config: Optional[ModelConfig] = None

    def __post_init__(self):
        if self.metadata is None:
            self.metadata = {}

    def to_dataframe(
        self, set_index: bool = False, model_config: Optional[ModelConfig] = None
    ) -> pd.DataFrame:
        """Convert sensor stream to a pandas DataFrame.

        Args:
            set_index: If True, use timestamp as index (may have duplicates)
            model_config: Optional ModelConfig to determine axis ordering.
                         If not provided, uses self.model_config if available.

        Returns:
            DataFrame with sensor data columns
        """
        if self.data.ndim == 1:
            df = pd.DataFrame(
                {
                    "timestamp": self.timestamps,
                    self.name: self.data,
                }
            )
        else:
            # Multi-axis data (e.g., 3-axis accelerometer)
            num_axes = self.data.shape[1]

            # Use provided model_config or fall back to stored one
            if model_config is None:
                model_config = self.model_config

            # Get axis labels from model config if available
            fourcc = self.metadata.get("fourcc")
            if model_config and fourcc and fourcc in model_config.axis_order:
                axis_names = model_config.axis_order[fourcc][:num_axes]
                logger.debug(
                    f"Using model-specific axis order for {fourcc}: {axis_names}"
                )
            else:
                # Default fallback: standard x, y, z, w ordering
                axis_names = ["x", "y", "z", "w"][:num_axes]
                if fourcc:
                    logger.debug(
                        f"No model-specific axis order for {fourcc}, using default: {axis_names}"
                    )

            if len(axis_names) < num_axes:
                # Ensure we never drop columns when axis labels are incomplete.
                axis_names += [
                    f"axis_{i + 1}" for i in range(len(axis_names), num_axes)
                ]

            # Build DataFrame with explicit column order to preserve axis ordering
            # Use axis-only labels when model config defines them; fall back to name+axis.
            use_axis_only = (
                model_config is not None
                and fourcc is not None
                and fourcc in model_config.axis_order
            )

            data_dict = {"timestamp": self.timestamps}
            column_names = ["timestamp"]
            seen_names = {"timestamp"}

            for i, axis in enumerate(axis_names):
                if use_axis_only and axis not in seen_names:
                    col_name = axis
                else:
                    col_name = f"{self.name}_{axis}"
                data_dict[col_name] = self.data[:, i]
                column_names.append(col_name)
                seen_names.add(col_name)

            # Create DataFrame and explicitly reorder columns to match axis_names order
            df = pd.DataFrame(data_dict)
            df = df[column_names]  # Reorder columns to match our specified order

        if set_index:
            df = df.set_index("timestamp")
        return df


class GoProTelemetry:
    """High-level interface for GoPro telemetry data.

    This class provides easy access to all sensor streams in a GoPro video,
    with methods to export to various formats and visualize the data.

    Attributes:
        filepath: Path to the source MP4 file
        streams: Dictionary of sensor streams keyed by stream name
        metadata: Video and device metadata
        model_config: Model-specific configuration
        detected_model: Auto-detected model name (if any)
    """

    def __init__(self, filepath: str, model_config: Optional[ModelConfig] = None):
        """Initialize telemetry object.

        Args:
            filepath: Path to GoPro MP4 file
            model_config: Optional ModelConfig for model-specific parsing
        """
        self.filepath = Path(filepath)
        self.streams: Dict[str, SensorStream] = {}
        self.metadata: Dict[str, Any] = {}
        self._raw_packets: List[tuple] = []
        self._parser = GPMFParser()
        self.model_config = model_config
        self.detected_model: Optional[str] = None

    @classmethod
    def from_file(cls, filepath: str, model: Optional[str] = None) -> "GoProTelemetry":
        """Load and parse telemetry from a GoPro MP4 file.

        Args:
            filepath: Path to the GoPro MP4 file
            model: Optional model identifier (e.g., 'HERO10', 'HERO7_BLACK').
                   If None, attempts to auto-detect from metadata.

        Returns:
            GoProTelemetry object with parsed data
        """
        # If model specified, use it directly
        if model:
            logger.info(f"Using manually specified model: {model}")
            model_config = get_model_config(model)
            telemetry = cls(filepath, model_config=model_config)
            telemetry._load()
            return telemetry

        # Otherwise, attempt auto-detection
        # First, extract a sample of GPMF data to detect model
        logger.info("Attempting to auto-detect GoPro model...")
        try:
            raw_packets = extract_gpmf_stream(str(filepath))
            if raw_packets:
                # Parse first packet to get device info
                parser = GPMFParser()
                _, first_packet = raw_packets[0]
                samples = parser.parse(first_packet)

                # Attempt detection
                detected = detect_model_from_metadata(samples)
                if detected:
                    logger.info(f"Detected model: {detected}")
                    model_config = get_model_config(detected)
                    telemetry = cls(filepath, model_config=model_config)
                    telemetry.detected_model = detected
                    telemetry._load()
                    return telemetry
                else:
                    logger.warning("Could not detect model, using GENERIC config")
                    model_config = get_model_config("GENERIC")
                    telemetry = cls(filepath, model_config=model_config)
                    telemetry._load()
                    return telemetry
        except Exception as e:
            logger.warning(f"Error during model detection: {e}, using GENERIC config")
            model_config = get_model_config("GENERIC")
            telemetry = cls(filepath, model_config=model_config)
            telemetry._load()
            return telemetry

    def _load(self):
        """Load and parse all telemetry data from the file."""
        # Extract raw GPMF packets
        self._raw_packets = extract_gpmf_stream(str(self.filepath))

        # Parse each packet and accumulate sensor data
        all_streams: Dict[str, List] = {}

        for timestamp, packet_data in self._raw_packets:
            samples = self._parser.parse(packet_data)
            devices = self._parser.get_device_streams(samples)

            # Extract streams from all devices
            for device_id, device_data in devices.items():
                for stream_name, stream_data in device_data.get("streams", {}).items():
                    if stream_name not in all_streams:
                        all_streams[stream_name] = {
                            "timestamps": [],
                            "data": [],
                            "units": stream_data.get("units"),
                            "scale": stream_data.get("scale"),
                            "fourcc": stream_data.get("fourcc"),
                        }

                    # Extract the actual sensor values
                    # Only include samples that match the stream's main FourCC
                    stream_fourcc = stream_data.get("fourcc")
                    for sample in stream_data.get("data", []):
                        # Skip metadata samples (like ORIN, STMP) - only include main sensor data
                        if stream_fourcc and sample.fourcc == stream_fourcc:
                            all_streams[stream_name]["timestamps"].append(timestamp)
                            all_streams[stream_name]["data"].append(sample.data)

        # Convert accumulated data to SensorStream objects
        for stream_name, stream_info in all_streams.items():
            self._create_sensor_stream(stream_name, stream_info)

    def _create_sensor_stream(self, name: str, stream_info: Dict):
        """Create a SensorStream from accumulated data.

        Args:
            name: Stream name
            stream_info: Dictionary with timestamps, data, units, scale
        """
        data_list = stream_info["data"]
        timestamp_list = stream_info["timestamps"]

        if not data_list:
            return

        # Flatten the data structure
        # Each entry in data_list can be:
        # - A scalar (single value)
        # - A list/tuple of scalars (multi-axis single sample)
        # - A list of lists/tuples (multiple multi-axis samples)
        flat_data = []
        flat_timestamps = []

        fourcc = stream_info.get("fourcc")
        axis_order_len = None
        if self.model_config and fourcc in self.model_config.axis_order:
            axis_order_len = len(self.model_config.axis_order[fourcc])

        for ts, item in zip(timestamp_list, data_list):
            # Skip non-numeric data (strings, bytes, etc.)
            if isinstance(item, (str, bytes)):
                continue

            if isinstance(item, (list, tuple)):
                if len(item) == 0:
                    continue
                # Check if this is a list of samples or a single multi-axis sample
                first_elem = item[0]
                if isinstance(first_elem, (list, tuple)):
                    # List of multi-axis samples: [(z,x,y), (z,x,y), ...]
                    for sample in item:
                        flat_data.append(sample)
                        flat_timestamps.append(ts)
                else:
                    # Single multi-axis sample or list of scalars
                    if isinstance(first_elem, (int, float)):
                        # Could be either:
                        # - Multiple scalar samples: [v1, v2, v3, ...]
                        # - Single multi-axis sample: (z, x, y)
                        # Heuristic: if length <= 4 or matches a known axis order,
                        # assume single multi-axis sample.
                        if len(item) <= 4 or (
                            axis_order_len is not None and len(item) == axis_order_len
                        ):
                            # Single multi-axis sample
                            flat_data.append(item)
                            flat_timestamps.append(ts)
                        else:
                            # Multiple scalar samples
                            for sample in item:
                                flat_data.append(sample)
                                flat_timestamps.append(ts)
                    elif isinstance(first_elem, (str, bytes)):
                        # Skip non-numeric data
                        continue
                    else:
                        # Unknown structure, append as-is
                        flat_data.append(item)
                        flat_timestamps.append(ts)
            elif isinstance(item, (int, float)):
                # Scalar numeric value
                flat_data.append(item)
                flat_timestamps.append(ts)

        if not flat_data:
            return

        # Convert to numpy arrays
        try:
            data = np.array(flat_data)
            timestamps = np.array(flat_timestamps)
        except (ValueError, TypeError) as e:
            # If conversion fails, store as object array
            print(f"Warning: Could not convert {name} to numeric array: {e}")
            data = np.array(flat_data, dtype=object)
            timestamps = np.array(flat_timestamps)

        # Apply scaling if provided
        scale = stream_info.get("scale")
        if scale is not None and data.dtype != object:
            if isinstance(scale, (list, tuple)):
                # Different scale for each axis
                scale_array = np.array(scale)
                data = data.astype(float) / scale_array
            else:
                # Single scale for all values
                data = data.astype(float) / scale

        # Store FourCC in metadata for axis ordering
        metadata = {"fourcc": stream_info.get("fourcc")}

        # Validate FourCC against model if available
        fourcc = stream_info.get("fourcc")
        if self.model_config and fourcc:
            if fourcc not in self.model_config.supported_fourccs:
                logger.warning(
                    f"FourCC '{fourcc}' not in supported set for model "
                    f"{self.model_config.display_name}. This may indicate "
                    f"incorrect model detection or a newer firmware version."
                )

        self.streams[name] = SensorStream(
            name=name,
            data=data,
            timestamps=timestamps,
            units=stream_info.get("units"),
            scale=scale,
            metadata=metadata,
            model_config=self.model_config,
        )

    def get_stream(self, name: str) -> Optional[SensorStream]:
        """Get a specific sensor stream by name.

        Args:
            name: Stream name (e.g., 'ACCL', 'GYRO', 'GPS5')

        Returns:
            SensorStream object or None if not found
        """
        return self.streams.get(name)

    def list_streams(self) -> List[str]:
        """Get list of all available stream names.

        Returns:
            List of stream names
        """
        return list(self.streams.keys())

    def to_dataframe(
        self, streams: Optional[List[str]] = None
    ) -> Dict[str, pd.DataFrame]:
        """Convert telemetry data to pandas DataFrames.

        Note: Different streams have different sample rates, so they are returned
        as separate DataFrames in a dictionary.

        Args:
            streams: List of stream names to include (default: all)

        Returns:
            Dictionary mapping stream names to DataFrames
        """
        if streams is None:
            streams = self.list_streams()

        result = {}
        for stream_name in streams:
            stream = self.get_stream(stream_name)
            if stream:
                result[stream_name] = stream.to_dataframe(
                    model_config=self.model_config
                )

        return result

    def to_dict(self) -> Dict[str, Any]:
        """Convert telemetry data to a dictionary.

        Returns:
            Dictionary with stream names as keys and data arrays as values
        """
        return {
            name: {
                "data": stream.data.tolist(),
                "timestamps": stream.timestamps.tolist(),
                "units": stream.units,
                "scale": stream.scale,
                "metadata": stream.metadata,
            }
            for name, stream in self.streams.items()
        }

    def export_csv(self, output_dir: str, streams: Optional[List[str]] = None):
        """Export telemetry data to CSV files.

        Each stream is exported to a separate CSV file.

        Args:
            output_dir: Directory for output CSV files
            streams: List of stream names to export (default: all)
        """
        import os

        os.makedirs(output_dir, exist_ok=True)

        dfs = self.to_dataframe(streams)
        for stream_name, df in dfs.items():
            # Sanitize filename
            filename = stream_name.replace(" ", "_").replace("[", "").replace("]", "")
            filepath = os.path.join(output_dir, f"{filename}.csv")
            df.to_csv(filepath, index=False)
            print(f"  Exported {filepath}")

    def export_json(self, output_path: str):
        """Export telemetry data to JSON file.

        Args:
            output_path: Path for output JSON file
        """
        import json

        data = self.to_dict()
        with open(output_path, "w") as f:
            json.dump(data, f, indent=2)

    def export_hdf5(self, output_path: str, streams: Optional[List[str]] = None):
        """Export telemetry data to HDF5 file.

        Each stream is stored as a separate dataset in the HDF5 file.

        Args:
            output_path: Path for output HDF5 file
            streams: List of stream names to export (default: all)

        Raises:
            ImportError: If h5py is not installed
        """
        try:
            import h5py
        except ImportError:
            raise ImportError(
                "h5py is required for HDF5 export. Install it with: pip install h5py"
            )

        if streams is None:
            streams = self.list_streams()

        with h5py.File(output_path, "w") as f:
            # Store metadata
            f.attrs["video_file"] = str(self.filepath.name)
            f.attrs["num_streams"] = len(streams)

            # Store each stream
            for stream_name in streams:
                stream = self.get_stream(stream_name)
                if stream is None:
                    continue

                # Create group for this stream
                grp = f.create_group(stream_name.replace("/", "_"))

                # Store data
                grp.create_dataset("data", data=stream.data, compression="gzip")
                grp.create_dataset(
                    "timestamps", data=stream.timestamps, compression="gzip"
                )

                # Store metadata as attributes
                if stream.units:
                    grp.attrs["units"] = stream.units
                if stream.scale is not None:
                    if isinstance(stream.scale, (list, tuple)):
                        grp.attrs["scale"] = stream.scale
                    else:
                        grp.attrs["scale"] = stream.scale

                grp.attrs["shape"] = stream.data.shape
                grp.attrs["dtype"] = str(stream.data.dtype)

    def export_npz(self, output_path: str, streams: Optional[List[str]] = None):
        """Export telemetry data to NumPy NPZ file.

        Each stream is stored with keys: '<stream_name>_data' and '<stream_name>_timestamps'.

        Args:
            output_path: Path for output NPZ file
            streams: List of stream names to export (default: all)
        """
        if streams is None:
            streams = self.list_streams()

        data_dict = {}

        # Add metadata
        data_dict["_video_file"] = str(self.filepath.name)
        data_dict["_stream_names"] = streams

        # Store each stream
        for stream_name in streams:
            stream = self.get_stream(stream_name)
            if stream is None:
                continue

            # Sanitize key names (replace spaces and special chars)
            key_base = (
                stream_name.replace(" ", "_")
                .replace("[", "")
                .replace("]", "")
                .replace(",", "")
            )

            data_dict[f"{key_base}_data"] = stream.data
            data_dict[f"{key_base}_timestamps"] = stream.timestamps

            # Store metadata as separate arrays
            if stream.units:
                data_dict[f"{key_base}_units"] = stream.units
            if stream.scale is not None:
                data_dict[f"{key_base}_scale"] = np.array(stream.scale)

        np.savez_compressed(output_path, **data_dict)

    def __repr__(self) -> str:
        """String representation of the telemetry object."""
        streams_info = ", ".join(self.list_streams())
        model_info = (
            f", model='{self.model_config.display_name}'" if self.model_config else ""
        )
        return f"GoProTelemetry(file='{self.filepath.name}'{model_info}, streams=[{streams_info}])"
