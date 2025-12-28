"""Example: Visualize GoPro telemetry with Rerun.

This example shows how to visualize GoPro telemetry data using Rerun.
Rerun provides an interactive viewer for time-series data, 3D visualizations,
and video playback.

Requirements:
    pip install gopropy[visualization]

Usage:
    python visualize_rerun.py

Note: This will open the Rerun viewer in a new window.
"""

import sys

sys.path.insert(0, "../src")

import gopropy
from gopropy.visualization import visualize

# Load telemetry from the sample video
print("Loading GoPro telemetry...")
telemetry = gopropy.load("../data/river_side_1.MP4")

print(f"Loaded {len(telemetry.list_streams())} streams:")
for stream_name in telemetry.list_streams():
    stream = telemetry.get_stream(stream_name)
    print(f"  - {stream_name}: {stream.data.shape}")

# Visualize with Rerun
# This will:
# - Initialize Rerun viewer
# - Log all telemetry streams
# - Optionally log video frames (can be slow for long videos)
print("\nVisualizing in Rerun...")
visualize(
    telemetry,
    video_path="../data/river_side_1.MP4",  # Comment out to skip video logging
    spawn=True,
)

print("""
✓ Rerun viewer opened!

In the Rerun viewer, you can:
- View time-series plots for all sensor streams
- Navigate through time using the timeline
- View 3D visualizations (accelerometer arrows, GPS path, etc.)
- See synchronized video playback
- Compare multiple streams side-by-side

Tips:
- Click on entities in the left panel to toggle visibility
- Use the timeline at the bottom to scrub through time
- Select multiple entities to compare them
""")
