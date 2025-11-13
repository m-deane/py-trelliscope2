"""
Phase 3 Complete Demo - Interactive Browser Validation

This demo creates a display with all Phase 3 features enabled:
- Views System (save/load/delete)
- Global Search (search across metadata)
- Panel Details Modal (click panels for details)

Run this script to test the complete Dash viewer in your browser.
"""

import sys
from pathlib import Path
sys.path.insert(0, str(Path(__file__).parent.parent))

import pandas as pd
import matplotlib.pyplot as plt
from trelliscope import Display
import tempfile

print("=" * 70)
print("PHASE 3 COMPLETE - INTERACTIVE DEMO")
print("=" * 70)

# Create sample data with meaningful content for testing
print("\n📊 Creating sample data with 20 panels...")

countries = ['United States', 'United Kingdom', 'Germany', 'France', 'Japan',
             'Canada', 'Australia', 'Brazil', 'India', 'China',
             'Italy', 'Spain', 'Mexico', 'South Korea', 'Netherlands',
             'Switzerland', 'Sweden', 'Norway', 'Denmark', 'Belgium']

continents = ['North America', 'Europe', 'Europe', 'Europe', 'Asia',
              'North America', 'Oceania', 'South America', 'Asia', 'Asia',
              'Europe', 'Europe', 'North America', 'Asia', 'Europe',
              'Europe', 'Europe', 'Europe', 'Europe', 'Europe']

gdp = [21.4, 2.8, 3.8, 2.7, 5.1,
       1.7, 1.4, 1.8, 2.9, 14.3,
       2.0, 1.4, 1.3, 1.6, 0.9,
       0.7, 0.5, 0.4, 0.4, 0.5]

population = [331, 67, 83, 65, 126,
              38, 26, 212, 1380, 1440,
              60, 47, 128, 52, 17,
              9, 10, 5, 6, 12]

df = pd.DataFrame({
    'country': countries,
    'continent': continents,
    'gdp': gdp,
    'population': population,
    'gdp_per_capita': [g/p for g, p in zip(gdp, population)]
})

print(f"✓ Created data for {len(df)} countries")

# Create matplotlib figures
print("\n🎨 Generating panel visualizations...")
figures = []
for idx, row in df.iterrows():
    fig, (ax1, ax2) = plt.subplots(1, 2, figsize=(8, 3))

    # GDP bar chart
    ax1.bar(['GDP'], [row['gdp']], color='steelblue')
    ax1.set_ylabel('GDP (Trillion USD)')
    ax1.set_title(f"{row['country']}")
    ax1.set_ylim(0, max(gdp) * 1.1)

    # Population bar chart
    ax2.bar(['Pop'], [row['population']], color='coral')
    ax2.set_ylabel('Population (Millions)')
    ax2.set_ylim(0, max(population) * 1.1)

    plt.tight_layout()
    figures.append(fig)
    plt.close()

df['panel'] = figures
print(f"✓ Generated {len(figures)} panel visualizations")

# Create display
print("\n📁 Creating Trelliscope display...")
output_dir = Path(tempfile.mkdtemp())

display = Display(df, name="phase3_demo", path=str(output_dir))
display.set_panel_column('panel')
display.set_default_labels(['country', 'continent', 'gdp', 'population'])
display_path = display.write(force=True)

print(f"✓ Display created at: {display_path}")

# Launch interactive viewer
print("\n" + "=" * 70)
print("🚀 LAUNCHING INTERACTIVE VIEWER")
print("=" * 70)
print("\n📋 TESTING CHECKLIST:")
print("\n1️⃣  VIEWS SYSTEM:")
print("   □ Filter by continent = 'Europe'")
print("   □ Sort by GDP (descending)")
print("   □ Save as view named 'Europe GDP'")
print("   □ Clear filters")
print("   □ Load 'Europe GDP' view from dropdown")
print("   □ Verify filters/sorts restored")
print("   □ Delete 'Europe GDP' view")
print("")
print("2️⃣  GLOBAL SEARCH:")
print("   □ Search for 'United' (should find US & UK)")
print("   □ Search for 'America' (should find continents)")
print("   □ Search for 'Germany' (should find 1)")
print("   □ Clear search")
print("   □ Verify results summary updates")
print("")
print("3️⃣  PANEL DETAILS MODAL:")
print("   □ Click on United States panel")
print("   □ Verify modal opens with full-size chart")
print("   □ Check all metadata displayed")
print("   □ Click 'Next' button → should show United Kingdom")
print("   □ Click 'Previous' button → should show United States")
print("   □ Close modal")
print("")
print("4️⃣  INTEGRATION TEST:")
print("   □ Search for 'Europe'")
print("   □ Filter GDP > 2.0")
print("   □ Sort by population (ascending)")
print("   □ Click a panel to open modal")
print("   □ Navigate through filtered results")
print("   □ Save as view named 'Large European Economies'")
print("   □ Clear all")
print("   □ Load saved view")
print("   □ Verify everything restored correctly")
print("")
print("=" * 70)
print("🌐 Opening browser on http://localhost:8053...")
print("=" * 70)
print("")
print("💡 TIP: Keep this terminal open to see any errors")
print("    Press Ctrl+C to stop the server when done testing")
print("")

# Import and launch viewer
from trelliscope.dash_viewer import DashViewer

viewer = DashViewer(display_path, mode="external", debug=False)
viewer.run(port=8053)
