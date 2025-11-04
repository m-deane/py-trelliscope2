# Trelliscope Display Templates

This directory contains templates for creating trelliscope displays using different approaches.

## Available Templates

### 1. `static_display_template.py` - Static Panel Display (Approach 2)

**Use when:**
- Panels can be pre-rendered as images (PNG/JPEG)
- Display is relatively small (< 10,000 panels)
- Want simple deployment (just files, no server needed)
- Need offline capability
- Want maximum compatibility

**Advantages:**
- ✅ Simple - No server infrastructure required
- ✅ Fast - Direct file loading, no HTTP requests
- ✅ Portable - Just copy files to any web server
- ✅ Reliable - Uses stable CDN viewer (v0.7.16)
- ✅ Offline-capable - Works without internet (if viewer cached)

**How to use:**

```bash
# 1. Copy template
cp templates/static_display_template.py my_display.py

# 2. Customize the template:
#    - Update DISPLAY_NAME, DISPLAY_DESCRIPTION
#    - Modify generate_data() to load your data
#    - Customize create_panel() with your visualization logic
#    - Adjust layout and label settings

# 3. Run the script
python my_display.py

# 4. Start HTTP server
cd output
python3 -m http.server 8000

# 5. Open viewer in browser
open http://localhost:8000/my_display_viewer.html
```

**Template sections:**

1. **Configuration** - Display name, layout, output paths
2. **Data Generation** - Create or load your DataFrame
3. **Panel Generation** - Visualization logic (matplotlib, plotly, etc.)
4. **Display Creation** - Configure trelliscope Display object
5. **HTML Viewer** - Auto-generated viewer file

---

## Quick Start Example

```python
from pathlib import Path
import pandas as pd
import matplotlib.pyplot as plt
from trelliscope import Display

# 1. Create data
data = pd.DataFrame({
    'id': range(5),
    'value': [10, 25, 15, 30, 20],
    'category': ['A', 'B', 'C', 'D', 'E']
})

# 2. Generate panels
output_dir = Path("output/my_display")
panels_dir = output_dir / "panels"
panels_dir.mkdir(parents=True, exist_ok=True)

panel_ids = []
for idx, row in data.iterrows():
    fig, ax = plt.subplots(figsize=(5, 5))
    ax.bar([row['category']], [row['value']])
    fig.savefig(panels_dir / f"panel_{idx}.png")
    plt.close(fig)
    panel_ids.append(str(idx))

data['panel'] = panel_ids

# 3. Create display (no panel_interface set = defaults to local files)
display = (Display(data, name="my_display")
    .set_panel_column("panel")
    .infer_metas()
    .set_default_layout(ncol=3))

# 4. Write display
display.write(output_path=output_dir, render_panels=False, force=True)

# 5. Create viewer HTML
html = '''<!DOCTYPE html>
<html>
<head>
    <link rel="stylesheet" href="https://unpkg.com/trelliscopejs-lib@0.7.16/dist/assets/index.css">
</head>
<body>
    <div id="trelliscope_root" class="trelliscope-not-spa"></div>
    <script type="module">
        const m = await import('https://unpkg.com/trelliscopejs-lib@0.7.16/dist/assets/index.js');
        (window.trelliscopeApp || m.trelliscopeApp)('trelliscope_root', './my_display');
    </script>
</body>
</html>'''

with open("output/my_display_viewer.html", "w") as f:
    f.write(html)
```

---

## Template Customization Guide

### Data Generation

Replace `generate_data()` with your actual data source:

```python
def generate_data() -> pd.DataFrame:
    # Option 1: Load from CSV
    return pd.read_csv('data.csv')

    # Option 2: Load from database
    # import sqlalchemy
    # engine = sqlalchemy.create_engine('postgresql://...')
    # return pd.read_sql('SELECT * FROM table', engine)

    # Option 3: Generate programmatically
    # return pd.DataFrame({...})
```

### Panel Visualization

Customize `create_panel()` for your visualization needs:

```python
# Matplotlib example
def create_panel(row, panel_dir, panel_id):
    fig, ax = plt.subplots(figsize=(6, 4))
    ax.plot(row['x_data'], row['y_data'])
    ax.set_title(row['title'])

    panel_filename = f"panel_{panel_id}.png"
    fig.savefig(panel_dir / panel_filename, dpi=150)
    plt.close(fig)
    return panel_filename

# Plotly example
def create_panel(row, panel_dir, panel_id):
    import plotly.graph_objects as go

    fig = go.Figure()
    fig.add_trace(go.Scatter(x=row['x'], y=row['y']))

    panel_filename = f"panel_{panel_id}.png"
    fig.write_image(panel_dir / panel_filename)
    return panel_filename
```

### Display Configuration

Customize layout, labels, and metadata:

```python
display = (Display(data, name="my_display", description="My analysis")
    .set_panel_column("panel")
    .infer_metas()
    .set_default_layout(ncol=4, nrow=2)  # 4 columns, 2 rows
    .set_default_labels(["category", "value", "date"])  # Panel labels
    .set_default_sort([("value", "desc")])  # Default sorting
)

# Add custom metadata descriptions
display.update_meta(
    varname="value",
    desc="Measured value in units",
    digits=2  # Format numbers
)

display.update_meta(
    varname="category",
    desc="Category classification"
)
```

---

## File Structure

After running a template, you'll get:

```
output/
├── my_display/
│   ├── displayInfo.json      # Display configuration
│   ├── metadata.csv           # Cognostics data
│   └── panels/
│       ├── panel_0.png
│       ├── panel_1.png
│       └── ...
└── my_display_viewer.html     # Viewer entry point
```

---

## Troubleshooting

### Issue: Panels not showing in viewer

**Check:**
1. DevTools Console - any errors?
2. DevTools Network tab - are panel PNGs loading?
3. displayInfo.json - is `"type": "file"` set?
4. Panel files - do they exist in panels/ directory?

**Solution:**
```python
# Ensure you're NOT setting panel_interface (defaults to local files)
display = Display(data, name="my_display")
    .set_panel_column("panel")  # ✓ Correct
    # .set_panel_interface(...)  # ✗ Don't do this for static displays
```

### Issue: "No displays found" error

**Check:**
1. Is viewer HTML in correct location? (parent of display directory)
2. Is path in initFunc correct?

**Solution:**
```javascript
// If HTML is in output/ and display is in output/my_display/
initFunc('trelliscope_root', './my_display');  // ✓ Correct

// NOT these:
// initFunc('trelliscope_root', 'my_display');      // ✗ Missing ./
// initFunc('trelliscope_root', '/my_display');     // ✗ Absolute path
```

### Issue: CORS errors when opening HTML file directly

**Solution:** Always use an HTTP server:
```bash
cd output
python3 -m http.server 8000
```

Don't open HTML files with `file://` protocol.

---

## Best Practices

1. **Panel File Naming**: Use consistent naming like `panel_{id}.png`
2. **Image Quality**: Balance file size vs quality (DPI 100-150 usually sufficient)
3. **Cognostics**: Include meaningful metadata for filtering/sorting
4. **Labels**: Show 2-3 most important cognostics as panel labels
5. **Layout**: Choose ncol based on panel complexity (simple plots: 4-6, complex: 2-3)
6. **Testing**: Always test with small subset first before generating thousands of panels

---

## Performance Tips

```python
# For large datasets, use progress tracking
from tqdm import tqdm

for idx, row in tqdm(data.iterrows(), total=len(data)):
    create_panel(row, panels_dir, idx)

# Parallel panel generation (if panels are independent)
from multiprocessing import Pool

def create_panel_wrapper(args):
    idx, row, panels_dir = args
    return create_panel(row, panels_dir, idx)

with Pool() as pool:
    args_list = [(idx, row, panels_dir) for idx, row in data.iterrows()]
    panel_ids = pool.map(create_panel_wrapper, args_list)
```

---

## Related Documentation

- [Approach 2 Implementation Guide](../output/APPROACH_2_IMPLEMENTATION.md)
- [py-trelliscope Core Documentation](../../docs/)
- [trelliscopejs-lib Viewer Docs](https://hafen.github.io/trelliscopejs-lib/)
