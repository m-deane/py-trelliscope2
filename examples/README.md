# py-trelliscope Examples

This directory contains working examples and templates for creating trelliscope displays using different approaches.

## Quick Start

**New to trelliscope?** Start here:

1. **[5-Minute Tutorial](templates/QUICK_START.md)** - Create your first display
2. **[Static Display Template](templates/static_display_template.py)** - Copy and customize
3. **[Simple Example](simple_static_example.py)** - See working code

## Approaches

py-trelliscope supports multiple approaches for creating displays. Choose based on your needs:

### Approach 2: Static Panel Displays ⭐ **Recommended**

**Use when**: Panels can be pre-rendered, want simple deployment, need offline capability

**Advantages**:
- ✅ Simple - No server required
- ✅ Fast - Direct file loading
- ✅ Reliable - Stable CDN viewer
- ✅ Portable - Just copy files

**Resources**:
- 📖 [Complete Workflow Guide](APPROACH_2_SUMMARY.md)
- 📖 [Implementation Details](output/APPROACH_2_IMPLEMENTATION.md)
- 📖 [Quick Start Tutorial](templates/QUICK_START.md)
- 🔧 [Reusable Template](templates/static_display_template.py)
- 💡 [Working Example](simple_static_example.py)

**Quick Example**:
```python
import pandas as pd
import matplotlib.pyplot as plt
from pathlib import Path
from trelliscope import Display

# 1. Create data
data = pd.DataFrame({'id': range(5), 'value': [10, 25, 15, 30, 20]})

# 2. Generate panels
panels_dir = Path("output/my_display/panels")
panels_dir.mkdir(parents=True, exist_ok=True)
for idx, row in data.iterrows():
    fig, ax = plt.subplots()
    ax.bar(['Value'], [row['value']])
    fig.savefig(panels_dir / f"panel_{idx}.png")
    plt.close(fig)
data['panel'] = [str(i) for i in range(len(data))]

# 3. Create display (defaults to local files)
display = (Display(data, name="my_display")
    .set_panel_column("panel")
    .infer_metas()
    .set_default_layout(ncol=3))

# 4. Write display
display.write(output_path=Path("output/my_display"), render_panels=False, force=True)

# 5. View at http://localhost:8000/my_display_viewer.html
```

### Approach 3: REST Panel Interface

**Use when**: Very large displays (100k+ panels), dynamic data, need server-side computation

**Resources**:
- 💡 [REST Example](rest_panels_example.py)
- 🔧 [Panel Server](panel_server.py)

**Note**: More complex, requires Flask server and forked viewer.

## Directory Structure

```
examples/
├── README.md                          # This file
├── APPROACH_2_SUMMARY.md              # Complete Approach 2 workflow guide
│
├── templates/                          # Reusable templates
│   ├── README.md                      # Template usage guide
│   ├── QUICK_START.md                 # 5-minute tutorial
│   └── static_display_template.py     # Complete template
│
├── output/                             # Generated displays
│   ├── APPROACH_2_IMPLEMENTATION.md   # Technical documentation
│   ├── simple_static/                 # Example static display
│   │   ├── displayInfo.json
│   │   ├── metadata.csv
│   │   └── panels/
│   │       ├── panel_0.png
│   │       └── ...
│   ├── simple_static_viewer.html      # Simple viewer
│   └── simple_static_test.html        # Debug viewer
│
├── simple_static_example.py           # ⭐ Working Approach 2 example
├── rest_panels_example.py             # Approach 3 example
├── panel_server.py                    # Flask server for REST panels
│
└── (other test files...)
```

## Documentation

### Getting Started
- **[Quick Start (5 min)](templates/QUICK_START.md)** - Fastest way to create a display
- **[Complete Workflow](APPROACH_2_SUMMARY.md)** - Full Approach 2 guide with all details
- **[Template Guide](templates/README.md)** - How to customize templates

### Technical Details
- **[Approach 2 Implementation](output/APPROACH_2_IMPLEMENTATION.md)** - Technical architecture and patterns
- **[Template Code](templates/static_display_template.py)** - Fully documented template

### Examples
- **[Simple Static Example](simple_static_example.py)** - Basic 5-panel display
- **[REST Panels Example](rest_panels_example.py)** - Dynamic panel generation

## Common Tasks

### Create a New Display

```bash
# 1. Copy template
cp templates/static_display_template.py my_analysis.py

# 2. Edit my_analysis.py (customize data, panels, layout)

# 3. Run it
python my_analysis.py

# 4. Start HTTP server
cd output
python3 -m http.server 8000

# 5. Open in browser
open http://localhost:8000/my_analysis_viewer.html
```

### View Existing Display

```bash
# Start HTTP server
cd output
python3 -m http.server 8000

# Open in browser
open http://localhost:8000/simple_static_viewer.html
```

### Customize Panel Visualization

Edit the `create_panel()` function in your script:

```python
def create_panel(row, panel_dir, panel_id):
    fig, ax = plt.subplots(figsize=(6, 4))

    # Your custom visualization here
    ax.plot(row['x'], row['y'], marker='o')
    ax.set_title(f"{row['category']}: {row['metric']:.2f}")

    # Save panel
    panel_filename = f"panel_{panel_id}.png"
    fig.savefig(panel_dir / panel_filename, dpi=100)
    plt.close(fig)

    return panel_filename
```

### Add Filtering and Sorting

```python
display = (Display(data, name="my_display")
    .set_panel_column("panel")
    .infer_metas()
    .set_default_layout(ncol=3)
    .set_default_labels(["category", "value"])
    .set_default_sort([("value", "desc")])  # Sort by value
    .set_default_filter(varname="category", values=["A", "B"]))  # Filter to A and B
```

## Visualization Examples

### Time Series

```python
def create_panel(row, panel_dir, panel_id):
    fig, ax = plt.subplots(figsize=(6, 4))
    ax.plot(row['dates'], row['values'])
    ax.set_title(f"{row['ticker']} - Return: {row['return']:.1f}%")
    ax.set_xlabel('Date')
    ax.set_ylabel('Price')
    fig.savefig(panel_dir / f"panel_{panel_id}.png")
    plt.close(fig)
    return f"panel_{panel_id}.png"
```

### Scatter Plots

```python
def create_panel(row, panel_dir, panel_id):
    fig, ax = plt.subplots(figsize=(5, 5))
    ax.scatter(row['x_data'], row['y_data'], alpha=0.6)
    ax.set_title(f"R² = {row['r_squared']:.3f}")

    # Add regression line
    z = np.polyfit(row['x_data'], row['y_data'], 1)
    p = np.poly1d(z)
    ax.plot(row['x_data'], p(row['x_data']), "r--")

    fig.savefig(panel_dir / f"panel_{panel_id}.png")
    plt.close(fig)
    return f"panel_{panel_id}.png"
```

### Heatmaps

```python
import seaborn as sns

def create_panel(row, panel_dir, panel_id):
    fig, ax = plt.subplots(figsize=(6, 5))
    sns.heatmap(row['matrix'], annot=True, fmt='.2f', cmap='coolwarm', ax=ax)
    ax.set_title(f"{row['category']} Correlation Matrix")
    fig.savefig(panel_dir / f"panel_{panel_id}.png", dpi=120)
    plt.close(fig)
    return f"panel_{panel_id}.png"
```

## Troubleshooting

### Panels Not Showing

**Check**:
1. DevTools Console - any JavaScript errors?
2. DevTools Network - are panel PNGs loading (200 OK)?
3. displayInfo.json - is `"type": "file"` in panel source?
4. panels/ directory - do PNG files exist?

**Fix**: Ensure you're NOT calling `.set_panel_interface()`:
```python
# ✓ Correct (defaults to local files)
display = Display(data, name="my_display")
    .set_panel_column("panel")
    .infer_metas()

# ✗ Wrong (sets REST interface)
display.set_panel_interface(RESTPanelInterface(...))
```

### CORS Errors

**Problem**: Opening HTML files directly with `file://` protocol causes CORS errors.

**Solution**: Always use HTTP server:
```bash
cd output
python3 -m http.server 8000
```

### Viewer Shows "No Displays Found"

**Check**: Is the path in `initFunc` correct?

```javascript
// If HTML is in output/ and display is in output/my_display/
initFunc('trelliscope_root', './my_display');  // ✓ Correct

// NOT:
// 'my_display'      (missing ./)
// './my_display/'   (trailing slash)
// '/my_display'     (absolute path)
```

## Performance Tips

### Large Datasets

```python
from tqdm import tqdm

# Show progress bar
for idx, row in tqdm(data.iterrows(), total=len(data)):
    create_panel(row, panels_dir, idx)
```

### Parallel Generation

```python
from multiprocessing import Pool

def create_panel_wrapper(args):
    idx, row, panels_dir = args
    return create_panel(row, panels_dir, idx)

with Pool() as pool:
    args_list = [(idx, row, panels_dir) for idx, row in data.iterrows()]
    panel_ids = pool.map(create_panel_wrapper, args_list)
```

## Best Practices

1. **Test with small subset first** - Generate 5-10 panels before full dataset
2. **Use meaningful cognostics** - Include metadata for effective filtering/sorting
3. **Choose appropriate layout** - 3-4 columns for most displays
4. **Label wisely** - Show 2-3 most important variables
5. **Optimize image size** - Balance quality vs file size (DPI 100-150)

## Additional Resources

### External Documentation
- [trelliscopejs-lib Viewer](https://hafen.github.io/trelliscopejs-lib/)
- [py-trelliscope Main Docs](../docs/)

### Reference
- [R trelliscope Package](../reference/) - Original R implementation

## Support

**Questions or issues?**

1. Check [APPROACH_2_SUMMARY.md](APPROACH_2_SUMMARY.md) troubleshooting section
2. Review [template documentation](templates/README.md)
3. Examine [working example](simple_static_example.py)
4. Open issue on GitHub

---

**Last Updated**: 2025-11-03

**Status**: ✅ Production Ready
