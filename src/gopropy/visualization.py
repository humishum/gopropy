"""Optional visualization utilities for GoPro telemetry using Rerun.

This module is optional and requires rerun-sdk to be installed:
    pip install gopropy[visualization]
"""

from typing import TYPE_CHECKING, Optional

if TYPE_CHECKING:
    from .telemetry import GoProTelemetry


def to_rerun(
    telemetry: "GoProTelemetry",
    video_path: Optional[str] = None,
    app_id: str = "gopro_telemetry",
):
    """Log GoPro telemetry data to Rerun for visualization.

    This function logs all telemetry streams to Rerun in a structured format.
    It does NOT call rr.init() or rr.spawn() - you should do that before calling
    this function if needed.

    Args:
        telemetry: GoProTelemetry object with parsed data
        video_path: Optional path to video file for synchronized playback
        app_id: Rerun application ID (only used if you haven't called rr.init())

    Example:
        >>> import gopropy
        >>> from gopropy.visualization import to_rerun
        >>> import rerun as rr
        >>>
        >>> # Load telemetry
        >>> telemetry = gopropy.load("GOPR0001.MP4")
        >>>
        >>> # Initialize Rerun and log data
        >>> rr.init(app_id="gopro_viewer", spawn=True)
        >>> to_rerun(telemetry, video_path="GOPR0001.MP4")

    Raises:
        ImportError: If rerun-sdk is not installed
    """
    try:
        import rerun  # noqa: F401
    except ImportError:
        raise ImportError(
            "rerun-sdk is required for visualization. "
            "Install it with: pip install gopropy[visualization]"
        )

    # Log video if path provided
    if video_path:
        _log_video(video_path)

    # Log each sensor stream
    for stream_name in telemetry.list_streams():
        stream = telemetry.get_stream(stream_name)
        if stream is None:
            continue

        _log_stream_to_rerun(stream_name, stream)


def _log_video(video_path: str):
    """Log video frames to Rerun."""
    try:
        import rerun as rr
        import cv2
    except ImportError:
        print("Warning: opencv-python required for video logging, skipping video")
        return

    cap = cv2.VideoCapture(video_path)
    fps = cap.get(cv2.CAP_PROP_FPS)
    frame_idx = 0

    while True:
        ret, frame = cap.read()
        if not ret:
            break

        # Convert BGR to RGB
        frame_rgb = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)

        # Log frame with timestamp
        timestamp_sec = frame_idx / fps
        rr.set_time("video_time", timestamp=timestamp_sec)
        rr.log("video/frame", rr.Image(frame_rgb))

        frame_idx += 1

        # Limit to reasonable frame count for demo
        if frame_idx > 1000:  # ~16 seconds at 60fps
            print(f"Logged {frame_idx} video frames (limited for demo)")
            break

    cap.release()
    print(f"Logged {frame_idx} video frames at {fps:.1f} fps")


def _log_stream_to_rerun(stream_name: str, stream):
    """Log a single sensor stream to Rerun."""
    import rerun as rr

    # Skip non-numeric data
    if stream.data.dtype == object:
        print(f"Skipping {stream_name} (non-numeric data)")
        return

    # Create entity path (replace special chars)
    entity_path = (
        f"sensors/{stream_name.replace(' ', '_').replace('[', '').replace(']', '')}"
    )

    # Log data points
    for i, (timestamp, values) in enumerate(zip(stream.timestamps, stream.data)):
        rr.set_time("telemetry_time", timestamp=float(timestamp))

        if stream.data.ndim == 1:
            # Scalar data
            rr.log(f"{entity_path}/value", rr.Scalars([float(values)]))

        elif stream.data.ndim == 2:
            num_axes = stream.data.shape[1]

            # Log based on data dimensions
            if num_axes == 3:
                # 3D vector (accelerometer, gyroscope, etc.)
                rr.log(
                    f"{entity_path}/vector",
                    rr.Arrows3D(
                        origins=[[0, 0, 0]],
                        vectors=[values.tolist()],
                    ),
                )
                # Also log individual components
                rr.log(f"{entity_path}/x", rr.Scalars([float(values[0])]))
                rr.log(f"{entity_path}/y", rr.Scalars([float(values[1])]))
                rr.log(f"{entity_path}/z", rr.Scalars([float(values[2])]))

            elif num_axes == 4:
                # 4D data (quaternions, etc.)
                rr.log(f"{entity_path}/w", rr.Scalars([float(values[0])]))
                rr.log(f"{entity_path}/x", rr.Scalars([float(values[1])]))
                rr.log(f"{entity_path}/y", rr.Scalars([float(values[2])]))
                rr.log(f"{entity_path}/z", rr.Scalars([float(values[3])]))

            elif num_axes == 5 and "GPS" in stream_name:
                # GPS data (lat, lon, alt, speed2d, speed3d)
                rr.log(f"{entity_path}/latitude", rr.Scalars([float(values[0])]))
                rr.log(f"{entity_path}/longitude", rr.Scalars([float(values[1])]))
                rr.log(f"{entity_path}/altitude", rr.Scalars([float(values[2])]))
                rr.log(f"{entity_path}/speed_2d", rr.Scalars([float(values[3])]))
                rr.log(f"{entity_path}/speed_3d", rr.Scalars([float(values[4])]))

                # Log as 3D point (for map view)
                # Convert lat/lon to approximate local coords (simplified)
                # In production, you'd use proper projection
                rr.log(
                    f"{entity_path}/position",
                    rr.Points3D(
                        [[float(values[1]), float(values[0]), float(values[2])]],
                        radii=[2.0],
                    ),
                )

            else:
                # Generic multi-axis data - log each axis
                for axis_idx in range(num_axes):
                    rr.log(
                        f"{entity_path}/axis_{axis_idx}",
                        rr.Scalars([float(values[axis_idx])]),
                    )

    print(f"Logged {len(stream.timestamps)} samples for {stream_name}")


def visualize(
    telemetry: "GoProTelemetry",
    video_path: Optional[str] = None,
    spawn: bool = True,
):
    """Quick visualization of GoPro telemetry with Rerun.

    This is a convenience function that initializes Rerun, logs the data,
    and optionally spawns the viewer.

    Args:
        telemetry: GoProTelemetry object with parsed data
        video_path: Optional path to video file
        spawn: If True, spawn the Rerun viewer

    Example:
        >>> import gopropy
        >>> from gopropy.visualization import visualize
        >>>
        >>> telemetry = gopropy.load("GOPR0001.MP4")
        >>> visualize(telemetry, video_path="GOPR0001.MP4")

    Raises:
        ImportError: If rerun-sdk is not installed
    """
    try:
        import rerun as rr
    except ImportError:
        raise ImportError(
            "rerun-sdk is required for visualization. "
            "Install it with: pip install gopropy[visualization]"
        )

    # Initialize Rerun
    app_id = f"gopro_{telemetry.filepath.stem}"
    rr.init(app_id, spawn=spawn)

    # Log the data
    print("Logging telemetry data to Rerun...")
    to_rerun(telemetry, video_path)
    print("✓ Done! Check the Rerun viewer.")
