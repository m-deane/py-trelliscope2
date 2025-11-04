# Approach 2: Static Panel Displays - Complete Workflow

This document provides a comprehensive overview of the Approach 2 implementation for creating static panel trelliscope displays.

## Overview

**Approach 2** is the simpler, file-based approach to creating trelliscope displays using pre-rendered panel images. This approach:

- Uses **static PNG/JPEG files** for panels (not REST API)
- Uses **CDN-loaded viewer** v0.7.16 (not forked viewer)
- Requires **no server infrastructure** (just static file serving)
- Is **compatible with the original working pattern** (test_html_panels.html)

## Architecture

```
┌─────────────────┐
│  Python Script  │
│   (Your Code)   │
└────────┬────────┘
         │
         ├─> Generate Data (DataFrame)
         │
         ├─> Create Panel Images (matplotlib/plotly/etc.)
         │   └─> Save to panels/*.png
         │
         ├─> Create Display Object
         │   └─> Don't set panel_interface (defaults to local files)
         │
         └─> Write Display
             └─> Generates displayInfo.json + metadata.csv

┌─────────────────────────────────────────────────┐
│  Output Structure                               │
├─────────────────────────────────────────────────┤
│  my_display/                                    │
│  ├── displayInfo.json  (panel source: "file")  │
│  ├── metadata.csv                               │
│  └── panels/                                    │
│      ├── panel_0.png                            │
│      ├── panel_1.png                            │
│      └── ...                                    │
│                                                  │
│  my_display_viewer.html  (CDN viewer)          │
└─────────────────────────────────────────────────┘
         │
         ▼
┌─────────────────┐
│   HTTP Server   │  (python3 -m http.server)
└────────┬────────┘
         │
         ▼
┌─────────────────┐
│     Browser     │
│  (Loads viewer, │
│   then panels)  │
└─────────────────┘
```

## Complete Workflow

### 1. Prepare Your Environment

```bash
# Activate virtual environment
conda activate py-trelliscope

# Navigate to examples directory
cd /path/to/py-trelliscope2/examples
```

### 2. Create Your Display Script

**Option A: Use the Template (Recommended)**

```bash
# Copy template
cp templates/static_display_template.py my_analysis.py

# Edit my_analysis.py:
# - Change DISPLAY_NAME
# - Update generate_data()
# - Customize create_panel()
# - Adjust layout/labels
```

**Option B: From Scratch**

```python
import pandas as pd
import matplotlib.pyplot as plt
from pathlib import Path
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
    # Create visualization
    fig, ax = plt.subplots(figsize=(5, 5))
    ax.bar([row['category']], [row['value']])
    ax.set_title(f"{row['category']}: {row['value']}")

    # Save panel
    fig.savefig(panels_dir / f"panel_{idx}.png")
    plt.close(fig)
    panel_ids.append(str(idx))

data['panel'] = panel_ids

# 3. Create display (NO panel_interface set = defaults to local files)
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

### 3. Run Your Script

```bash
python my_analysis.py
```

Expected output:
```
Creating Static Trelliscope Display: my_display
Step 1: Loading data...
✓ Loaded 5 rows with 4 columns

Step 2: Setting up output directory...

Step 3: Generating panels...
Generating 5 panels...
✓ Generated all 5 panels

Step 4: Creating display configuration...
✓ Display configuration created

Step 5: Writing display files...
✓ Display files written

Step 6: Creating viewer HTML...
✓ Viewer HTML created

✓ Display creation complete!
```

### 4. Start HTTP Server

```bash
cd output
python3 -m http.server 8000
```

### 5. Open in Browser

```bash
# Open viewer
open http://localhost:8000/my_display_viewer.html

# Or navigate manually:
# http://localhost:8000/my_display_viewer.html
```

### 6. Explore Your Display

You should see:
- Grid of panels with your visualizations
- Sidebar with filter/sort controls
- Labels showing cognostic values on each panel
- Interactive filtering and sorting capabilities

## Key Principles

### ✅ DO:

1. **Pre-render panels** as PNG/JPEG files before creating Display
2. **Store panel IDs** (not filenames) in panel column
3. **DON'T call** `.set_panel_interface()` - let it default to local files
4. **Use `render_panels=False`** when writing Display (panels already rendered)
5. **Serve via HTTP** - don't open HTML files directly (CORS issues)

### ❌ DON'T:

1. **Don't set panel_interface** - it should default to `{"type": "file"}`
2. **Don't use REST API** - this is for static files only
3. **Don't use forked viewer** - use stable CDN version (v0.7.16)
4. **Don't open file:// URLs** - always use HTTP server
5. **Don't store full paths in panel column** - just IDs (0, 1, 2, ...)

## File Structure Details

### displayInfo.json

```json
{
  "name": "my_display",
  "description": "My analysis",
  "metas": [
    {
      "varname": "panel",
      "type": "panel",
      "paneltype": "img",
      "aspect": 1.0,
      "source": {
        "type": "file",         // ← KEY: local files, not REST
        "isLocal": true,
        "port": 0
      }
    },
    {
      "varname": "category",
      "type": "factor",
      "levels": ["A", "B", "C", "D", "E"]
    },
    {
      "varname": "value",
      "type": "number",
      "digits": 2
    }
  ],
  "dataSource": "./metadata.csv",
  "n": 5,
  "primarypanel": "panel",
  "state": {
    "layout": {"ncol": 3, "nrow": null, "page": 1},
    "labels": ["category", "value"],
    "sort": [],
    "filter": []
  }
}
```

### metadata.csv

```csv
id,value,category,panel
0,10,A,0
1,25,B,1
2,15,C,2
3,30,D,3
4,20,E,4
```

**Important**: Panel column contains just IDs (0-4), viewer constructs paths as `panels/panel_{id}.png`

### Panel Files

```
panels/
├── panel_0.png  (491x490 PNG)
├── panel_1.png
├── panel_2.png
├── panel_3.png
└── panel_4.png
```

## Comparison to Other Approaches

| Feature | Approach 2 (Static) | Approach 3 (REST) |
|---------|---------------------|-------------------|
| **Panel Source** | Pre-rendered PNG files | Generated on-demand |
| **Viewer** | CDN v0.7.16 | Forked viewer |
| **Panel Interface** | `{"type": "file"}` | `{"type": "REST"}` |
| **Server Required** | No (just HTTP) | Yes (Flask API) |
| **Best For** | Small-medium displays | Large/dynamic displays |
| **Complexity** | Simple | Complex |
| **Deployment** | Copy files | Server + API |

## When to Use Approach 2

### ✅ Perfect For:

- Displays with < 10,000 panels
- Panels can be pre-rendered
- Static/unchanging data
- Simple deployment requirements
- Offline capability needed
- Maximum compatibility desired

### ❌ Not Ideal For:

- Very large displays (100k+ panels)
- Panels are expensive to generate
- Data changes frequently
- Dynamic/interactive panels
- Need server-side computation

## Troubleshooting

### Panels Not Showing

**Symptoms**: Viewer loads but panels are blank or missing

**Check**:
1. DevTools Console - any errors?
2. DevTools Network - are panel PNG files loading?
3. displayInfo.json - is `"type": "file"` present?
4. panels/ directory - do PNG files exist?

**Fix**:
```python
# Ensure you're NOT setting panel_interface
display = (Display(data, name="my_display")
    .set_panel_column("panel")
    .infer_metas())  # ← No .set_panel_interface() call

# Ensure render_panels=False (panels already rendered)
display.write(output_path=output_dir, render_panels=False, force=True)
```

### CORS Errors

**Symptoms**: Console shows CORS errors, resources fail to load

**Cause**: Opening HTML file directly with `file://` protocol

**Fix**: Always use HTTP server
```bash
cd output
python3 -m http.server 8000
open http://localhost:8000/my_display_viewer.html
```

### Viewer Shows "No Displays Found"

**Symptoms**: Viewer loads but shows empty state

**Check**:
1. Is viewer HTML in correct location? (parent of display directory)
2. Is path in initFunc correct?

**Fix**:
```javascript
// If HTML is in output/ and display is in output/my_display/
initFunc('trelliscope_root', './my_display');  // ✓ Correct

// NOT:
// './my_display/'  (trailing slash)
// 'my_display'     (missing ./)
// '/my_display'    (absolute path)
```

### Panel Paths Wrong

**Symptoms**: Network tab shows 404 errors for panel images

**Check**:
1. Panel column in metadata.csv - contains just IDs (0, 1, 2)?
2. Panel files named correctly - panel_0.png, panel_1.png?

**Fix**:
```python
# Store just the ID, not full filename
panel_ids.append(str(idx))  # ✓ Correct: "0", "1", "2"

# NOT:
# panel_ids.append(f"panel_{idx}.png")  # ✗ Wrong
# panel_ids.append(str(panel_path))      # ✗ Wrong
```

## Advanced Topics

### Parallel Panel Generation

```python
from multiprocessing import Pool
from functools import partial

def create_panel_wrapper(args):
    idx, row, panels_dir = args
    return create_panel(row, panels_dir, idx)

# Generate panels in parallel
with Pool() as pool:
    args_list = [(idx, row, panels_dir) for idx, row in data.iterrows()]
    panel_ids = pool.map(create_panel_wrapper, args_list)
```

### Progress Tracking

```python
from tqdm import tqdm

for idx, row in tqdm(data.iterrows(), total=len(data), desc="Generating panels"):
    create_panel(row, panels_dir, idx)
```

### Custom Meta Variable Configuration

```python
display = (Display(data, name="my_display")
    .set_panel_column("panel")
    .infer_metas()  # Auto-detect types
    .update_meta(
        varname="value",
        desc="Measured value in units",
        digits=2,
        locale=True  # Format with locale-specific separators
    )
    .update_meta(
        varname="category",
        desc="Sample category classification"
    ))
```

### Default State Configuration

```python
display = (Display(data, name="my_display")
    .set_panel_column("panel")
    .infer_metas()
    .set_default_layout(ncol=4, nrow=2)
    .set_default_labels(["category", "value", "region"])
    .set_default_sort([("value", "desc"), ("category", "asc")])
    .set_default_filter(varname="region", values=["North", "South"]))
```

## Resources

### Documentation
- [Approach 2 Implementation Guide](output/APPROACH_2_IMPLEMENTATION.md) - Detailed technical documentation
- [Template README](templates/README.md) - Template usage guide
- [Quick Start](templates/QUICK_START.md) - 5-minute tutorial

### Code
- [static_display_template.py](templates/static_display_template.py) - Reusable template
- [simple_static_example.py](simple_static_example.py) - Working example
- [test_html_panels.html](output/test_html_panels.html) - Original working reference

### External
- [trelliscopejs-lib Documentation](https://hafen.github.io/trelliscopejs-lib/)
- [py-trelliscope Main Docs](../docs/)

## Examples Gallery

### Time Series Display

```python
# Create time series display with 50 stock charts
import yfinance as yf

tickers = ['AAPL', 'GOOGL', 'MSFT', ...]  # 50 tickers

data = []
for ticker in tickers:
    stock = yf.Ticker(ticker)
    hist = stock.history(period="1y")

    data.append({
        'ticker': ticker,
        'data': hist,
        'return_1y': (hist['Close'][-1] / hist['Close'][0] - 1) * 100,
        'volatility': hist['Close'].pct_change().std() * 100,
        'sector': stock.info.get('sector', 'Unknown')
    })

df = pd.DataFrame(data)

# Generate panels
for idx, row in df.iterrows():
    fig, ax = plt.subplots(figsize=(6, 4))
    ax.plot(row['data'].index, row['data']['Close'])
    ax.set_title(f"{row['ticker']} - 1Y Return: {row['return_1y']:.1f}%")
    fig.savefig(panels_dir / f"panel_{idx}.png")
    plt.close(fig)
```

### Geographic Display

```python
# Create map display with regional statistics
import geopandas as gpd

regions = gpd.read_file('regions.shp')

data = []
for idx, region in regions.iterrows():
    data.append({
        'region': region['name'],
        'population': region['population'],
        'area': region['area'],
        'density': region['population'] / region['area'],
        'geometry': region['geometry']
    })

df = pd.DataFrame(data)

# Generate map panels
for idx, row in df.iterrows():
    fig, ax = plt.subplots(figsize=(5, 5))
    gpd.GeoDataFrame([row]).plot(ax=ax)
    ax.set_title(f"{row['region']} - Density: {row['density']:.0f}/km²")
    fig.savefig(panels_dir / f"panel_{idx}.png")
    plt.close(fig)
```

## Status

**Status**: ✅ Production Ready

**Last Updated**: 2025-11-03

**Tested**: ✓ Working with py-trelliscope v0.1.0

**Browser Compatibility**: Chrome, Firefox, Safari, Edge (latest versions)

**Dependencies**:
- Python 3.8+
- pandas
- trelliscope
- matplotlib (or plotly, altair)

## Support

For issues or questions:
1. Check [troubleshooting section](#troubleshooting) above
2. Review [APPROACH_2_IMPLEMENTATION.md](output/APPROACH_2_IMPLEMENTATION.md)
3. See [examples](.) for working code
4. Open issue on GitHub
