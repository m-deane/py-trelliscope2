"""
End-to-end example demonstrating REST panel integration.

This example shows how to create a trelliscope display that loads panels
via REST API instead of pre-rendered files, enabling dynamic panel generation
and reduced storage requirements.

Prerequisites:
    - Panel server running on http://localhost:5001 (run panel_server.py)
    - Forked viewer copied to trelliscope/viewer/ directory
"""

import sys
from pathlib import Path

import pandas as pd

# Add parent directory to path for imports
sys.path.insert(0, str(Path(__file__).parent.parent))

from trelliscope import (
    Display,
    FactorMeta,
    NumberMeta,
    RESTPanelInterface,
)


def create_rest_panel_display():
    """
    Create a display with REST panel interface.

    This creates a minimal display that references panels served by the
    panel_server.py REST API instead of pre-rendered panel files.
    """
    print("=" * 80)
    print("REST PANEL INTEGRATION - END-TO-END EXAMPLE")
    print("=" * 80)
    print()

    # Step 1: Create sample data
    print("Step 1: Creating sample data...")
    data = pd.DataFrame(
        {
            "id": [0, 1, 2],
            "value": [0, 10, 20],
            "category": ["A", "B", "C"],
            "panel": ["0", "1", "2"],  # Panel IDs for REST API
        }
    )
    print(f"  Created {len(data)} rows")
    print()

    # Step 2: Create display
    print("Step 2: Creating display...")
    display = Display(
        data, name="rest_demo", description="Demonstration of REST panel loading"
    )
    print(f"  Display name: {display.name}")
    print()

    # Step 3: Set panel column
    print("Step 3: Setting panel column...")
    display.set_panel_column("panel")
    print(f"  Panel column: {display.panel_column}")
    print()

    # Step 4: Configure REST panel interface
    print("Step 4: Configuring REST panel interface...")
    interface = RESTPanelInterface(
        base="http://localhost:5001/api/panels/minimal_manual", port=5001
    )
    display.set_panel_interface(interface)
    print(f"  Interface type: REST")
    print(f"  Base URL: {interface.base}")
    print(f"  Port: {interface.port}")
    print()

    # Step 5: Add metadata (cognostics)
    print("Step 5: Adding metadata...")
    display.add_meta_variable(NumberMeta("value", label="Value", digits=2))
    display.add_meta_variable(
        FactorMeta("category", label="Category", levels=["A", "B", "C"])
    )
    print(f"  Added {len(display.list_meta_variables())} meta variables")
    print()

    # Step 6: Configure display layout
    print("Step 6: Configuring layout...")
    display.set_default_layout(ncol=3, nrow=1)
    display.set_default_labels(["category", "value"])
    display.set_panel_options(aspect=1.0)
    print(f"  Layout: {display.state['layout']['ncol']} columns")
    print(f"  Labels: {display.state['labels']}")
    print()

    # Step 7: Write display (without rendering panels)
    print("Step 7: Writing display...")
    output_path = Path("./examples/output/rest_demo")
    display.write(
        output_path=output_path,
        force=True,
        render_panels=False,  # Don't render panels - they come from REST API
    )
    print(f"  Output: {output_path}")
    print()

    # Step 8: Verify displayInfo.json
    print("Step 8: Verifying displayInfo.json...")
    display_info_path = output_path / "displayInfo.json"
    if display_info_path.exists():
        print(f"  ✓ displayInfo.json created")

        # Read and display relevant sections
        import json

        with open(display_info_path) as f:
            display_info = json.load(f)

        print(f"  ✓ Display name: {display_info['name']}")
        print(f"  ✓ Number of panels: {display_info['n']}")
        print(f"  ✓ Primary panel: {display_info.get('primarypanel', 'N/A')}")

        # Find panel meta in metas array
        panel_meta = None
        for meta in display_info["metas"]:
            if meta["type"] == "panel":
                panel_meta = meta
                break

        if panel_meta:
            print(f"  ✓ Panel meta found:")
            print(f"    - varname: {panel_meta['varname']}")
            print(f"    - paneltype: {panel_meta['paneltype']}")
            print(f"    - aspect: {panel_meta['aspect']}")
            print(f"    - source.type: {panel_meta['source']['type']}")
            print(f"    - source.url: {panel_meta['source']['url']}")
            print(f"    - source.isLocal: {panel_meta['source']['isLocal']}")
        else:
            print(f"  ✗ Panel meta not found in metas array!")
    else:
        print(f"  ✗ displayInfo.json not found!")
    print()

    # Step 9: Copy forked viewer
    print("Step 9: Setting up viewer...")
    viewer_src = Path(__file__).parent.parent / "trelliscope" / "viewer"
    if viewer_src.exists():
        import shutil

        # Copy viewer files to output directory
        for file in ["index.html"]:
            if (viewer_src / file).exists():
                shutil.copy(viewer_src / file, output_path.parent / file)
        assets_dir = viewer_src / "assets"
        if assets_dir.exists():
            target_assets = output_path.parent / "assets"
            if target_assets.exists():
                shutil.rmtree(target_assets)
            shutil.copytree(assets_dir, target_assets)
        print(f"  ✓ Viewer files copied")
    else:
        print(f"  ✗ Viewer not found at {viewer_src}")
        print(f"  ⚠️  You need to copy the forked viewer to trelliscope/viewer/")
    print()

    # Step 10: Instructions for testing
    print("Step 10: Testing instructions")
    print("-" * 80)
    print("To test the REST panel integration:")
    print()
    print("1. Ensure panel server is running:")
    print("   $ python examples/panel_server.py")
    print()
    print("2. Verify server health:")
    print("   $ curl http://localhost:5001/api/health")
    print()
    print("3. Test panel endpoint:")
    print("   $ curl -I http://localhost:5001/api/panels/minimal_manual/0")
    print("   Should return: HTTP/1.1 200 OK, Content-Type: image/png")
    print()
    print("4. Open viewer in browser:")
    print(f"   http://localhost:5001/rest_demo")
    print()
    print("5. Check browser console:")
    print("   - Look for network requests to /api/panels/minimal_manual/{0,1,2}")
    print("   - All requests should return 200 OK")
    print("   - Panels should render in viewer")
    print()
    print("6. Inspect displayInfo.json:")
    print(f"   $ cat {display_info_path}")
    print("   - Look for panel meta with source.type='REST'")
    print("   - Verify source.url matches panel server")
    print()
    print("=" * 80)
    print("INTEGRATION COMPLETE!")
    print("=" * 80)
    print()

    return display


def verify_panel_server():
    """Verify panel server is accessible."""
    import requests

    print("Verifying panel server...")
    try:
        response = requests.get("http://localhost:5001/api/health", timeout=2)
        if response.status_code == 200:
            health = response.json()
            print(f"  ✓ Panel server is running")
            print(f"    Output dir: {health.get('output_dir')}")
            print(f"    Displays dir exists: {health.get('displays_dir_exists')}")
            return True
        else:
            print(f"  ✗ Server returned status {response.status_code}")
            return False
    except requests.exceptions.RequestException as e:
        print(f"  ✗ Cannot connect to panel server: {e}")
        print(f"  ⚠️  Make sure panel_server.py is running on port 5001")
        return False


def test_panel_endpoint():
    """Test individual panel endpoint."""
    import requests

    print("\nTesting panel endpoint...")
    try:
        response = requests.head(
            "http://localhost:5001/api/panels/minimal_manual/0", timeout=2
        )
        if response.status_code == 200:
            print(f"  ✓ Panel endpoint responding")
            print(f"    Status: {response.status_code}")
            print(f"    Content-Type: {response.headers.get('Content-Type')}")
            return True
        else:
            print(f"  ✗ Panel endpoint returned status {response.status_code}")
            return False
    except requests.exceptions.RequestException as e:
        print(f"  ✗ Cannot reach panel endpoint: {e}")
        return False


if __name__ == "__main__":
    # Verify prerequisites
    server_ok = verify_panel_server()
    panel_ok = test_panel_endpoint()

    if not server_ok or not panel_ok:
        print("\n⚠️  Prerequisites not met. Please start panel server:")
        print("   python examples/panel_server.py")
        sys.exit(1)

    print()
    # Create the display
    display = create_rest_panel_display()

    print("\n✅ Example completed successfully!")
    print("\nNext steps:")
    print("  1. Open http://localhost:5001/rest_demo in browser")
    print("  2. Verify panels load via REST API (check Network tab)")
    print("  3. Interact with display (filter, sort, labels)")
