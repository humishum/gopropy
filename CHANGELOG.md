# Changelog

All notable changes to this project will be documented in this file.

The format is based on [Keep a Changelog](https://keepachangelog.com/en/1.0.0/),
and this project adheres to [Semantic Versioning](https://semver.org/spec/v2.0.0.html).

## [0.1.0] - 2024-12-27

### Added
- Initial release of GoPro-Py
- Extract telemetry from GoPro MP4 files (GPMF format)
- Support for multiple sensor streams:
  - Accelerometer (ACCL)
  - Gyroscope (GYRO)
  - GPS (GPS5, GPS9)
  - Camera Orientation (CORI)
  - Image Orientation (IORI)
  - Gravity Vector (GRAV)
  - Exposure, ISO, White Balance
  - Audio levels, microphone wet detection
  - Scene classification, image uniformity
- Model-specific configuration system
  - Auto-detection from MP4 metadata
  - Manual model override capability
  - Support for Hero5 through Hero13 cameras
- Correct axis ordering handling:
  - Z, X, Y for IMU sensors (ACCL, GYRO)
  - W, X, Y, Z for quaternion sensors (CORI, IORI)
- Multiple export formats:
  - CSV (one file per stream)
  - JSON (single file)
  - HDF5 (with h5py)
  - NumPy NPZ (compressed)
- Pandas DataFrame integration
- NumPy array support
- Optional Rerun visualization support
- Comprehensive documentation and examples

### Fixed
- Corrected quaternion ordering (w, x, y, z instead of x, y, z, w)
- Proper handling of GoPro's non-standard axis ordering

## [Unreleased]

### Planned
- Add unit tests
- Add continuous integration
- Support for more GoPro models (MAX, Fusion, etc.)
- Performance optimizations
- Additional visualization tools

