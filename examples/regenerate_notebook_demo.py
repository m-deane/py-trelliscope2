"""Regenerate notebook_demo display with fixed viewer code."""

import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent.parent))

import matplotlib.pyplot as plt
import pandas as pd

from trelliscope import Display
from trelliscope.meta import FactorMeta, NumberMeta


def create_simple_plot(category, value):
    """Create a simple bar plot - EXACT function from working version."""
    fig, ax = plt.subplots(figsize=(5, 5))
    ax.bar(
        [category],
        [value],
        color=["#1f77b4", "#ff7f0e", "#2ca02c", "#d62728", "#9467bd"][
            ord(category) - ord("A")
        ],
    )
    ax.set_ylim(0, 35)
    ax.set_title(f"Category {category}")
    ax.set_ylabel("Value")
    plt.tight_layout()
    return fig


def main():
    """Regenerate notebook_demo display."""
    print("Regenerating notebook_demo display with fixed viewer code...")

    # Create data - EXACT pattern
    data = {
        "category": ["A", "B", "C", "D", "E"],
        "value": [10, 25, 15, 30, 20],
        "panel": [],
    }

    # Create matplotlib figures
    for cat, val in zip(data["category"], data["value"]):
        fig = create_simple_plot(cat, val)
        data["panel"].append(fig)

    df = pd.DataFrame(data)

    # Create display - EXACT pattern
    display = Display(
        df, name="notebook_demo", description="Notebook Demo - Exact Working Pattern"
    )
    display.set_panel_column("panel")

    # Add explicit meta variables
    display.add_meta_variable(
        FactorMeta(
            varname="category", label="Category", levels=["A", "B", "C", "D", "E"]
        )
    )
    display.add_meta_variable(NumberMeta(varname="value", label="Value"))

    # Set default layout
    display.set_default_layout(ncol=3, nrow=None, arrangement="row")
    display.set_default_labels(["category", "value"])

    # Write display with fixed viewer code
    output_dir = Path("examples/output/notebook_demo")
    display.write(output_path=output_dir, force=True, viewer_debug=False)

    print(f"✓ Display regenerated at: {output_dir}")
    print(f"\nTo view:")
    print(f"  1. Server already running on port 8762")
    print(f"  2. Open: http://localhost:8762/")
    print(f"\nExpected result: 5 panels displayed correctly!")

    # Close matplotlib figures
    plt.close("all")


if __name__ == "__main__":
    main()
