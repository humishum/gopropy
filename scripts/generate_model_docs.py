#!/usr/bin/env python3
"""Generate model documentation from models.py configuration."""

import sys
from pathlib import Path

# Add src to path
sys.path.insert(0, str(Path(__file__).parent.parent / "src"))

from gopropy.models import GOPRO_MODELS_BASE, build_model_config


def generate_models_markdown() -> str:
    """Generate markdown documentation for all GoPro models."""
    
    lines = ["# GoPro Model Support\n"]
    lines.append("This document details the metadata support for different GoPro camera models.\n")
    lines.append("Based on the official [GPMF Parser documentation](https://github.com/gopro/gpmf-parser).\n")
    lines.append("\n## Supported Models\n")
    
    # Create summary table
    lines.append("| Model | Year | Firmware | Inherits From | Added FourCCs |")
    lines.append("|-------|------|----------|---------------|---------------|")
    
    models = sorted(
        [(k, v) for k, v in GOPRO_MODELS_BASE.items() if k != "GENERIC"],
        key=lambda x: x[1].release_year
    )
    
    for model_name, config in models:
        built = build_model_config(model_name)
        added_count = len(config.added_fourccs)
        inherits = config.inherits_from or "—"
        lines.append(
            f"| {config.display_name} | {config.release_year} | "
            f"{config.firmware_version} | {inherits} | {added_count} |"
        )
    
    # Detailed sections for each model
    lines.append("\n## Model Details\n")
    
    for model_name, config in models:
        built = build_model_config(model_name)
        
        lines.append(f"\n### {config.display_name}\n")
        lines.append(f"**Release Year:** {config.release_year}  ")
        lines.append(f"**Firmware Version:** {config.firmware_version}  ")
        if config.inherits_from:
            lines.append(f"**Inherits From:** {config.inherits_from}  ")
        if config.notes:
            lines.append(f"**Notes:** {config.notes}  ")
        lines.append("")
        
        # Axis ordering
        if config.axis_order:
            lines.append("**Axis Ordering:**")
            for fourcc, axes in sorted(config.axis_order.items()):
                lines.append(f"- `{fourcc}`: {', '.join(axes)}")
            lines.append("")
        
        # Added FourCC codes
        if config.added_fourccs:
            lines.append(f"**Added FourCC Codes ({len(config.added_fourccs)}):**")
            for fourcc in sorted(config.added_fourccs):
                lines.append(f"- `{fourcc}`")
            lines.append("")
        
        # Changed FourCC codes
        if config.changed_fourccs:
            lines.append("**Changed FourCC Codes:**")
            for fourcc, description in sorted(config.changed_fourccs.items()):
                lines.append(f"- `{fourcc}`: {description}")
            lines.append("")
        
        # Total supported FourCC codes
        lines.append(f"**Total Supported FourCC Codes:** {len(built.supported_fourccs)}")
        lines.append("")
    
    # Axis ordering explanation
    lines.append("\n## Axis Ordering\n")
    lines.append("**Important:** GoPro cameras do NOT use standard X, Y, Z axis ordering.\n")
    lines.append("\n### IMU Sensors (Hero5+)\n")
    lines.append("- **ACCL (Accelerometer):** Z, X, Y")
    lines.append("- **GYRO (Gyroscope):** Z, X, Y")
    lines.append("\nThis is documented in the official GPMF parser for Hero5 Black and Session,")
    lines.append("and is assumed to continue for later models.\n")
    lines.append("\n### Orientation Sensors (Hero8+)\n")
    lines.append("- **CORI (Camera Orientation):** X, Y, Z, W (quaternion)")
    lines.append("- **IORI (Image Orientation):** X, Y, Z, W (quaternion)")
    lines.append("- **GRAV (Gravity Vector):** X, Y, Z")
    lines.append("\n### GPS Data\n")
    lines.append("GPS data is not in XYZ format:")
    lines.append("- **GPS5:** Latitude, Longitude, Altitude, 2D Speed, 3D Speed")
    lines.append("- **GPS9:** Latitude, Longitude, Altitude, 2D Speed, 3D Speed, Days since 2000, Seconds since midnight, DOP, Fix")
    lines.append("")
    
    return "\n".join(lines)


def main():
    """Generate and save model documentation."""
    # Create docs directory if it doesn't exist
    docs_dir = Path(__file__).parent.parent / "docs"
    docs_dir.mkdir(exist_ok=True)
    
    # Generate documentation
    markdown = generate_models_markdown()
    
    # Save to file
    output_file = docs_dir / "MODELS.md"
    output_file.write_text(markdown)
    
    print(f"✓ Generated model documentation: {output_file}")
    print(f"  Total models documented: {len([k for k in GOPRO_MODELS_BASE.keys() if k != 'GENERIC'])}")


if __name__ == "__main__":
    main()

