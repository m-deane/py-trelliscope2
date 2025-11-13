"""
Test script to verify notebook display generation.

This script replicates the notebook workflow to ensure displays are generated
correctly with the multi-display structure and proper panel configuration.
"""

import json
from pathlib import Path

import matplotlib.pyplot as plt
import numpy as np
import pandas as pd

from trelliscope import Display


def make_plot(row):
    """Create a simple plot based on row data."""
    fig, ax = plt.subplots(figsize=(6, 4))

    # Generate some data based on row values
    x = np.linspace(0, 10, 100)
    y = np.sin(x + row["value"] / 100) * row["score"]

    ax.plot(x, y, linewidth=2)
    ax.set_title(f"Category {row['category']} - ID {row['id']}")
    ax.set_xlabel("X")
    ax.set_ylabel("Y")
    ax.grid(True, alpha=0.3)

    plt.tight_layout()
    return fig


def verify_multi_display_structure(output_path: Path, display_name: str) -> bool:
    """Verify that all required files exist with correct structure."""
    print("\n" + "=" * 60)
    print("VERIFYING MULTI-DISPLAY STRUCTURE")
    print("=" * 60)

    all_valid = True

    # Root files
    root_files = {
        "index.html": output_path / "index.html",
        "config.json": output_path / "config.json",
    }

    print("\n1. Root Files:")
    for name, path in root_files.items():
        exists = path.exists()
        status = "✓" if exists else "✗"
        print(f"  {status} {name}")
        if not exists:
            all_valid = False

    # Display directory files
    display_dir = output_path / "displays" / display_name
    display_files = {
        "displayList.json": output_path / "displays" / "displayList.json",
        "displayInfo.json": display_dir / "displayInfo.json",
        "metaData.json": display_dir / "metaData.json",
        "metaData.js": display_dir / "metaData.js",
        "metadata.csv": display_dir / "metadata.csv",
    }

    print("\n2. Display Files:")
    for name, path in display_files.items():
        exists = path.exists()
        status = "✓" if exists else "✗"
        print(f"  {status} {name}")
        if not exists:
            all_valid = False

    # Check panels directory
    panels_dir = display_dir / "panels"
    panels_exist = panels_dir.exists() and panels_dir.is_dir()
    status = "✓" if panels_exist else "✗"
    print(f"\n3. Panels Directory:")
    print(f"  {status} panels/")
    if panels_exist:
        panel_files = list(panels_dir.glob("*.png"))
        print(f"      Found {len(panel_files)} panel images")
    else:
        all_valid = False

    return all_valid


def verify_display_info_content(output_path: Path, display_name: str) -> bool:
    """Verify displayInfo.json has correct content."""
    print("\n" + "=" * 60)
    print("VERIFYING DISPLAYINFO.JSON CONTENT")
    print("=" * 60)

    display_info_path = output_path / "displays" / display_name / "displayInfo.json"

    if not display_info_path.exists():
        print("\n✗ displayInfo.json not found!")
        return False

    with open(display_info_path, "r", encoding="utf-8") as f:
        info = json.load(f)

    all_valid = True

    # Check critical fields
    checks = {
        "name": info.get("name") == display_name,
        "n (panel count)": info.get("n", 0) > 0,
        "primarypanel": info.get("primarypanel") == "panel",
        "panelInterface exists": "panelInterface" in info,
        "cogData exists": "cogData" in info and len(info.get("cogData", [])) > 0,
        "cogInterface exists": "cogInterface" in info,
    }

    print("\n1. Required Fields:")
    for field, valid in checks.items():
        status = "✓" if valid else "✗"
        print(f"  {status} {field}")
        if not valid:
            all_valid = False

    # Check panelInterface configuration
    if "panelInterface" in info:
        pi = info["panelInterface"]
        pi_checks = {
            "type == 'file'": pi.get("type") == "file",
            "base == 'panels'": pi.get("base") == "panels",
            "panelCol == 'panel'": pi.get("panelCol") == "panel",
        }

        print("\n2. panelInterface Configuration:")
        for check, valid in pi_checks.items():
            status = "✓" if valid else "✗"
            print(f"  {status} {check}")
            if not valid:
                all_valid = False
                print(f"      Actual: {json.dumps(pi, indent=4)}")

    # Check panel meta in metas array
    metas = info.get("metas", [])
    panel_meta = None
    for meta in metas:
        if meta.get("varname") == "panel":
            panel_meta = meta
            break

    print("\n3. Panel Meta in Metas Array:")
    if panel_meta:
        print(f"  ✓ Panel meta found")
        meta_checks = {
            "type == 'panel'": panel_meta.get("type") == "panel",
            "paneltype == 'img'": panel_meta.get("paneltype") == "img",
            "has source": "source" in panel_meta,
        }
        for check, valid in meta_checks.items():
            status = "✓" if valid else "✗"
            print(f"    {status} {check}")
            if not valid:
                all_valid = False
    else:
        print(f"  ✗ Panel meta NOT FOUND in metas array")
        all_valid = False

    # Check cogData panel references
    if "cogData" in info:
        cog_data = info["cogData"]
        if len(cog_data) > 0:
            first_entry = cog_data[0]
            panel_ref = first_entry.get("panel")

            print("\n4. cogData Panel References:")
            if panel_ref:
                # Should be just "0.png", not "panels/0.png" (base path is in panelInterface)
                correct_format = panel_ref.endswith(".png") and "/" not in panel_ref
                status = "✓" if correct_format else "✗"
                print(f"  {status} Panel reference format: '{panel_ref}'")
                if not correct_format:
                    print(f"      Expected format: '0.png' (no path prefix)")
                    all_valid = False
            else:
                print(f"  ✗ No panel reference in cogData")
                all_valid = False

    return all_valid


def main():
    """Run the notebook workflow test."""
    print("=" * 60)
    print("NOTEBOOK DISPLAY GENERATION TEST")
    print("=" * 60)

    # Create sample data (matching notebook)
    print("\n1. Creating sample data...")
    np.random.seed(42)
    data = pd.DataFrame(
        {
            "id": range(20),
            "value": np.random.randn(20) * 100 + 500,
            "category": np.random.choice(["A", "B", "C"], 20),
            "score": np.random.uniform(0, 100, 20),
        }
    )
    print(f"   Created DataFrame with {len(data)} rows")

    # Generate plots
    print("\n2. Generating plots...")
    data["panel"] = data.apply(make_plot, axis=1)
    print(f"   Generated {len(data)} matplotlib figures")

    # Create display
    print("\n3. Creating display...")
    output_dir = Path("examples/output/notebook_test")
    output_dir.mkdir(parents=True, exist_ok=True)

    display = (
        Display(data, name="basic_viewer_demo", path=output_dir)
        .set_panel_column("panel")
        .infer_metas()
        .set_default_layout(nrow=2, ncol=3)
    )
    print(f"   Display created: '{display.name}'")

    # Write display
    print("\n4. Writing display...")
    output_path = display.write(force=True)
    print(f"   Output path: {output_path}")

    # Close matplotlib figures
    plt.close("all")

    # Verify structure
    structure_valid = verify_multi_display_structure(output_path, "basic_viewer_demo")

    # Verify content
    content_valid = verify_display_info_content(output_path, "basic_viewer_demo")

    # Final result
    print("\n" + "=" * 60)
    print("FINAL RESULT")
    print("=" * 60)

    if structure_valid and content_valid:
        print("\n✓ ALL CHECKS PASSED!")
        print("\nThe notebook display has been generated correctly.")
        print("\nTo view the display:")
        print(f"  1. cd {output_path}")
        print(f"  2. python -m http.server 8888")
        print(f"  3. Open http://localhost:8888/")
        print("\nExpected result: Viewer shows 20 panels (not '0 of 0')")
    else:
        print("\n✗ SOME CHECKS FAILED!")
        print("\nPlease review the errors above.")
        return 1

    return 0


if __name__ == "__main__":
    exit(main())
