"""Example: Export GoPro telemetry to various formats.

This example demonstrates exporting telemetry data to different formats:
- CSV (one file per stream)
- JSON (all streams in one file)
- HDF5 (binary format, good for large datasets)
- NPZ (NumPy compressed format)
"""

import sys

sys.path.insert(0, "../src")

import gopropy
import numpy as np

# Load telemetry
print("Loading GoPro telemetry...")
telemetry = gopropy.load("../data/river_side_1.MP4")
print(f"✓ Loaded {len(telemetry.list_streams())} streams\n")

# Export to different formats
print("=" * 60)
print("Exporting to various formats...")
print("=" * 60)

# 1. CSV Export (directory with one file per stream)
print("\n1. CSV Export (human-readable, one file per stream)")
telemetry.export_csv("exports/csv")
print("   ✓ Exported to exports/csv/")

# 2. JSON Export (single file, all streams)
print("\n2. JSON Export (human-readable, single file)")
telemetry.export_json("exports/telemetry.json")
print("   ✓ Exported to exports/telemetry.json")

# 3. HDF5 Export (binary, compressed, good for large data)
print("\n3. HDF5 Export (binary, compressed, efficient)")
try:
    telemetry.export_hdf5("exports/telemetry.h5")
    print("   ✓ Exported to exports/telemetry.h5")

    # Show how to load HDF5 data back
    print("\n   Loading data back from HDF5:")
    import h5py

    with h5py.File("exports/telemetry.h5", "r") as f:
        print(f"   - Video file: {f.attrs['video_file']}")
        print(f"   - Streams: {list(f.keys())[:5]}...")
        accel = f["Accelerometer"]
        print(f"   - Accelerometer shape: {accel['data'].shape}")
        print(f"   - Accelerometer units: {accel.attrs['units']}")
except ImportError:
    print("   ⚠ h5py not installed (pip install h5py), skipping HDF5 export")

# 4. NPZ Export (NumPy compressed format)
print("\n4. NPZ Export (NumPy compressed, easy to load)")
telemetry.export_npz("exports/telemetry.npz")
print("   ✓ Exported to exports/telemetry.npz")

# Show how to load NPZ data back
print("\n   Loading data back from NPZ:")
data = np.load("exports/telemetry.npz", allow_pickle=True)
print(f"   - Video file: {data['_video_file']}")
print(f"   - Streams: {data['_stream_names'][:5]}...")
print(f"   - Accelerometer shape: {data['Accelerometer_data'].shape}")

print("\n" + "=" * 60)
print("Export summary:")
print("=" * 60)
import os


def get_size(path):
    if os.path.isdir(path):
        total = sum(os.path.getsize(os.path.join(path, f)) for f in os.listdir(path))
        return total / 1024 / 1024  # MB
    return os.path.getsize(path) / 1024 / 1024  # MB


print(f"\nCSV:  {get_size('exports/csv'):.2f} MB (directory)")
print(f"JSON: {get_size('exports/telemetry.json'):.2f} MB")
if os.path.exists("exports/telemetry.h5"):
    print(f"HDF5: {get_size('exports/telemetry.h5'):.2f} MB (compressed)")
print(f"NPZ:  {get_size('exports/telemetry.npz'):.2f} MB (compressed)")

print("\nRecommendations:")
print("- CSV: Best for human inspection, Excel/spreadsheet software")
print("- JSON: Good for web apps, JavaScript integration")
print("- HDF5: Best for large datasets, Python/MATLAB/scientific computing")
print("- NPZ: Best for Python-only workflows, quick load with NumPy")
