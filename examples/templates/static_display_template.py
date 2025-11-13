"""
Template for Creating Static Panel Trelliscope Displays (Approach 2)

This template demonstrates the complete workflow for creating a trelliscope display
with pre-rendered static panel images (PNG/JPEG). This approach is simpler than
REST panels and requires no server infrastructure.

Usage:
1. Modify the data generation section with your actual data
2. Update the panel generation function with your visualization logic
3. Customize display configuration (name, description, layout, etc.)
4. Run the script to generate the display
5. Open the generated viewer HTML in a browser

Requirements:
- pandas
- matplotlib (or plotly, altair, etc.)
- trelliscope
"""

from pathlib import Path

import matplotlib.pyplot as plt
import pandas as pd

from trelliscope import Display

# ============================================================================
# CONFIGURATION
# ============================================================================

DISPLAY_NAME = "my_static_display"
DISPLAY_DESCRIPTION = "Description of my display"
OUTPUT_DIR = Path(__file__).parent.parent / "output"
PANEL_COLUMN_NAME = "panel"

# Layout configuration
NCOL = 3  # Number of columns in grid
NROW = None  # Number of rows (None for auto)

# Label configuration (columns to show as labels on panels)
LABEL_COLUMNS = ["category", "value"]

# ============================================================================
# 1. DATA GENERATION
# ============================================================================
# Replace this section with your actual data loading/generation


def generate_data() -> pd.DataFrame:
    """
    Generate or load your data here.

    Each row will become one panel in the display.
    Include columns for cognostics (metadata for filtering/sorting).

    Returns:
        DataFrame with one row per panel plus cognostic columns
    """
    data = pd.DataFrame(
        {
            "id": range(10),
            "value": [10, 25, 15, 30, 20, 18, 22, 28, 12, 16],
            "category": ["A", "B", "C", "D", "E", "A", "B", "C", "D", "E"],
            # Add more cognostic columns as needed
            # Examples:
            # 'date': pd.date_range('2024-01-01', periods=10),
            # 'region': ['North', 'South', ...],
            # 'score': [0.85, 0.92, ...],
        }
    )
    return data


# ============================================================================
# 2. PANEL GENERATION
# ============================================================================
# Customize this function to create your visualizations


def create_panel(row: pd.Series, panel_dir: Path, panel_id: int) -> str:
    """
    Create a single panel visualization.

    Args:
        row: DataFrame row containing data for this panel
        panel_dir: Directory to save panel image
        panel_id: Unique ID for this panel

    Returns:
        Filename of saved panel (e.g., "panel_0.png")
    """
    # Create your visualization here
    # This example uses matplotlib, but you can use plotly, altair, etc.

    fig, ax = plt.subplots(figsize=(5, 5))

    # Example visualization - replace with your plotting logic
    ax.bar([row["category"]], [row["value"]], color="steelblue")
    ax.set_ylabel("Value", fontsize=12)
    ax.set_title(f"{row['category']}: {row['value']}", fontsize=14, fontweight="bold")
    ax.set_ylim(0, max(row["value"] + 10, 35))
    ax.grid(True, alpha=0.3)

    plt.tight_layout()

    # Save panel
    panel_filename = f"panel_{panel_id}.png"
    panel_path = panel_dir / panel_filename
    fig.savefig(panel_path, dpi=100, bbox_inches="tight")
    plt.close(fig)

    return panel_filename


# ============================================================================
# 3. GENERATE PANELS
# ============================================================================


def generate_panels(data: pd.DataFrame, output_path: Path) -> pd.DataFrame:
    """
    Generate all panel images and add panel column to data.

    Args:
        data: Input DataFrame
        output_path: Base output directory for display

    Returns:
        DataFrame with panel column added
    """
    # Create panels directory
    panels_dir = output_path / "panels"
    panels_dir.mkdir(parents=True, exist_ok=True)

    print(f"Generating {len(data)} panels...")

    # Generate panel for each row
    panel_filenames = []
    for idx, row in data.iterrows():
        panel_filename = create_panel(row, panels_dir, idx)
        panel_filenames.append(str(idx))  # Store just the ID, not full filename

        if (idx + 1) % 10 == 0:
            print(f"  Generated {idx + 1}/{len(data)} panels")

    # Add panel column to data
    data[PANEL_COLUMN_NAME] = panel_filenames

    print(f"✓ Generated all {len(data)} panels")
    return data


# ============================================================================
# 4. CREATE DISPLAY
# ============================================================================


def create_display(data: pd.DataFrame, output_path: Path) -> Display:
    """
    Create trelliscope Display object.

    Args:
        data: DataFrame with panel column
        output_path: Output directory path

    Returns:
        Configured Display object
    """
    print("Creating display configuration...")

    # Create display WITHOUT setting panel_interface
    # This defaults to local file-based panels (Approach 2)
    display = (
        Display(data, name=DISPLAY_NAME, description=DISPLAY_DESCRIPTION)
        .set_panel_column(PANEL_COLUMN_NAME)
        .infer_metas()  # Auto-detect cognostic types from DataFrame
        .set_default_layout(ncol=NCOL, nrow=NROW)
        .set_default_labels(LABEL_COLUMNS)
    )

    # Optional: Add custom meta variable descriptions
    # display.update_meta(
    #     varname="value",
    #     desc="The measured value for this observation"
    # )

    print("✓ Display configuration created")
    return display


# ============================================================================
# 5. CREATE HTML VIEWER
# ============================================================================


def create_viewer_html(output_path: Path) -> None:
    """
    Create HTML viewer file.

    Args:
        output_path: Output directory path
    """
    viewer_html = f"""<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="utf-8">
    <meta name="viewport" content="width=device-width, initial-scale=1">
    <title>{DISPLAY_NAME} - Trelliscope Viewer</title>
    <link rel="stylesheet" href="https://unpkg.com/trelliscopejs-lib@0.7.16/dist/assets/index.css">
    <style>
        body {{
            margin: 0;
            padding: 0;
            font-family: -apple-system, BlinkMacSystemFont, "Segoe UI", Roboto, sans-serif;
        }}
        #trelliscope_root {{
            width: 100vw;
            height: 100vh;
        }}
    </style>
</head>
<body>
    <div id="trelliscope_root" class="trelliscope-not-spa"></div>

    <script type="module">
        try {{
            const module = await import('https://unpkg.com/trelliscopejs-lib@0.7.16/dist/assets/index.js');
            const initFunc = window.trelliscopeApp || module.trelliscopeApp;

            if (typeof initFunc === 'function') {{
                initFunc('trelliscope_root', './{DISPLAY_NAME}');
            }} else {{
                console.error('trelliscopeApp not found in module');
            }}
        }} catch (error) {{
            console.error('Failed to load viewer:', error);
        }}
    </script>
</body>
</html>
"""

    viewer_path = output_path.parent / f"{DISPLAY_NAME}_viewer.html"
    with open(viewer_path, "w") as f:
        f.write(viewer_html)

    print(f"✓ Viewer HTML created: {viewer_path}")


# ============================================================================
# MAIN EXECUTION
# ============================================================================


def main():
    """Main execution function."""
    print(f"\n{'='*70}")
    print(f"Creating Static Trelliscope Display: {DISPLAY_NAME}")
    print(f"{'='*70}\n")

    # 1. Generate/load data
    print("Step 1: Loading data...")
    data = generate_data()
    print(f"✓ Loaded {len(data)} rows with {len(data.columns)} columns")

    # 2. Set up output directory
    output_path = OUTPUT_DIR / DISPLAY_NAME
    print(f"\nStep 2: Setting up output directory...")
    print(f"  Output path: {output_path}")

    # 3. Generate panels
    print(f"\nStep 3: Generating panels...")
    data = generate_panels(data, output_path)

    # 4. Create display
    print(f"\nStep 4: Creating display configuration...")
    display = create_display(data, output_path)

    # 5. Write display (panels already rendered)
    print(f"\nStep 5: Writing display files...")
    display.write(output_path=output_path, render_panels=False, force=True)
    print(f"✓ Display files written to: {output_path}")

    # 6. Create viewer HTML
    print(f"\nStep 6: Creating viewer HTML...")
    create_viewer_html(output_path)

    # 7. Summary
    print(f"\n{'='*70}")
    print(f"✓ Display creation complete!")
    print(f"{'='*70}\n")
    print(f"Files created:")
    print(f"  - Display: {output_path}")
    print(f"  - Viewer:  {output_path.parent}/{DISPLAY_NAME}_viewer.html")
    print(f"\nTo view:")
    print(f"  1. Start HTTP server:")
    print(f"     cd {output_path.parent}")
    print(f"     python3 -m http.server 8000")
    print(f"  2. Open in browser:")
    print(f"     http://localhost:8000/{DISPLAY_NAME}_viewer.html")
    print()


if __name__ == "__main__":
    main()
