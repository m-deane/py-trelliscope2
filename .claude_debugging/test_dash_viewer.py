"""
Test script for Plotly Dash Interactive Viewer.

This script demonstrates the new show_interactive() method that launches
a Plotly Dash-based interactive viewer.

Usage:
    python examples/test_dash_viewer.py
"""

import sys
from pathlib import Path

# Add parent directory to path
sys.path.insert(0, str(Path(__file__).parent.parent))

import pandas as pd
import matplotlib.pyplot as plt
from trelliscope import Display
from trelliscope.meta import FactorMeta, NumberMeta

# Load refinery margins data
data_path = Path(__file__).parent / "_data" / "refinery_margins.csv"

print("="*70)
print("PLOTLY DASH INTERACTIVE VIEWER - TEST")
print("="*70)
print(f"\nLoading data from: {data_path}")

df = pd.read_csv(data_path)
df['date'] = pd.to_datetime(df['date'])

print(f"✓ Loaded {len(df):,} rows")
print(f"  Date range: {df['date'].min().date()} to {df['date'].max().date()}")

# Get countries
countries = sorted(df['country'].unique())
print(f"  Countries: {len(countries)}")

# Create matplotlib plots for each country
def create_matplotlib_plot(country_data, country_name):
    """Create simple matplotlib plot."""
    fig, ax = plt.subplots(figsize=(6, 4))

    ax.plot(country_data['date'], country_data['refinery_kbd'],
            color='#2c7fb8', linewidth=2, marker='o', markersize=3)

    ax.set_title(f"Refinery Capacity - {country_name}", fontsize=11, fontweight='bold')
    ax.set_xlabel("Date", fontsize=9)
    ax.set_ylabel("Refinery (kbd)", fontsize=9)
    ax.grid(True, alpha=0.3)

    plt.tight_layout()
    return fig

print("\n" + "="*70)
print("Creating display data...")
print("="*70)

display_data = []
for country in countries:
    country_df = df[df['country'] == country].copy()

    # Calculate statistics
    stats = {
        'country': country,
        'avg_capacity': country_df['refinery_kbd'].mean(),
        'max_capacity': country_df['refinery_kbd'].max(),
        'min_capacity': country_df['refinery_kbd'].min(),
        'n_obs': len(country_df)
    }

    # Create matplotlib figure
    fig = create_matplotlib_plot(country_df, country)
    stats['panel'] = fig

    display_data.append(stats)
    print(f"  ✓ {country}: avg={stats['avg_capacity']:.1f} kbd")

# Convert to DataFrame
display_df = pd.DataFrame(display_data)

print(f"\n✓ Created {len(display_df)} panels")

# Create Display
print("\n" + "="*70)
print("Creating Trelliscope display...")
print("="*70)

display = Display(
    display_df,
    name="refinery_dash_test",
    description="Refinery Capacity by Country - Dash Viewer Test"
)

# Configure
display.set_panel_column("panel")
display.add_meta_variable(
    FactorMeta(varname="country", label="Country", levels=sorted(countries))
)
display.add_meta_variable(
    NumberMeta(varname="avg_capacity", label="Avg Capacity (kbd)", digits=1)
)
display.add_meta_variable(
    NumberMeta(varname="max_capacity", label="Max Capacity (kbd)", digits=1)
)
display.add_meta_variable(
    NumberMeta(varname="min_capacity", label="Min Capacity (kbd)", digits=1)
)
display.add_meta_variable(
    NumberMeta(varname="n_obs", label="# Observations", digits=0)
)
display.set_default_layout(ncol=3, nrow=2, arrangement="row")
display.set_default_labels(["country", "avg_capacity"])

# Write display
output_path = Path("output/refinery_dash_test")
print(f"\nWriting display to: {output_path}")
display.write(output_path=output_path, force=True, viewer_debug=False)

# Close matplotlib figures to free memory
plt.close('all')

print("\n✓ Display written successfully!")

# Launch interactive Dash viewer
print("\n" + "="*70)
print("LAUNCHING PLOTLY DASH INTERACTIVE VIEWER")
print("="*70)
print("\n🎯 Features available:")
print("  • Filter by country (multi-select dropdown)")
print("  • Filter by numeric ranges (avg/max/min capacity)")
print("  • Adjust grid layout (columns/rows)")
print("  • Pagination controls")
print("  • Panel labels")
print("\n📝 Note: This will open in your browser. Press Ctrl+C to stop.")
print("\n" + "="*70 + "\n")

# Launch Dash viewer
try:
    display.show_interactive(port=8050, debug=False)
except KeyboardInterrupt:
    print("\n\n✓ Viewer stopped by user")
except Exception as e:
    print(f"\n❌ Error: {e}")
    print("\nMake sure you have installed the required dependencies:")
    print("  pip install dash dash-bootstrap-components")
