# GoPro-Py

**Python library for extracting and analyzing telemetry data from GoPro MP4 files.**

GoPro cameras record rich sensor data (accelerometer, gyroscope, GPS, etc.) in their videos using the GPMF (GoPro Metadata Format). This library makes it easy to extract, process, and visualize that telemetry data in Python.

## Features

- 🎥 **Extract telemetry from GoPro videos** - Supports all GoPro cameras that record GPMF data
- 📊 **Multiple sensor streams** - Accelerometer, gyroscope, GPS, camera settings, and more
- 🐍 **Python-native** - Work with NumPy arrays and Pandas DataFrames
- 💾 **Multiple export formats** - CSV, JSON, HDF5, NPZ
- 📈 **Interactive visualization** - Optional Rerun integration for 3D visualization and time-series analysis
- ⚡ **Fast and efficient** - Processes 100+ packets in under a second
- 🎯 **Simple API** - Just `load()` and go

## Installation

### Basic Installation

```bash
pip install gopropy
```

**Requirements:** Python ≥3.12, ffmpeg installed on your system

### Optional Features

```bash
# For interactive visualization with Rerun
pip install gopropy[visualization]

# For HDF5 export support
pip install h5py

# Install everything
pip install gopropy[all]
```

### Install from source

```bash
git clone https://github.com/yourusername/gopro-py.git
cd gopro-py
pip install -e .
```

## Quick Start

```python
import gopropy

# Load telemetry from a GoPro video
telemetry = gopropy.load("GOPR0001.MP4")

# Access sensor streams
accelerometer = telemetry.get_stream("Accelerometer")
print(f"Shape: {accelerometer.data.shape}")  # (21047, 3) - 21k samples, 3 axes
print(f"Units: {accelerometer.units}")        # m/s²
print(f"Data:\n{accelerometer.data[:5]}")     # First 5 samples

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

### Axis Ordering

**⚠️ Important:** GoPro cameras use non-standard axis ordering:

**IMU Sensors (Hero5+):**
- **Accelerometer (ACCL):** Z, X, Y order (not X, Y, Z)
- **Gyroscope (GYRO):** Z, X, Y order (not X, Y, Z)

**Orientation Sensors (Hero8+):**
- **Camera Orientation (CORI):** W, X, Y, Z (quaternion, scalar-first)
- **Image Orientation (IORI):** W, X, Y, Z (quaternion, scalar-first)
- **Gravity Vector (GRAV):** X, Y, Z (standard)

The Z, X, Y ordering for IMU sensors is documented in the [official GPMF parser](https://github.com/gopro/gpmf-parser) for Hero5. Quaternion ordering (w-first) was verified through data analysis. The library automatically handles this and labels axes correctly in DataFrames.

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

### Working with GPS Data

```python
# Get GPS stream
gps = telemetry.get_stream("GPS (Lat., Long., Alt., 2D speed, 3D speed)")

if gps and gps.data.dtype != object:
    # GPS data columns: [latitude, longitude, altitude, 2D_speed, 3D_speed]
    latitudes = gps.data[:, 0]
    longitudes = gps.data[:, 1]
    altitudes = gps.data[:, 2]

    print(f"GPS points: {len(latitudes)}")
    print(f"Altitude range: {altitudes.min():.1f} - {altitudes.max():.1f} m")
```

### Export Formats

#### CSV Export (Human-Readable)

```python
# Export all streams to separate CSV files
telemetry.export_csv("output_directory/")
# Creates: output_directory/Accelerometer.csv, Gyroscope.csv, etc.
```

**Best for:** Excel, spreadsheet software, human inspection

#### JSON Export (Web-Friendly)

```python
# Export all streams to a single JSON file
telemetry.export_json("telemetry.json")
```

**Best for:** Web applications, JavaScript integration

#### NPZ Export (Compact Binary)

```python
# Export to NumPy compressed format
telemetry.export_npz("telemetry.npz")

# Load it back
import numpy as np
data = np.load("telemetry.npz")
accel_data = data['Accelerometer_data']
accel_timestamps = data['Accelerometer_timestamps']
```

**Best for:** Python workflows, fast loading, compact storage (7x smaller than CSV)

#### HDF5 Export (Scientific Data)

```python
# Export to HDF5 format (requires h5py)
telemetry.export_hdf5("telemetry.h5")

# Load it back
import h5py
with h5py.File("telemetry.h5", 'r') as f:
    accel = f['Accelerometer']
    data = accel['data'][:]
    timestamps = accel['timestamps'][:]
    units = accel.attrs['units']
```

**Best for:** Large datasets, MATLAB/scientific computing, hierarchical data


## Interactive Visualization with Rerun

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

This opens the Rerun viewer with:
- 📈 **Time-series plots** for all sensor streams
- 🎯 **3D visualizations** (acceleration vectors, GPS path, orientation)
- 🎬 **Synchronized video playback** (optional)
- 🔍 **Interactive timeline** for scrubbing through time

### Advanced Rerun Usage

```python
import rerun as rr
from gopropy.visualization import to_rerun

# Custom Rerun setup
rr.init("my_gopro_analysis", spawn=True)

# Log telemetry data
to_rerun(telemetry, video_path="GOPR0001.MP4")

# Add your own custom visualizations
rr.log("analysis/max_accel", rr.Scalars([accel_magnitude.max()]))

# Save recording
rr.save("analysis.rrd")
```

### View Saved Recordings

```bash
# View a saved recording
rerun telemetry_recording.rrd
```

---

### Visualization Module (Optional)

#### `visualize(telemetry: GoProTelemetry, video_path: Optional[str] = None, spawn: bool = True)`

Quick visualization with Rerun viewer.

#### `to_rerun(telemetry: GoProTelemetry, video_path: Optional[str] = None)`

Log telemetry data to Rerun (requires `rr.init()` to be called first).

## Examples

Complete examples are available in the `examples/` directory:

- **`basic_usage.py`** - Core functionality demonstration
- **`export_formats.py`** - Export to CSV, JSON, HDF5, NPZ
- **`visualize_rerun.py`** - Interactive visualization with Rerun

```bash
# Run examples
python examples/basic_usage.py
python examples/export_formats.py
python examples/visualize_rerun.py
```

## Technical Details

### GPMF Format

GoPro uses the GPMF (GoPro Metadata Format) to store telemetry data in MP4 files. GPMF is a Key-Length-Value (KLV) structure designed for efficient storage of high-frequency sensor data.

This library:
1. **Extracts** the GPMF data stream from MP4 using ffmpeg
2. **Parses** the binary KLV structure
3. **Decodes** sensor data with proper scaling and units
4. **Provides** a clean Python API for accessing the data


### Supported Cameras

All GoPro cameras that record GPMF metadata, including:
- HERO 5 Black and newer
- HERO (2018) and newer
- MAX
- Fusion

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

### "ffmpeg not found"

Install ffmpeg on your system:
- **macOS:** `brew install ffmpeg`
- **Ubuntu/Debian:** `sudo apt install ffmpeg`
- **Windows:** Download from https://ffmpeg.org/download.html

### "No GPMF telemetry stream found"

The video file may not contain GPMF data. This can happen if:
- The camera model doesn't support GPMF
- Telemetry recording was disabled in camera settings
- The file is not a genuine GoPro video

### "Could not convert ... to numeric array"

Some streams may have inconsistent data structures across packets. These streams are stored as object arrays and can still be accessed, but may need special handling.

## License

MIT License - see LICENSE file for details

## Acknowledgments

- [GoPro GPMF Parser](https://github.com/gopro/gpmf-parser) - Official GPMF format documentation
- [Rerun](https://rerun.io) - Visualization framework
- Built with NumPy, Pandas, and ffmpeg
