#!/usr/bin/env python
"""Test viewer setup and diagnose issues."""

import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent.parent))

import matplotlib.pyplot as plt
import numpy as np
import pandas as pd

from trelliscope import Display

print("=" * 60)
print("VIEWER DIAGNOSTIC TEST")
print("=" * 60)

# Create simple test data
np.random.seed(42)
data = pd.DataFrame(
    {
        "id": range(5),
        "value": np.random.randn(5) * 100 + 500,
        "category": ["A", "B", "C", "A", "B"],
    }
)

print(f"\n1. Created test DataFrame with {len(data)} rows")


# Create simple plots
def make_plot(row):
    fig, ax = plt.subplots(figsize=(4, 3))
    ax.bar(["Value"], [row["value"]])
    ax.set_title(f"ID {row['id']} - {row['category']}")
    plt.tight_layout()
    return fig


data["panel"] = data.apply(make_plot, axis=1)
print(f"2. Generated {len(data)} matplotlib figures")

# Create test output directory
test_dir = Path("test_viewer_output")
test_dir.mkdir(exist_ok=True)
print(f"3. Created output directory: {test_dir}")

# Create and write display
display = (
    Display(data, name="viewer_test", path=test_dir)
    .set_panel_column("panel")
    .infer_metas()
)

output_path = display.write(force=True)
print(f"4. Display written to: {output_path}")

# Check files created
print(f"\n5. Verifying files...")
display_info = output_path / "displayInfo.json"
metadata_csv = output_path / "metadata.csv"
panels_dir = output_path / "panels"

print(f"   - displayInfo.json exists: {display_info.exists()}")
print(f"   - metadata.csv exists: {metadata_csv.exists()}")
print(f"   - panels/ directory exists: {panels_dir.exists()}")

if panels_dir.exists():
    panel_files = list(panels_dir.glob("*.png"))
    print(f"   - Panel files: {len(panel_files)} PNG files")

# Check displayInfo.json content
import json

with open(display_info) as f:
    info = json.load(f)

print(f"\n6. Checking displayInfo.json structure...")
print(f"   - name: {info.get('name')}")
print(f"   - metas: {len(info.get('metas', []))} metadata variables")
print(f"   - panelInterface: {json.dumps(info.get('panelInterface'), indent=6)}")

# Test viewer
print(f"\n7. Starting viewer...")
print(f"   If browser doesn't open, manually navigate to the URL shown")
print(f"   Press Ctrl+C to stop the server when done\n")

try:
    url = display.view(port=9999, open_browser=True, blocking=True)
except KeyboardInterrupt:
    print("\n\nServer stopped by user")
    print("\n" + "=" * 60)
    print("TEST COMPLETE")
    print("=" * 60)
