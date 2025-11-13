"""Verification script to test viewer fix for blank page issue.

This script creates a minimal display and verifies that the generated HTML
uses the correct JavaScript filename (trelliscope-viewer.js).
"""

import sys
from pathlib import Path

# Add project to path
sys.path.insert(0, str(Path(__file__).parent.parent))

import matplotlib.pyplot as plt
import pandas as pd

from trelliscope import Display

print("=" * 70)
print("VIEWER FIX VERIFICATION")
print("=" * 70)

# Create minimal test data
print("\n1. Creating test data...")
data = pd.DataFrame(
    {
        "id": [1, 2, 3],
        "value": [10, 20, 30],
    }
)


# Create simple panels
def make_panel(row):
    fig, ax = plt.subplots(figsize=(4, 3))
    ax.bar(["Value"], [row["value"]])
    ax.set_title(f"ID {row['id']}")
    ax.set_ylim(0, 35)
    plt.tight_layout()
    return fig


print("2. Generating panels...")
data["panel"] = data.apply(make_panel, axis=1)

# Create display
print("3. Creating display...")
output_dir = Path(__file__).parent / "verification_test"
display = (
    Display(data, name="viewer_fix_test", path=output_dir)
    .set_panel_column("panel")
    .infer_metas()
    .set_default_layout(nrow=1, ncol=3)
)

# Write display
print("4. Writing display...")
output_path = display.write(force=True)

# Generate viewer HTML manually
print("5. Generating viewer HTML...")
from trelliscope.viewer import generate_viewer_html, write_index_html

html = generate_viewer_html(display_name="viewer_fix_test", viewer_version="latest")
index_html = output_dir / "index.html"
write_index_html(index_html, html)

# Verify the HTML has the correct filename
print("6. Verifying generated HTML...")
html_content = index_html.read_text()

# Check for correct filename (UMD build)
if "trelliscope-viewer.umd.cjs" in html_content:
    print("   ✅ PASS: HTML uses correct filename 'trelliscope-viewer.umd.cjs'")
else:
    print("   ❌ FAIL: HTML does not contain 'trelliscope-viewer.umd.cjs'")
    sys.exit(1)

# Check for versioned CDN URL
if "@0.7.16" in html_content:
    print("   ✅ PASS: HTML uses specific version '@0.7.16'")
else:
    print("   ❌ FAIL: HTML does not use versioned CDN URL")
    sys.exit(1)

# Check it doesn't have the wrong ESM build
if (
    "trelliscope-viewer.js" in html_content
    and "trelliscope-viewer.umd.cjs" not in html_content
):
    print("   ❌ FAIL: HTML uses ESM build instead of UMD build")
    sys.exit(1)
else:
    print("   ✅ PASS: HTML uses UMD build (not ESM)")

# Check displayInfo.json has required fields
print("\n7. Verifying displayInfo.json...")
import json

display_info_path = output_dir / "viewer_fix_test" / "displayInfo.json"
display_info = json.loads(display_info_path.read_text())

panel_interface = display_info.get("panelInterface", {})
if panel_interface.get("format") == "png":
    print("   ✅ PASS: panelInterface has 'format' field set to 'png'")
else:
    print("   ❌ FAIL: panelInterface missing 'format' field")
    sys.exit(1)

if panel_interface.get("base") == "./panels":
    print("   ✅ PASS: panelInterface has 'base' field set to './panels'")
else:
    print("   ❌ FAIL: panelInterface missing 'base' field")
    sys.exit(1)

# Check panels were rendered
print("\n8. Verifying panels were rendered...")
panels_dir = output_dir / "viewer_fix_test" / "panels"
panel_files = list(panels_dir.glob("*.png"))
if len(panel_files) == 3:
    print(f"   ✅ PASS: Found {len(panel_files)} panel files")
else:
    print(f"   ❌ FAIL: Expected 3 panels, found {len(panel_files)}")
    sys.exit(1)

print("\n" + "=" * 70)
print("✅ ALL CHECKS PASSED!")
print("=" * 70)
print(f"\nOutput written to: {output_path}")
print("\nTo test in browser:")
print(f"  cd {output_dir}")
print(f"  python -m http.server 9999")
print(f"  Open: http://localhost:9999/index.html")
print("\nExpected result: Viewer should display 3 bar charts in a row")
print("=" * 70)
