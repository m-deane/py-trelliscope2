"""
Simple static panel example - Approach 2
Uses CDN viewer with pre-rendered PNG files (no REST API needed)
"""

import sys
from pathlib import Path

import matplotlib.pyplot as plt
import numpy as np
import pandas as pd

# Add parent directory to path
sys.path.insert(0, str(Path(__file__).parent.parent))

from trelliscope import Display


def create_simple_plot(value, category):
    """Create a simple matplotlib plot"""
    fig, ax = plt.subplots(figsize=(5, 5))

    # Simple bar chart
    ax.bar([category], [value], color="steelblue")
    ax.set_ylabel("Value", fontsize=12)
    ax.set_title(f"{category}: {value}", fontsize=14, fontweight="bold")
    ax.set_ylim(0, max(value + 10, 30))
    ax.grid(True, alpha=0.3)

    plt.tight_layout()
    return fig


def main():
    print("Creating simple static panel display...")

    # Create simple data
    data = pd.DataFrame(
        {
            "id": [0, 1, 2, 3, 4],
            "value": [10, 25, 15, 30, 20],
            "category": ["A", "B", "C", "D", "E"],
        }
    )

    # Generate plots and save to temporary files
    panel_paths = []
    output_dir = Path(__file__).parent / "output" / "simple_static" / "panels"
    output_dir.mkdir(parents=True, exist_ok=True)

    for idx, row in data.iterrows():
        fig = create_simple_plot(row["value"], row["category"])
        panel_path = output_dir / f"panel_{idx}.png"
        fig.savefig(panel_path, dpi=100, bbox_inches="tight")
        plt.close(fig)
        panel_paths.append(str(panel_path.name))
        print(f"  Created {panel_path.name}")

    # Add panel column with just filenames (relative to panels/ dir)
    data["panel"] = panel_paths

    # Create display WITHOUT setting panel_interface
    # This will default to local file-based panels
    display = (
        Display(data, name="simple_static", description="Simple Static Panel Example")
        .set_panel_column("panel")
        .infer_metas()
        .set_default_layout(ncol=3)
        .set_default_labels(["category", "value"])
    )

    # Write display (render_panels=False since we already rendered them)
    output_path = Path(__file__).parent / "output" / "simple_static"
    display.write(output_path=output_path, render_panels=False, force=True)

    print(f"\n✓ Display created at: {output_path}")
    print(f"  - displayInfo.json")
    print(f"  - metadata.csv")
    print(f"  - panels/ directory with {len(panel_paths)} PNG files")
    print(f"\nNext: Open simple_static_viewer.html in a browser")

    return display


if __name__ == "__main__":
    display = main()
