# GoProPy

**Python library for extracting and analyzing telemetry data from GoPro MP4 files.**

GoPro cameras record rich sensor data (accelerometer, gyroscope, GPS, etc.) in their videos using the GPMF (GoPro Metadata Format). This library makes it easy to extract, process, and visualize that telemetry data in Python.

## Installation

### Basic Installation

```bash
# MacOS
brew install ffmpeg
# Linux
sudo apt install ffmpeg

pip install gopropy

# For interactive visualization with Rerun
pip install gopropy[visualization]

# For HDF5 export support
pip install h5py

# Install everything
pip install gopropy[all]
```

## Quick Start

```python
import gopropy

# Load telemetry from a GoPro video
telemetry = gopropy.load("GOPR0001.MP4")

# Access sensor streams
accelerometer = telemetry.get_stream("Accelerometer")
print(f"Shape: {accelerometer.data.shape}")  # (N, 3)
print(f"Units: {accelerometer.units}")       # m/s²

# Get all available streams
print(f"Available streams: {telemetry.list_streams()}")

# Export to various formats
telemetry.export_csv("output/")           # CSV files (one per stream)
telemetry.export_json("telemetry.json")   # Single JSON file
telemetry.export_npz("telemetry.npz")     # NumPy compressed format
```

## Supported Sensor Streams

GoPro cameras record various sensor streams depending on the model. Common streams include:

| Stream | Description | Sample Rate | Dimensions |
|--------|-------------|-------------|------------|
| **Accelerometer** | 3-axis acceleration (m/s²) | ~200 Hz | (N, 3) |
| **Gyroscope** | 3-axis angular velocity (rad/s) | ~200 Hz | (N, 3) |
| **GPS** | Latitude, longitude, altitude, speed | ~18 Hz | (N, 5) |
| **Camera Orientation** | Quaternion orientation | ~60 Hz | (N, 4) |
| **Image Orientation** | Image sensor orientation | ~60 Hz | (N, 4) |
| **Gravity Vector** | Gravity direction | ~60 Hz | (N, 3) |
| **Exposure Time** | Shutter speed (seconds) | Variable | (N,) |
| **ISO** | Sensor ISO value | Variable | (N,) |
| **White Balance** | Temperature & RGB gains | Variable | (N,) or (N, 3) |

*Note: Available streams vary by camera model and settings.*

## Supported GoPro Models

GoPro-Py supports **Hero5 through Hero13** cameras with automatic model detection.

### Model Detection

The library automatically detects your GoPro model from the video metadata and applies the correct telemetry interpretation:

```python
import gopropy

# Auto-detect model (recommended)
telemetry = gopropy.load("GOPR0001.MP4")
print(telemetry)
# GoProTelemetry(file='GOPR0001.MP4', model='Hero10 Black', streams=[...])

# Manual override if needed
telemetry = gopropy.load("GOPR0001.MP4", model="HERO10")

# List all supported models
models = gopropy.list_supported_models()
print(models)  # ['HERO5_BLACK', 'HERO5_SESSION', 'HERO6_BLACK', ...]
```

### Model-Specific Features

Different GoPro models support different telemetry features:

| Model | Year | Key Additions |
|-------|------|---------------|
| Hero5 Black/Session | 2016 | Base GPMF support (ACCL, GYRO, GPS5) |
| Hero6 Black | 2017 | Face detection |
| Hero7 Black | 2018 | Scene classification, image uniformity |
| Hero8 Black | 2019 | Camera orientation (CORI), gravity vector, wind detection |
| Hero9 Black | 2020 | Enhanced GPS (GPS9 with 9 fields) |
| Hero10 Black | 2021 | Enhanced face detection v4 |
| Hero11-13 Black | 2022-2024 | Continued enhancements |

See [docs/MODELS.md](docs/MODELS.md) for complete FourCC code listings and detailed model specifications.

## Usage Examples

### Working with Individual Streams

```python
import gopropy
import numpy as np

telemetry = gopropy.load("GOPR0001.MP4")

# Get accelerometer data
accel = telemetry.get_stream("Accelerometer")

# Access as NumPy array
print(f"Acceleration data shape: {accel.data.shape}")
print(f"Timestamps shape: {accel.timestamps.shape}")
print(f"Sample rate: ~{len(accel.timestamps) / accel.timestamps[-1]:.0f} Hz")

# Compute magnitude
accel_magnitude = np.linalg.norm(accel.data, axis=1)
print(f"Max acceleration: {accel_magnitude.max():.2f} m/s²")

# Convert to DataFrame
df = accel.to_dataframe()
print(df.head())
#    timestamp  Accelerometer_x  Accelerometer_y  Accelerometer_z
# 0        0.0        12.652278        -2.630695        -4.201439
# 1        0.0        12.465228        -2.486811        -4.196643
```



## Visualization with Rerun

GoPro-Py includes optional integration with [Rerun](https://rerun.io) for interactive visualization of telemetry data.

### Installation

```bash
pip install gopropy[visualization]
```

### Quick Visualization

```python
import gopropy
from gopropy.visualization import visualize

# Load telemetry
telemetry = gopropy.load("GOPR0001.MP4")

# Launch interactive viewer
visualize(telemetry, video_path="GOPR0001.MP4")
```
---

### Visualization Module (Optional)

#### `visualize(telemetry: GoProTelemetry, video_path: Optional[str] = None, spawn: bool = True)`

Quick visualization with Rerun viewer.

#### `to_rerun(telemetry: GoProTelemetry, video_path: Optional[str] = None)`

Log telemetry data to Rerun (requires `rr.init()` to be called first).


## Requirements

- Python ≥ 3.12
- NumPy ≥ 1.24.0
- Pandas ≥ 2.0.0
- ffmpeg (must be installed on system)

### Optional Dependencies

- `rerun-sdk` ≥ 0.15.0 - For visualization
- `opencv-python` ≥ 4.8.0 - For video frame extraction
- `h5py` ≥ 3.8.0 - For HDF5 export

## Troubleshooting

### "No GPMF telemetry stream found"

The video file may not contain GPMF data. This can happen if:
- The camera model doesn't support GPMF
- Telemetry recording was disabled in camera settings
- The file is not a genuine GoPro video

### "Could not convert ... to numeric array"

Some streams may have inconsistent data structures across packets. These streams are stored as object arrays and can still be accessed, but may need special handling.
