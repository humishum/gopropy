"""Extract GPMF telemetry stream from GoPro MP4 files."""

import subprocess
import json
from pathlib import Path
from typing import List, Tuple


def extract_gpmf_stream(filepath: str) -> List[Tuple[float, bytes]]:
    """Extract raw GPMF telemetry data from a GoPro MP4 file.

    This function locates the GPMF metadata track (codec_tag: gpmd) in the MP4
    file and extracts all telemetry packets along with their timestamps.

    Args:
        filepath: Path to the GoPro MP4 file

    Returns:
        List of tuples (timestamp, raw_gpmf_data) where:
        - timestamp: Time in seconds from start of video
        - raw_gpmf_data: Raw GPMF binary data for that packet

    Raises:
        FileNotFoundError: If the file doesn't exist
        ValueError: If no GPMF stream is found in the file
        RuntimeError: If ffmpeg/ffprobe is not available
    """
    filepath = Path(filepath)
    if not filepath.exists():
        raise FileNotFoundError(f"File not found: {filepath}")

    # First, identify the GPMF stream index
    gpmf_stream_index = _find_gpmf_stream(filepath)
    if gpmf_stream_index is None:
        raise ValueError(f"No GPMF telemetry stream found in {filepath}")

    # Extract the raw GPMF data using ffmpeg
    return _extract_raw_packets(filepath, gpmf_stream_index)


def _find_gpmf_stream(filepath: Path) -> int | None:
    """Find the stream index of the GPMF metadata track.

    Args:
        filepath: Path to the MP4 file

    Returns:
        Stream index of GPMF track, or None if not found
    """
    try:
        result = subprocess.run(
            [
                "ffprobe",
                "-v",
                "quiet",
                "-print_format",
                "json",
                "-show_streams",
                str(filepath),
            ],
            capture_output=True,
            text=True,
            check=True,
        )
    except FileNotFoundError:
        raise RuntimeError(
            "ffprobe not found. Please install ffmpeg: https://ffmpeg.org/download.html"
        )
    except subprocess.CalledProcessError as e:
        raise RuntimeError(f"ffprobe failed: {e.stderr}")

    data = json.loads(result.stdout)

    # Look for the stream with codec_tag_string == "gpmd"
    for stream in data.get("streams", []):
        if stream.get("codec_tag_string") == "gpmd":
            return stream["index"]

    return None


def _extract_raw_packets(
    filepath: Path, stream_index: int
) -> List[Tuple[float, bytes]]:
    """Extract raw GPMF packets from the specified stream.

    Args:
        filepath: Path to the MP4 file
        stream_index: Index of the GPMF stream

    Returns:
        List of (timestamp, raw_data) tuples
    """
    # Get packet information (timestamps and sizes)
    packet_info = _extract_packet_info(filepath, stream_index)

    if not packet_info:
        return []

    try:
        # Extract raw binary data
        result = subprocess.run(
            [
                "ffmpeg",
                "-v",
                "quiet",
                "-i",
                str(filepath),
                "-map",
                f"0:{stream_index}",
                "-c",
                "copy",
                "-f",
                "rawvideo",
                "-",
            ],
            capture_output=True,
            check=True,
        )
    except FileNotFoundError:
        raise RuntimeError(
            "ffmpeg not found. Please install ffmpeg: https://ffmpeg.org/download.html"
        )
    except subprocess.CalledProcessError as e:
        raise RuntimeError(f"ffmpeg extraction failed: {e.stderr.decode()}")

    raw_data = result.stdout

    # Split the raw data based on packet sizes
    packets = []
    offset = 0

    for timestamp, size in packet_info:
        if offset + size > len(raw_data):
            break
        packet_data = raw_data[offset : offset + size]
        packets.append((timestamp, packet_data))
        offset += size

    return packets


def _extract_packet_info(filepath: Path, stream_index: int) -> List[Tuple[float, int]]:
    """Extract timestamp and size for each packet in the GPMF stream.

    Args:
        filepath: Path to the MP4 file
        stream_index: Index of the GPMF stream

    Returns:
        List of (timestamp, size) tuples
    """
    try:
        result = subprocess.run(
            [
                "ffprobe",
                "-v",
                "quiet",
                "-print_format",
                "json",
                "-show_packets",
                "-select_streams",
                str(stream_index),
                str(filepath),
            ],
            capture_output=True,
            text=True,
            check=True,
        )
    except subprocess.CalledProcessError as e:
        raise RuntimeError(f"ffprobe packet info extraction failed: {e.stderr}")

    data = json.loads(result.stdout)
    packet_info = []

    for packet in data.get("packets", []):
        pts_time = packet.get("pts_time")
        size = packet.get("size")
        if pts_time and size:
            packet_info.append((float(pts_time), int(size)))

    return packet_info
