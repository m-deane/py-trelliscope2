"""
Smoke test for Dash viewer - verify it can be instantiated without running.
"""

import sys
from pathlib import Path

# Add parent directory to path
sys.path.insert(0, str(Path(__file__).parent.parent))

import pandas as pd
import matplotlib.pyplot as plt
from trelliscope import Display
from trelliscope.meta import FactorMeta, NumberMeta
from trelliscope.dash_viewer import DashViewer

print("="*70)
print("DASH VIEWER SMOKE TEST")
print("="*70)

# Create simple test data
print("\n1. Creating test data...")
df = pd.DataFrame({
    'panel': ['panel1', 'panel2', 'panel3'],
    'category': ['A', 'B', 'C'],
    'value': [10, 20, 30]
})
print(f"   ✓ Created DataFrame with {len(df)} rows")

# Create simple matplotlib plots
print("\n2. Creating matplotlib plots...")
def create_test_plot(value):
    fig, ax = plt.subplots(figsize=(4, 3))
    ax.bar(['Test'], [value], color='blue')
    ax.set_ylim(0, 40)
    ax.set_title(f"Value: {value}")
    plt.tight_layout()
    return fig

df['panel'] = df['value'].apply(create_test_plot)
print(f"   ✓ Created {len(df)} matplotlib figures")

# Create display
print("\n3. Creating Display...")
display = Display(df, name='smoke_test', description='Smoke test for Dash viewer')
display.set_panel_column('panel')
display.add_meta_variable(FactorMeta(varname='category', label='Category', levels=['A', 'B', 'C']))
display.add_meta_variable(NumberMeta(varname='value', label='Value', digits=0))
display.set_default_layout(ncol=2, nrow=2)
display.set_default_labels(['category', 'value'])
print("   ✓ Display configured")

# Write display
print("\n4. Writing display to disk...")
output_path = Path("output/smoke_test")
display.write(output_path=output_path, force=True, viewer_debug=False)
plt.close('all')
print(f"   ✓ Display written to {output_path}")

# Test DashViewer instantiation
print("\n5. Testing DashViewer instantiation...")
try:
    viewer = DashViewer(
        display_path=output_path,
        mode="external",
        debug=False
    )
    print(f"   ✓ DashViewer instantiated: {viewer}")
    print(f"   ✓ Display name: {viewer.display_name}")
    print(f"   ✓ Number of panels: {len(viewer.cog_data)}")
    print(f"   ✓ Mode: {viewer.mode}")

    # Test app creation without running
    print("\n6. Testing Dash app creation...")
    app = viewer.create_app()
    print(f"   ✓ Dash app created: {app}")
    print(f"   ✓ App name: {app.config.name}")

    # Test state
    print("\n7. Testing DisplayState...")
    print(f"   ✓ Initial page: {viewer.state.current_page}")
    print(f"   ✓ Layout: {viewer.state.ncol}x{viewer.state.nrow}")
    print(f"   ✓ Panels per page: {viewer.state.panels_per_page}")
    print(f"   ✓ Active filters: {viewer.state.active_filters}")
    print(f"   ✓ Active sorts: {viewer.state.active_sorts}")
    print(f"   ✓ Active labels: {viewer.state.active_labels}")

    # Test loader
    print("\n8. Testing DisplayLoader...")
    print(f"   ✓ Display info loaded: {bool(viewer.loader.display_info)}")
    print(f"   ✓ Filterable metas: {len(viewer.loader.get_filterable_metas())}")

    filterable = viewer.loader.get_filterable_metas()
    for meta in filterable:
        print(f"      - {meta['varname']} ({meta['type']})")

    print("\n" + "="*70)
    print("✅ ALL SMOKE TESTS PASSED!")
    print("="*70)
    print("\nDash viewer is ready to use!")
    print("\nTo run the full test:")
    print("  python examples/test_dash_17_demo.py")
    print("\nTo run the simple test:")
    print("  python examples/test_dash_viewer.py")

except Exception as e:
    print(f"\n❌ ERROR: {e}")
    import traceback
    traceback.print_exc()
    sys.exit(1)
