"""
Test debug viewer mode.

Creates a simple display with debug viewer enabled to verify
the debug console and logging features work correctly.
"""

from pathlib import Path

import matplotlib.pyplot as plt
import pandas as pd

from trelliscope import Display
from trelliscope.meta import FactorMeta, NumberMeta


def create_simple_plot(label, value):
    """Create a simple plot."""
    fig, ax = plt.subplots(figsize=(4, 4))
    ax.bar([label], [value])
    ax.set_ylim(0, 50)
    ax.set_title(f"{label}")
    plt.tight_layout()
    return fig


def main():
    """Create display with debug viewer."""
    # Create data
    data = {"label": ["X", "Y", "Z"], "value": [10, 30, 20], "panel": []}

    # Create figures
    for label, val in zip(data["label"], data["value"]):
        fig = create_simple_plot(label, val)
        data["panel"].append(fig)

    df = pd.DataFrame(data)

    # Create display
    print("Creating display with DEBUG viewer...")
    display = Display(df, name="debug_test", description="Debug Viewer Test")
    display.set_panel_column("panel")
    display.add_meta_variable(FactorMeta("label", levels=["X", "Y", "Z"]))
    display.add_meta_variable(NumberMeta("value"))

    # Write with debug enabled
    output_dir = Path("examples/output/debug_viewer_test")
    display.write(
        output_path=output_dir, force=True, viewer_debug=True  # Enable debug mode
    )

    print(f"\n✓ Display created with debug viewer at: {output_dir}")
    print(f"\nTo test:")
    print(f"  1. cd {output_dir}")
    print(f"  2. python -m http.server 8001")
    print(f"  3. Open http://localhost:8001/")
    print(f"  4. Check the debug console at the bottom of the page")

    plt.close("all")


if __name__ == "__main__":
    main()
