"""Example demonstrating GoPro model detection and axis ordering."""

import gopropy

# Load telemetry with automatic model detection
telemetry = gopropy.load("../data/river_side_1.MP4")

print("=" * 70)
print("GoPro Model Detection Example")
print("=" * 70)

# Display detected model
print(f"\n📹 Camera Model: {telemetry.model_config.display_name}")
print(f"   Release Year: {telemetry.model_config.release_year}")
print(f"   Firmware: {telemetry.model_config.firmware_version}")
if telemetry.detected_model:
    print(f"   Auto-detected: Yes ({telemetry.detected_model})")

# Show axis ordering configuration
print(f"\n📐 Axis Ordering Configuration:")
for fourcc, axes in sorted(telemetry.model_config.axis_order.items()):
    print(f"   {fourcc}: {' → '.join(axes)}")

# Demonstrate correct axis labels in data
print(f"\n📊 Accelerometer Data (first 3 samples):")
accel = telemetry.get_stream("Accelerometer")
df = accel.to_dataframe()
print(df.head(3).to_string(index=False))

print(f"\n🌀 Gyroscope Data (first 3 samples):")
gyro = telemetry.get_stream("Gyroscope")
df = gyro.to_dataframe()
print(df.head(3).to_string(index=False))

print(f"\n🎥 Camera Orientation (quaternion: w, x, y, z):")
cori = telemetry.get_stream("CameraOrientation")
if cori:
    df = cori.to_dataframe()
    print(
        f"   First sample: w={df.iloc[0]['CameraOrientation_w']:.6f}, "
        f"x={df.iloc[0]['CameraOrientation_x']:.6f}, "
        f"y={df.iloc[0]['CameraOrientation_y']:.6f}, "
        f"z={df.iloc[0]['CameraOrientation_z']:.6f}"
    )

# Show all available models
print(f"\n✅ Supported Models ({len(gopropy.list_supported_models())}):")
for i, model in enumerate(gopropy.list_supported_models(), 1):
    print(f"   {i}. {model}")

print("\n" + "=" * 70)
print("Note: GoPro cameras use Z,X,Y axis ordering for IMU sensors,")
print("not the standard X,Y,Z. This library handles it automatically!")
print("=" * 70)
