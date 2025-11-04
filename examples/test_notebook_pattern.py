"""
Test that the notebook pattern produces the same configuration as the working version.

This script replicates the exact pattern from the updated notebook to verify
that it generates a working display configuration.
"""

import pandas as pd
import matplotlib.pyplot as plt
from pathlib import Path
import json

from trelliscope import Display
from trelliscope.meta import FactorMeta, NumberMeta


def create_simple_plot(category, value):
    """Create a simple bar plot - EXACT function from working version."""
    fig, ax = plt.subplots(figsize=(5, 5))
    ax.bar([category], [value], color=['#1f77b4', '#ff7f0e', '#2ca02c', '#d62728', '#9467bd'][ord(category) - ord('A')])
    ax.set_ylim(0, 35)
    ax.set_title(f"Category {category}")
    ax.set_ylabel("Value")
    plt.tight_layout()
    return fig


def main():
    """Test notebook pattern."""
    print("Testing Notebook Pattern")
    print("=" * 60)

    # EXACT PATTERN from notebook
    # Create data - EXACT pattern: dict first, then DataFrame
    data = {
        "category": ["A", "B", "C", "D", "E"],
        "value": [10, 25, 15, 30, 20],
        "panel": []  # Will be populated with figures
    }

    # Create matplotlib figures - EXACT loop pattern
    for cat, val in zip(data["category"], data["value"]):
        fig = create_simple_plot(cat, val)
        data["panel"].append(fig)

    # Convert to DataFrame
    df = pd.DataFrame(data)

    # Create display - EXACT pattern: no method chaining initially
    display = Display(df, name="notebook_pattern_test", description="Testing Notebook Pattern")

    # Set panel column
    display.set_panel_column("panel")

    # Add meta variables - EXPLICIT FactorMeta and NumberMeta
    display.add_meta_variable(
        FactorMeta(varname="category", label="Category", levels=["A", "B", "C", "D", "E"])
    )
    display.add_meta_variable(
        NumberMeta(varname="value", label="Value")
    )

    # Set default layout - EXACT parameters
    display.set_default_layout(ncol=3, nrow=None, arrangement="row")
    display.set_default_labels(["category", "value"])

    # Write display - EXACT pattern with output_path parameter
    output_dir = Path("examples/output/notebook_pattern_test")
    print(f"Writing display to {output_dir}...")
    display.write(output_path=output_dir, force=True, viewer_debug=False)

    # Close matplotlib figures
    plt.close('all')

    # Verify configuration matches working version
    print("\nVerifying configuration...")

    working_info_path = Path("examples/output/simple_static_test/displays/simple_static/displayInfo.json")
    new_info_path = output_dir / "displays" / "notebook_pattern_test" / "displayInfo.json"

    with open(working_info_path) as f:
        working_info = json.load(f)

    with open(new_info_path) as f:
        new_info = json.load(f)

    # Compare critical fields
    checks = [
        ("panelInterface.type", working_info['panelInterface']['type'], new_info['panelInterface']['type']),
        ("panelInterface.base", working_info['panelInterface']['base'], new_info['panelInterface']['base']),
        ("panelInterface.panelCol", working_info['panelInterface']['panelCol'], new_info['panelInterface']['panelCol']),
        ("primarypanel", working_info['primarypanel'], new_info['primarypanel']),
        ("n (panel count)", working_info['n'], new_info['n']),
    ]

    all_pass = True
    for field, working_val, new_val in checks:
        match = working_val == new_val
        status = "✓" if match else "✗"
        print(f"{status} {field}: {working_val} == {new_val}")
        if not match:
            all_pass = False

    # Check panel meta exists
    panel_meta = None
    for meta in new_info['metas']:
        if meta['varname'] == 'panel':
            panel_meta = meta
            break

    if panel_meta:
        print(f"✓ Panel meta found in metas array")
        print(f"  - type: {panel_meta['type']}")
        print(f"  - paneltype: {panel_meta['paneltype']}")
        print(f"  - source.type: {panel_meta['source']['type']}")
    else:
        print("✗ Panel meta NOT FOUND")
        all_pass = False

    print("\n" + "=" * 60)
    if all_pass:
        print("✅ SUCCESS: Notebook pattern produces correct configuration!")
        print("\nThe notebook pattern matches the working version exactly.")
        print("When users run the notebook, they will get a working display.")
    else:
        print("❌ FAILURE: Configuration mismatch detected")
    print("=" * 60)


if __name__ == "__main__":
    main()
