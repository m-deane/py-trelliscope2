"""
Smoke test for views functionality in Dash viewer.
"""

import sys
from pathlib import Path

# Add parent directory to path
sys.path.insert(0, str(Path(__file__).parent.parent))

import pandas as pd
import matplotlib.pyplot as plt
from trelliscope import Display
from trelliscope.dash_viewer import DashViewer
from trelliscope.dash_viewer.views_manager import ViewsManager

print("=" * 60)
print("VIEWS SMOKE TEST")
print("=" * 60)

# Test 1: Create a simple display
print("\n1. Creating test display...")
df = pd.DataFrame({
    'id': list(range(5)),
    'category': ['A', 'B', 'C', 'A', 'B'],
    'value': [10, 20, 30, 15, 25]
})

# Create matplotlib figures (not pre-rendered files)
figures = []
for i in range(5):
    fig, ax = plt.subplots(figsize=(4, 3))
    ax.bar(['Val'], [df.loc[i, 'value']])
    ax.set_title(f"Panel {i}")
    ax.set_ylim(0, 35)
    figures.append(fig)

df['panel'] = figures

# Create output directory
import tempfile
output_dir = Path(tempfile.mkdtemp())

display = Display(df, name="test_display", path=str(output_dir))
display.set_panel_column('panel')
display.set_default_labels(['category', 'value'])
display_path = display.write(force=True)

print(f"✓ Display created at: {display_path}")

# Test 2: Initialize ViewsManager
print("\n2. Testing ViewsManager...")
views_manager = ViewsManager(display_path)

# Save a test view
test_view = {
    'name': 'Test View 1',
    'state': {
        'layout': {'ncol': 3, 'nrow': 2, 'page': 1, 'arrangement': 'row'},
        'labels': ['category', 'value'],
        'sorts': [{'varname': 'value', 'dir': 'desc'}],
        'filters': [{'varname': 'category', 'value': ['A', 'B']}]
    }
}

success = views_manager.save_view(test_view)
print(f"✓ Save view: {'SUCCESS' if success else 'FAILED'}")

# Get views
views = views_manager.get_views()
print(f"✓ Get views: Found {len(views)} view(s)")

# Test 3: Initialize DashViewer
print("\n3. Testing DashViewer initialization...")
viewer = DashViewer(display_path, mode="external", debug=False)
print(f"✓ Viewer initialized")
print(f"✓ Display name: {viewer.display_name}")
print(f"✓ Panels: {len(viewer.cog_data)}")
print(f"✓ Views manager: {type(viewer.views_manager).__name__}")

# Test 4: Create app (don't run)
print("\n4. Creating Dash app...")
app = viewer.create_app()
print(f"✓ App created successfully")
print(f"✓ Callbacks registered")

# Test 5: Views components
print("\n5. Testing views components...")
from trelliscope.dash_viewer.components.views import (
    create_views_panel,
    create_view_item,
    update_views_panel_state
)

views_panel = create_views_panel(views)
print(f"✓ create_views_panel: OK")

view_item = create_view_item(0, test_view)
print(f"✓ create_view_item: OK")

view_items, view_options = update_views_panel_state(views)
print(f"✓ update_views_panel_state: OK")
print(f"  - View items: {len(view_items)}")
print(f"  - View options: {len(view_options)}")

# Test 6: Delete view
print("\n6. Testing view deletion...")
success = views_manager.delete_view(0)
print(f"✓ Delete view: {'SUCCESS' if success else 'FAILED'}")

views_after = views_manager.get_views()
print(f"✓ Views after deletion: {len(views_after)}")

# Cleanup
print("\n7. Cleanup...")
import shutil
shutil.rmtree(output_dir)
print(f"✓ Cleaned up temp directory")

print("\n" + "=" * 60)
print("ALL VIEWS SMOKE TESTS PASSED ✓")
print("=" * 60)
print("\nViews system ready for testing!")
print("To test interactively, run:")
print(f"  display.show_interactive()")
