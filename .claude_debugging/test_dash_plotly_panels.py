"""
Test Dash viewer with Plotly panels (HTML extraction).

This script creates a display with interactive Plotly figures and tests
whether the Dash viewer can correctly extract and render them natively.
"""

import sys
from pathlib import Path

# Add parent directory to path
sys.path.insert(0, str(Path(__file__).parent.parent))

import pandas as pd
import plotly.graph_objects as go
from trelliscope import Display
from trelliscope.meta import FactorMeta, NumberMeta

print("="*70)
print("DASH VIEWER TEST - Plotly Panels (Native Rendering)")
print("="*70)

# Load data
data_path = Path(__file__).parent / "_data" / "refinery_margins.csv"
print(f"\nLoading data from: {data_path.absolute()}")

df = pd.read_csv(data_path)
df['date'] = pd.to_datetime(df['date'])

print(f"✓ Loaded {len(df):,} rows")

# Get countries
countries = sorted(df['country'].unique())
print(f"\nCountries ({len(countries)}):")
for i, country in enumerate(countries, 1):
    print(f"  {i}. {country}")

# Create Plotly plot function (responsive)
def create_plotly_plot_responsive(country_data, country_name):
    """
    Create responsive interactive Plotly plot.

    Uses autosize=True so panels resize with layout changes.
    """
    fig = go.Figure()

    # Add line trace with markers
    fig.add_trace(go.Scatter(
        x=country_data['date'],
        y=country_data['refinery_kbd'],
        mode='lines+markers',
        name='Refinery Capacity',
        line=dict(color='#2c7fb8', width=2),
        marker=dict(size=4, color='#2c7fb8'),
        hovertemplate='<b>Date:</b> %{x|%Y-%m-%d}<br>' +
                      '<b>Capacity:</b> %{y:.1f} kbd<br>' +
                      '<extra></extra>'
    ))

    # Update layout - RESPONSIVE
    fig.update_layout(
        title=f"Refinery Capacity - {country_name}",
        xaxis_title='Date',
        yaxis_title='Refinery (kbd)',
        plot_bgcolor='white',
        paper_bgcolor='white',
        hovermode='closest',
        showlegend=False,
        autosize=True,  # KEY: Makes plot responsive
        margin=dict(l=60, r=20, t=40, b=60)
    )

    # Add grid styling
    fig.update_xaxes(showgrid=True, gridcolor='#e0e0e0', gridwidth=0.5)
    fig.update_yaxes(showgrid=True, gridcolor='#e0e0e0', gridwidth=0.5)

    return fig

# Create display data
print("\n" + "="*70)
print("Creating Plotly figures...")
print("="*70)

plotly_data = []

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

    # Create Plotly figure (RESPONSIVE)
    plotly_fig = create_plotly_plot_responsive(country_df, country)
    plotly_data.append({**stats, 'panel': plotly_fig})

    print(f"  ✓ {country}: avg={stats['avg_capacity']:.1f} kbd")

# Convert to DataFrame
plotly_df = pd.DataFrame(plotly_data)

print(f"\n✓ Created {len(plotly_df)} Plotly panels (responsive)")

# Create display
print("\n" + "="*70)
print("Creating Trelliscope display...")
print("="*70)

plotly_display = Display(
    plotly_df,
    name="refinery_plotly_dash",
    description="Refinery Capacity - Dash Viewer with Plotly Panels"
)

# Configure
plotly_display.set_panel_column("panel")
plotly_display.add_meta_variable(
    FactorMeta(varname="country", label="Country", levels=sorted(countries))
)
plotly_display.add_meta_variable(
    NumberMeta(varname="avg_capacity", label="Avg Capacity (kbd)", digits=1)
)
plotly_display.add_meta_variable(
    NumberMeta(varname="max_capacity", label="Max Capacity (kbd)", digits=1)
)
plotly_display.add_meta_variable(
    NumberMeta(varname="min_capacity", label="Min Capacity (kbd)", digits=1)
)
plotly_display.add_meta_variable(
    NumberMeta(varname="n_obs", label="# Observations", digits=0)
)
plotly_display.set_default_layout(ncol=3, nrow=2, arrangement="row")
plotly_display.set_default_labels(["country", "avg_capacity"])

# Write
plotly_output = Path("output/refinery_plotly_dash")
print(f"\nWriting display to: {plotly_output}")
plotly_display.write(output_path=plotly_output, force=True, viewer_debug=False)

print("\n✅ Display written successfully!")
print(f"   Panel type: HTML (interactive Plotly)")

# Launch Dash viewer
print("\n" + "="*70)
print("LAUNCHING DASH VIEWER WITH PLOTLY PANELS")
print("="*70)
print("\n🎯 Test these features:")
print("\n  🎨 Native Plotly Rendering:")
print("    • Panels are extracted from HTML and rendered natively")
print("    • NO iframes - native Dash Graph components")
print("    • Full interactivity: hover, zoom, pan")
print("    • Responsive resizing when layout changes")
print("\n  📊 Filtering:")
print("    • Country filter (multi-select)")
print("    • Capacity filters (range sliders)")
print("\n  🔀 Sorting:")
print("    • Add sort (dropdown)")
print("    • Toggle ascending/descending (↑↓ buttons)")
print("    • Remove sort (✕ button)")
print("    • Clear all sorts")
print("\n  🎨 Layout:")
print("    • Adjust columns/rows")
print("    • Watch Plotly panels resize automatically")
print("\n  📄 Pagination:")
print("    • Previous/Next buttons")
print("    • Page info")
print("\n📝 Note: Press Ctrl+C to stop the server")
print("="*70 + "\n")

# Launch Dash viewer
try:
    print("🚀 Starting Dash viewer with Plotly panels...")
    plotly_display.show_interactive(port=8051, debug=False)
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
