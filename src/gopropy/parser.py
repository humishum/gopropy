"""Parse GPMF (GoPro Metadata Format) binary data.

GPMF uses a Key-Length-Value (KLV) structure with 32-bit alignment.
"""

import struct
from dataclasses import dataclass
from typing import Any, Dict, List, Optional
from enum import Enum


class GPMFType(Enum):
    """GPMF data type codes."""

    SIGNED_BYTE = ord("b")
    UNSIGNED_BYTE = ord("B")
    SIGNED_SHORT = ord("s")
    UNSIGNED_SHORT = ord("S")
    SIGNED_LONG = ord("l")
    UNSIGNED_LONG = ord("L")
    FLOAT = ord("f")
    DOUBLE = ord("d")
    FOURCC = ord("F")
    ASCII = ord("c")
    UTC_TIME = ord("U")
    GUID = ord("G")
    COMPLEX = ord("?")
    NESTED = ord("\0")  # Nested structure


@dataclass
class GPMFSample:
    """Represents a single GPMF KLV sample."""

    fourcc: str  # 4-character key
    type_code: str  # Single character type
    structure_size: int  # Size of each sample element
    repeat_count: int  # Number of repeated samples
    data: Any  # Parsed data
    raw_data: bytes  # Raw binary data


class GPMFParser:
    """Parser for GPMF binary format.

    The GPMF format uses a modified Key-Length-Value structure:
    - Key: 4-byte FourCC (7-bit ASCII)
    - Type: 1 byte (type code)
    - Size: 1 byte (size of structure in bytes)
    - Repeat: 2 bytes (number of samples)
    - Data: Variable length, 32-bit aligned
    """

    TYPE_SIZES = {
        "b": 1,
        "B": 1,  # bytes
        "s": 2,
        "S": 2,  # shorts
        "l": 4,
        "L": 4,  # longs
        "f": 4,  # float
        "d": 8,  # double
        "F": 4,  # FourCC
        "c": 1,  # ASCII char
        "U": 16,  # UTC timestamp
        "G": 16,  # GUID
        "?": 0,  # Complex (variable)
        "\0": 0,  # Nested
    }

    def __init__(self):
        self.samples: List[GPMFSample] = []
        self.nested_data: Dict[str, List[GPMFSample]] = {}

    def parse(self, data: bytes, offset: int = 0) -> List[GPMFSample]:
        """Parse GPMF binary data into structured samples.

        Args:
            data: Raw GPMF binary data
            offset: Starting offset in the data

        Returns:
            List of parsed GPMF samples
        """
        samples = []
        pos = offset

        while pos < len(data) - 8:  # Need at least 8 bytes for header
            # Check if we've hit padding (null bytes)
            if data[pos : pos + 4] == b"\x00\x00\x00\x00":
                break

            sample = self._parse_sample(data, pos)
            if sample is None:
                break

            samples.append(sample)

            # Calculate next position (data is 32-bit aligned)
            data_size = sample.structure_size * sample.repeat_count
            aligned_size = (data_size + 3) & ~3  # Round up to multiple of 4
            pos += 8 + aligned_size  # Header (8 bytes) + aligned data

        return samples

    def _parse_sample(self, data: bytes, offset: int) -> Optional[GPMFSample]:
        """Parse a single GPMF KLV sample.

        Args:
            data: Raw GPMF data
            offset: Starting offset of the sample

        Returns:
            Parsed GPMFSample or None if invalid
        """
        if offset + 8 > len(data):
            return None

        # Parse header (8 bytes)
        fourcc = data[offset : offset + 4].decode("ascii", errors="replace")
        type_code = chr(data[offset + 4])
        structure_size = data[offset + 5]
        repeat_count = struct.unpack(">H", data[offset + 6 : offset + 8])[0]

        # Calculate data size and extract raw data
        data_size = structure_size * repeat_count
        aligned_size = (data_size + 3) & ~3

        if offset + 8 + aligned_size > len(data):
            return None

        raw_data = data[offset + 8 : offset + 8 + data_size]

        # Parse the actual data based on type
        parsed_data = self._parse_data(
            raw_data, type_code, structure_size, repeat_count
        )

        return GPMFSample(
            fourcc=fourcc,
            type_code=type_code,
            structure_size=structure_size,
            repeat_count=repeat_count,
            data=parsed_data,
            raw_data=raw_data,
        )

    def _parse_data(
        self,
        data: bytes,
        type_code: str,
        structure_size: int,
        repeat_count: int,
    ) -> Any:
        """Parse the data portion of a GPMF sample.

        Args:
            data: Raw data bytes
            type_code: GPMF type code
            structure_size: Size of each sample structure
            repeat_count: Number of repeated samples

        Returns:
            Parsed data (type depends on type_code)
        """
        # Handle nested structures
        if type_code == "\0":
            return self.parse(data)

        # Handle ASCII strings
        if type_code == "c":
            return data.decode("ascii", errors="replace").rstrip("\x00")

        # Handle FourCC
        if type_code == "F":
            fourccs = []
            for i in range(repeat_count):
                fourcc = data[i * 4 : (i + 1) * 4].decode("ascii", errors="replace")
                fourccs.append(fourcc)
            return fourccs if repeat_count > 1 else fourccs[0]

        # Handle numeric types
        format_char = self._get_format_char(type_code)
        if format_char is None:
            return data  # Return raw data for unknown types

        element_size = struct.calcsize(f">{format_char}")
        elements_per_sample = structure_size // element_size

        values = []
        offset = 0

        for _ in range(repeat_count):
            sample_values = []
            for _ in range(elements_per_sample):
                value = struct.unpack(
                    f">{format_char}", data[offset : offset + element_size]
                )[0]
                sample_values.append(value)
                offset += element_size

            # If only one element per sample, unwrap the list
            if elements_per_sample == 1:
                values.append(sample_values[0])
            else:
                values.append(tuple(sample_values))

        # If only one sample, unwrap the list
        return values if repeat_count > 1 else values[0] if values else None

    def _get_format_char(self, type_code: str) -> Optional[str]:
        """Get struct format character for a GPMF type code.

        Args:
            type_code: GPMF type code

        Returns:
            struct format character or None
        """
        mapping = {
            "b": "b",  # signed byte
            "B": "B",  # unsigned byte
            "s": "h",  # signed short
            "S": "H",  # unsigned short
            "l": "i",  # signed long (32-bit int)
            "L": "I",  # unsigned long (32-bit int)
            "f": "f",  # float
            "d": "d",  # double
        }
        return mapping.get(type_code)

    def find_samples(self, samples: List[GPMFSample], fourcc: str) -> List[GPMFSample]:
        """Find all samples with a specific FourCC key.

        Args:
            samples: List of samples to search
            fourcc: FourCC key to find

        Returns:
            List of matching samples
        """
        matches = []
        for sample in samples:
            if sample.fourcc == fourcc:
                matches.append(sample)
            # Recursively search nested structures
            if sample.type_code == "\0" and isinstance(sample.data, list):
                matches.extend(self.find_samples(sample.data, fourcc))
        return matches

    def get_device_streams(
        self, samples: List[GPMFSample]
    ) -> Dict[str, Dict[str, Any]]:
        """Extract all device streams from parsed GPMF data.

        Args:
            samples: List of parsed GPMF samples

        Returns:
            Dictionary mapping stream names to their metadata and data
        """
        devices = {}

        for sample in samples:
            if sample.fourcc == "DEVC" and sample.type_code == "\0":
                device_data = self._parse_device(sample.data)
                if device_data:
                    device_id = device_data.get("device_id", "unknown")
                    devices[device_id] = device_data

        return devices

    def _parse_device(self, device_samples: List[GPMFSample]) -> Dict[str, Any]:
        """Parse a DEVC (device) structure.

        Args:
            device_samples: Samples within a DEVC structure

        Returns:
            Dictionary with device metadata and streams
        """
        device = {
            "device_id": None,
            "device_name": None,
            "streams": {},
        }

        for sample in device_samples:
            if sample.fourcc == "DVID":
                device["device_id"] = sample.data
            elif sample.fourcc == "DVNM":
                device["device_name"] = sample.data
            elif sample.fourcc == "STRM" and sample.type_code == "\0":
                stream = self._parse_stream(sample.data)
                if stream and "name" in stream:
                    device["streams"][stream["name"]] = stream

        return device

    def _parse_stream(self, stream_samples: List[GPMFSample]) -> Dict[str, Any]:
        """Parse a STRM (stream) structure.

        Args:
            stream_samples: Samples within a STRM structure

        Returns:
            Dictionary with stream metadata and data
        """
        stream = {
            "name": None,
            "units": None,
            "scale": None,
            "data": [],
            "fourcc": None,
        }

        # Primary sensor data FourCCs (the main data streams we want)
        primary_fourccs = {
            "ACCL",
            "GYRO",
            "GPS5",
            "MAGN",
            "SHUT",
            "WBAL",
            "WRGB",
            "ISOE",
            "YAVG",
            "UNIF",
            "CORI",
        }

        # All known sensor/metadata FourCC codes
        sensor_fourccs = primary_fourccs | {
            "GPSF",
            "GPSU",
            "GPSP",
            "FACE",
            "FCNM",
            "ISOG",
            "AALP",
            "MWET",
            "WNDM",
            "MTRX",
            "ORIN",
            "ORIO",
            "GRAV",
            "IORI",
            "SCEN",
            "SROT",
        }

        for sample in stream_samples:
            if sample.fourcc == "STNM":
                stream["name"] = sample.data
            elif sample.fourcc == "SIUN":
                stream["units"] = sample.data
            elif sample.fourcc == "SCAL":
                stream["scale"] = sample.data
            elif sample.fourcc in sensor_fourccs:
                # Prioritize primary data FourCCs over metadata
                if sample.fourcc in primary_fourccs:
                    if not stream["fourcc"] or stream["fourcc"] not in primary_fourccs:
                        stream["fourcc"] = sample.fourcc
                elif not stream["fourcc"]:
                    stream["fourcc"] = sample.fourcc

                if not stream["name"]:
                    stream["name"] = sample.fourcc
                stream["data"].append(sample)

        return stream if stream["name"] else {}
