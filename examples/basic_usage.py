"""Basic usage example for gopropy."""

import gopropy

# Load telemetry from a GoPro video
telemetry = gopropy.load("../data/river_side_1.MP4")

print(f"Loaded: {telemetry}")
print(f"\nAvailable streams: {telemetry.list_streams()}\n")

# Access individual sensor streams
accelerometer = telemetry.get_stream("Accelerometer")
print(f"Accelerometer:")
print(f"  Shape: {accelerometer.data.shape}")
print(f"  Units: {accelerometer.units}")
print(
    f"  Sample rate: ~{len(accelerometer.timestamps) / accelerometer.timestamps[-1]:.0f} Hz"
)
print(f"  First few samples:\n{accelerometer.data[:5]}\n")

gyroscope = telemetry.get_stream("Gyroscope")
print(f"Gyroscope:")
print(f"  Shape: {gyroscope.data.shape}")
print(f"  Units: {gyroscope.units}")
print(f"  First few samples:\n{gyroscope.data[:5]}\n")

gps = telemetry.get_stream("GPS (Lat., Long., Alt., 2D speed, 3D speed)")
if gps and gps.data.dtype != object:
    print(f"GPS:")
    print(f"  Shape: {gps.data.shape}")
    print(f"  Columns: Latitude, Longitude, Altitude, 2D Speed, 3D Speed")
    print(f"  First location:\n{gps.data[0]}\n")

# Get individual stream as DataFrame
accel_df = accelerometer.to_dataframe()
print(f"\nAccelerometer DataFrame shape: {accel_df.shape}")
print(accel_df.head())

# Get all streams as DataFrames
all_dfs = telemetry.to_dataframe()
print(f"\nAll streams as DataFrames: {len(all_dfs)} streams")

# Export to CSV
print("\nExporting to CSV...")
telemetry.export_csv("telemetry_csv")
print("✓ Exported all streams to telemetry_csv/ directory")

# Export to JSON
print("\nExporting to JSON...")
telemetry.export_json("telemetry_all.json")
print("✓ Exported telemetry_all.json")

print("\n✓ Done!")
