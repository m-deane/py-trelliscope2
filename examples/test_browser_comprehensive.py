"""
Browser Testing Validation Script and Checklist

This script launches the Dash viewer and provides a comprehensive checklist
for manual browser testing of all features.
"""

import sys
from pathlib import Path

# Add parent directory to path
sys.path.insert(0, str(Path(__file__).parent.parent))

import pandas as pd
import matplotlib.pyplot as plt
from trelliscope import Display
from trelliscope.meta import FactorMeta, NumberMeta

print("="*70)
print("COMPREHENSIVE BROWSER TEST - Full Feature Validation")
print("="*70)

# Load refinery data
data_path = Path(__file__).parent / "_data" / "refinery_margins.csv"
print(f"\nLoading data from: {data_path.absolute()}")

df = pd.read_csv(data_path)
df['date'] = pd.to_datetime(df['date'])

print(f"✓ Loaded {len(df):,} rows")

# Get countries
countries = sorted(df['country'].unique())
print(f"  Countries: {len(countries)}")

# Create matplotlib plots
def create_matplotlib_plot(country_data, country_name):
    """Create matplotlib plot."""
    fig, ax = plt.subplots(figsize=(8, 5))

    ax.plot(country_data['date'], country_data['refinery_kbd'],
            color='#2c7fb8', linewidth=2, marker='o', markersize=3)

    ax.set_title(f"Refinery Capacity - {country_name}", fontsize=12, fontweight='bold')
    ax.set_xlabel("Date", fontsize=10)
    ax.set_ylabel("Refinery (kbd)", fontsize=10)
    ax.grid(True, alpha=0.3)

    plt.tight_layout()
    return fig

# Create display data
print("\nCreating display data...")
matplotlib_data = []

for country in countries:
    country_df = df[df['country'] == country].copy()

    stats = {
        'country': country,
        'avg_capacity': country_df['refinery_kbd'].mean(),
        'max_capacity': country_df['refinery_kbd'].max(),
        'min_capacity': country_df['refinery_kbd'].min(),
        'n_obs': len(country_df)
    }

    matplotlib_fig = create_matplotlib_plot(country_df, country)
    matplotlib_data.append({**stats, 'panel': matplotlib_fig})

matplotlib_df = pd.DataFrame(matplotlib_data)
print(f"✓ Created {len(matplotlib_df)} panels")

# Create display
print("\nCreating display...")
display = Display(
    matplotlib_df,
    name="browser_test_comprehensive",
    description="Comprehensive Browser Test - All Features"
)

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

# Write
output_path = Path("output/browser_test_comprehensive")
print(f"Writing display to: {output_path}")
display.write(output_path=output_path, force=True, viewer_debug=False)
plt.close('all')

print("\n" + "="*70)
print("BROWSER TEST CHECKLIST")
print("="*70)
print("\nThe viewer will launch shortly. Please test ALL features below:")
print("\n" + "─"*70)
print("1. INITIAL LOAD")
print("─"*70)
print("  □ Page loads without errors")
print("  □ Display name shows: 'browser_test_comprehensive'")
print("  □ Panel count shows: 'Showing 1-6 of 10 panels'")
print("  □ Grid shows 3 columns × 2 rows (6 panels)")
print("  □ All 6 panels render correctly")
print("  □ Panel labels show beneath each panel")
print("  □ Labels show: Country and Avg Capacity")

print("\n" + "─"*70)
print("2. FILTERING - Factor Type (Country)")
print("─"*70)
print("  □ Click country filter dropdown")
print("  □ All 10 countries listed with counts")
print("  □ Select 'Germany'")
print("  □ Panel count updates: 'Showing 1-1 of 1 panels'")
print("  □ Only Germany panel shows")
print("  □ Select 'United Kingdom' (add to filter)")
print("  □ Panel count updates: 'Showing 1-2 of 2 panels'")
print("  □ Both panels show")
print("  □ Click 'Clear All Filters'")
print("  □ All 10 panels return")

print("\n" + "─"*70)
print("3. FILTERING - Number Type (Capacity)")
print("─"*70)
print("  □ Find 'Avg Capacity' range slider")
print("  □ Note min and max values")
print("  □ Drag left handle to increase minimum")
print("  □ Panel count decreases")
print("  □ Only panels with high avg capacity show")
print("  □ Drag right handle to decrease maximum")
print("  □ Panel count decreases further")
print("  □ Click 'Clear All Filters'")
print("  □ All panels return")

print("\n" + "─"*70)
print("4. SORTING")
print("─"*70)
print("  □ Find 'Sort' section in sidebar")
print("  □ Click 'Add Sort' dropdown")
print("  □ All sortable variables listed")
print("  □ Select 'Avg Capacity'")
print("  □ Sort appears in 'Active Sorts' as '1. Avg Capacity ↑'")
print("  □ Panels reorder (lowest capacity first)")
print("  □ Click ↓ button to change to descending")
print("  □ Panels reorder (highest capacity first)")
print("  □ Add another sort: 'Country'")
print("  □ Shows as '2. Country ↑' (secondary sort)")
print("  □ Panels reorder by capacity, then country")
print("  □ Click ✕ on first sort")
print("  □ First sort removed, 'Country' becomes priority 1")
print("  □ Click 'Clear All Sorts'")
print("  □ All sorts removed, original order returns")

print("\n" + "─"*70)
print("5. PAGINATION")
print("─"*70)
print("  □ Page info shows: 'Page 1 of 2'")
print("  □ 'Previous' button is disabled")
print("  □ Click 'Next' button")
print("  □ Page info updates: 'Page 2 of 2'")
print("  □ Panel count updates: 'Showing 7-10 of 10 panels'")
print("  □ 4 panels show (remainder)")
print("  □ 'Next' button is disabled")
print("  □ Click 'Previous' button")
print("  □ Return to Page 1")
print("  □ 6 panels show again")

print("\n" + "─"*70)
print("6. LAYOUT ADJUSTMENT")
print("─"*70)
print("  □ Find 'Columns' dropdown (current: 3)")
print("  □ Change to 2 columns")
print("  □ Grid adjusts to 2×2 (4 panels)")
print("  □ Panel count updates: 'Showing 1-4 of 10 panels'")
print("  □ Panels resize to fit new layout")
print("  □ Change to 4 columns")
print("  □ Grid adjusts to 4×2 (8 panels)")
print("  □ Panel count updates: 'Showing 1-8 of 10 panels'")
print("  □ Change 'Rows' to 3")
print("  □ Grid adjusts to 4×3 (12 panels)")
print("  □ All 10 panels fit on one page")
print("  □ Page info shows: 'Page 1 of 1'")
print("  □ Both navigation buttons disabled")

print("\n" + "─"*70)
print("7. COMBINED FEATURES")
print("─"*70)
print("  □ Reset layout to 3×2")
print("  □ Apply filter: Country = 'Germany', 'Italy', 'Norway'")
print("  □ Panel count: 'Showing 1-3 of 3 panels'")
print("  □ Add sort: 'Avg Capacity' descending")
print("  □ Panels reorder within filtered set")
print("  □ Change layout to 2×2")
print("  □ Panel count: 'Showing 1-3 of 3 panels' (all fit)")
print("  □ Clear filter")
print("  □ Panel count updates to full set with sort applied")
print("  □ Clear sort")
print("  □ Return to default state")

print("\n" + "─"*70)
print("8. ERROR HANDLING")
print("─"*70)
print("  □ Check browser console (F12) - no errors")
print("  □ Check Network tab - all resources load")
print("  □ Rapidly click filters/sorts - no crashes")
print("  □ Change layout while filtering - no errors")

print("\n" + "─"*70)
print("9. VISUAL QUALITY")
print("─"*70)
print("  □ Panels are clear and readable")
print("  □ Labels are properly formatted")
print("  □ No visual glitches or overlaps")
print("  □ Grid spacing looks good")
print("  □ Sidebar scrolls smoothly if needed")
print("  □ Controls are responsive (hover states, clicks)")

print("\n" + "─"*70)
print("10. PERFORMANCE")
print("─"*70)
print("  □ Initial load < 2 seconds")
print("  □ Filter changes < 500ms")
print("  □ Sort changes < 500ms")
print("  □ Layout changes < 500ms")
print("  □ Page navigation < 200ms")
print("  □ No lag when interacting")

print("\n" + "="*70)
print("TEST SUMMARY")
print("="*70)
print("\nAfter completing all tests above, verify:")
print("  □ All features work as expected")
print("  □ No errors in browser console")
print("  □ Performance is acceptable")
print("  □ UI is intuitive and responsive")
print("\nIf all checkboxes are ✓, the viewer passes browser validation!")

print("\n" + "="*70)
print("LAUNCHING VIEWER...")
print("="*70)
print(f"\n🌐 URL: http://localhost:8052")
print("📋 Use the checklist above to validate all features")
print("⏱️  Estimated test time: 10-15 minutes")
print("📝 Press Ctrl+C to stop when done\n")

# Launch viewer
try:
    display.show_interactive(port=8052, debug=False)
except KeyboardInterrupt:
    print("\n\n✅ Browser test completed!")
    print("Please review the checklist and note any failures.")
except Exception as e:
    print(f"\n❌ Error: {e}")
    import traceback
    traceback.print_exc()
