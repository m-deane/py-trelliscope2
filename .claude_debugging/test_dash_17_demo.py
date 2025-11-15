"""
Test Dash viewer with data from 17_dual_display_demo.ipynb

This script tests the Dash viewer with the same refinery margins dataset
used in the dual display demo, creating a display with matplotlib panels.
"""

import sys
from pathlib import Path

# Add parent directory to path
sys.path.insert(0, str(Path(__file__).parent.parent))

import pandas as pd
import matplotlib.pyplot as plt
import matplotlib.dates as mdates
from trelliscope import Display
from trelliscope.meta import FactorMeta, NumberMeta

print("="*70)
print("DASH VIEWER TEST - Refinery Margins (from 17_dual_display_demo)")
print("="*70)

# Load data
data_path = Path(__file__).parent / "_data" / "refinery_margins.csv"
print(f"\nLoading data from: {data_path.absolute()}")

df = pd.read_csv(data_path)
df['date'] = pd.to_datetime(df['date'])

print(f"✓ Loaded {len(df):,} rows")
print(f"  Shape: {df.shape}")
print(f"  Date range: {df['date'].min().date()} to {df['date'].max().date()}")

# Get countries
countries = sorted(df['country'].unique())
print(f"\nCountries ({len(countries)}):")
for i, country in enumerate(countries, 1):
    print(f"  {i}. {country}")

# Create matplotlib plot function
def create_matplotlib_plot(country_data, country_name):
    """Create matplotlib plot matching 17_dual_display_demo style."""
    fig, ax = plt.subplots(figsize=(8, 5))

    # Plot line and points
    ax.plot(country_data['date'], country_data['refinery_kbd'],
            color='#2c7fb8', linewidth=2, marker='o', markersize=3,
            markerfacecolor='#2c7fb8', markeredgewidth=0)

    # Format x-axis dates
    ax.xaxis.set_major_formatter(mdates.DateFormatter('%Y'))
    ax.xaxis.set_major_locator(mdates.YearLocator(2))

    # Labels and title
    ax.set_title(f"Refinery Capacity - {country_name}", fontsize=12, fontweight='bold')
    ax.set_xlabel("Date", fontsize=10)
    ax.set_ylabel("Refinery (kbd)", fontsize=10)

    # Grid
    ax.grid(True, alpha=0.3, linestyle='--', linewidth=0.5)

    plt.tight_layout()

    return fig

# Create display data
print("\n" + "="*70)
print("Creating display data...")
print("="*70)

matplotlib_data = []

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
    matplotlib_fig = create_matplotlib_plot(country_df, country)
    matplotlib_data.append({**stats, 'panel': matplotlib_fig})

    print(f"  ✓ {country}: avg={stats['avg_capacity']:.1f} kbd")

# Convert to DataFrame
matplotlib_df = pd.DataFrame(matplotlib_data)

print(f"\n✓ Created {len(matplotlib_df)} matplotlib panels")

# Create display
print("\n" + "="*70)
print("Creating Trelliscope display...")
print("="*70)

matplotlib_display = Display(
    matplotlib_df,
    name="refinery_by_country_dash",
    description="Refinery Capacity by Country - Dash Viewer Test (Matplotlib)"
)

# Configure
matplotlib_display.set_panel_column("panel")
matplotlib_display.add_meta_variable(
    FactorMeta(varname="country", label="Country", levels=sorted(countries))
)
matplotlib_display.add_meta_variable(
    NumberMeta(varname="avg_capacity", label="Avg Capacity (kbd)", digits=1)
)
matplotlib_display.add_meta_variable(
    NumberMeta(varname="max_capacity", label="Max Capacity (kbd)", digits=1)
)
matplotlib_display.add_meta_variable(
    NumberMeta(varname="min_capacity", label="Min Capacity (kbd)", digits=1)
)
matplotlib_display.add_meta_variable(
    NumberMeta(varname="n_obs", label="# Observations", digits=0)
)
matplotlib_display.set_default_layout(ncol=3, nrow=2, arrangement="row")
matplotlib_display.set_default_labels(["country", "avg_capacity"])

# Write
matplotlib_output = Path("output/refinery_by_country_dash")
print(f"\nWriting display to: {matplotlib_output}")
matplotlib_display.write(output_path=matplotlib_output, force=True, viewer_debug=False)

# Close matplotlib figures
plt.close('all')

print("\n✅ Display written successfully!")
print(f"   Panel type: PNG (static images)")

# Launch Dash viewer
print("\n" + "="*70)
print("LAUNCHING DASH VIEWER")
print("="*70)
print("\n🎯 Test these features:")
print("\n  📊 Filtering:")
print("    • Country filter (multi-select dropdown)")
print("    • Avg Capacity filter (range slider)")
print("    • Max Capacity filter (range slider)")
print("    • Min Capacity filter (range slider)")
print("    • # Observations filter (range slider)")
print("\n  🎨 Layout:")
print("    • Adjust columns (1-6)")
print("    • Adjust rows (1-6)")
print("    • Watch panels resize")
print("\n  📄 Pagination:")
print("    • Navigate with Previous/Next buttons")
print("    • See page info ('Page N of M')")
print("    • See panel count ('Showing X-Y of Z')")
print("\n  🏷️  Labels:")
print("    • Country and Avg Capacity shown below each panel")
print("\n  🧹 Clear Filters:")
print("    • Click 'Clear All Filters' to reset")
print("\n📝 Note: Press Ctrl+C to stop the server")
print("="*70 + "\n")

# Launch Dash viewer
try:
    print("🚀 Starting Dash viewer...")
    matplotlib_display.show_interactive(port=8050, debug=False)
except KeyboardInterrupt:
    print("\n\n✓ Viewer stopped by user")
except ImportError as e:
    print(f"\n❌ Missing dependencies: {e}")
    print("\nInstall with:")
    print("  pip install dash dash-bootstrap-components")
except Exception as e:
    print(f"\n❌ Error: {e}")
    import traceback
    traceback.print_exc()
