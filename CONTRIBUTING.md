# Contributing to GoPro-Py

Thank you for your interest in contributing to GoPro-Py! This document provides guidelines and instructions for contributing.

## Getting Started

### Development Setup

1. **Clone the repository:**
   ```bash
   git clone https://github.com/yourusername/gopro-py.git
   cd gopro-py
   ```

2. **Install dependencies:**
   ```bash
   pip install -e ".[dev,all]"
   ```

3. **Verify installation:**
   ```bash
   python -c "import gopropy; print(gopropy.__version__)"
   ```

## Development Workflow

### Code Style

We use:
- **Black** for code formatting
- **Ruff** for linting

Run before committing:
```bash
black src/ examples/
ruff check src/
```

### Testing

Run tests (when available):
```bash
pytest tests/
```

### Adding New Features

1. Create a feature branch
2. Implement your changes
3. Add/update documentation
4. Add tests if applicable
5. Submit a pull request

## Model-Specific Configurations

When adding support for new GoPro models:

1. **Update `src/gopropy/models.py`:**
   - Add the new model configuration
   - Document FourCC codes added/changed
   - Set up inheritance from previous model
   - Specify axis ordering if changed

2. **Update documentation:**
   - Run `python scripts/generate_model_docs.py`
   - Update README.md if needed

3. **Test with actual data:**
   - Verify model detection works
   - Validate axis ordering
   - Check all sensor streams

### Axis Ordering

Be careful with axis ordering:
- **IMU sensors (ACCL, GYRO):** Use Z, X, Y (GoPro standard)
- **Quaternions (CORI, IORI):** Use W, X, Y, Z (scalar-first)
- **Verify with actual data** - don't assume!

## Documentation

- Keep README.md up to date
- Add docstrings to all public functions
- Update CHANGELOG.md for notable changes
- Add examples for new features

## Reporting Issues

When reporting bugs, please include:
- GoPro model and firmware version
- Python version
- Code to reproduce the issue
- Error messages/stack traces
- Sample data if possible (small file)

## Code of Conduct

- Be respectful and inclusive
- Provide constructive feedback
- Focus on the code, not the person
- Help others learn

## Questions?

Open an issue with the "question" label for any questions about contributing.

## License

By contributing, you agree that your contributions will be licensed under the MIT License.

