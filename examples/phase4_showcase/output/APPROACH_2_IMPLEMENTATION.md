# Approach 2: Simple Static Panel Implementation

## Summary

Successfully reverted to the simpler standalone viewer approach that was working before (test_html_panels.html style). This uses:

- **Viewer**: CDN-loaded trelliscopejs-lib v0.7.16 (no fork needed)
- **Panels**: Pre-rendered static PNG files
- **Panel Interface**: Local file-based (`"type": "file"`)
- **No REST API**: No panel server needed

---

## Key Differences from REST Approach (Approach 3)

| Feature | Approach 2 (Static Files) | Approach 3 (REST Panels) |
|---------|---------------------------|--------------------------|
| **Viewer** | CDN v0.7.16 (stable) | Forked viewer (custom) |
| **Panels** | Pre-rendered PNG files | Generated on-demand |
| **panelInterface** | `{"type": "file", "isLocal": true}` | `{"type": "REST", "base": "url"}` |
| **Server needed** | No | Yes (Flask panel server) |
| **Complexity** | Simple | More complex |
| **Use case** | Static displays | Dynamic displays |

---

## Files Created

### 1. Python Example: `simple_static_example.py`

```python
# Key differences from REST version:
# 1. DON'T call .set_panel_interface() - defaults to local files
# 2. Pre-render panels as PNG files
# 3. Store panel filenames in DataFrame

# Example:
display = (Display(data, name="simple_static")
    .set_panel_column("panel")     # Panel column has filenames
    .infer_metas()                  # No panel interface set!
    .write(output_path=output_path, render_panels=False))
```

### 2. HTML Viewer: `simple_static_viewer.html`

```html
<!-- Load viewer from CDN -->
<link rel="stylesheet" href="https://unpkg.com/trelliscopejs-lib@0.7.16/dist/assets/index.css">

<!-- Initialize with path to display directory -->
<script type="module">
    const module = await import('https://unpkg.com/trelliscopejs-lib@0.7.16/dist/assets/index.js');
    const initFunc = window.trelliscopeApp || module.trelliscopeApp;
    initFunc('trelliscope_root', './simple_static');
</script>
```

### 3. Generated Files

```
simple_static/
├── displayInfo.json       # Contains "type": "file" panel interface
├── metadata.csv          # Cognostics data
└── panels/
    ├── panel_0.png
    ├── panel_1.png
    ├── panel_2.png
    ├── panel_3.png
    └── panel_4.png
```

---

## displayInfo.json Format

```json
{
  "name": "simple_static",
  "metas": [
    {
      "varname": "panel",
      "type": "panel",
      "paneltype": "img",
      "source": {
        "type": "file",        // LOCAL FILES, not REST
        "isLocal": true,
        "port": 0
      }
    }
  ],
  "primarypanel": "panel",
  "dataSource": "./metadata.csv",
  "n": 5
}
```

**Compare with REST approach:**
```json
{
  "source": {
    "type": "REST",          // REST API
    "url": "http://localhost:5001/api/panels/display_name"
  }
}
```

---

## How Panel Loading Works

### Approach 2 (Static Files):
1. Viewer loads displayInfo.json
2. Sees `"type": "file"` panel interface
3. Loads metadata.csv
4. For each panel, constructs file path: `panels/panel_{id}.png`
5. Loads PNG directly as `<img src="panels/panel_0.png">`

### Approach 3 (REST):
1. Viewer loads displayInfo.json
2. Sees `"type": "REST"` panel interface
3. Loads metadata.csv
4. For each panel, makes HTTP request: `GET /api/panels/display/0`
5. Server generates/serves PNG on-demand

---

## When to Use Each Approach

### Use Approach 2 (Static Files) When:
- ✅ Panels can be pre-rendered
- ✅ Display is relatively small (< 1000 panels)
- ✅ Want simple deployment (just files, no server)
- ✅ Want maximum compatibility
- ✅ Need it to work without network/server

### Use Approach 3 (REST) When:
- ✅ Panels are expensive to generate (save time by generating on-demand)
- ✅ Display is very large (100,000+ panels - don't want to store all)
- ✅ Panels are dynamic (data changes frequently)
- ✅ Need authentication/authorization
- ✅ Want to serve from remote API

---

## Testing Checklist

### ✅ Pre-Flight
- [x] simple_static_example.py runs without errors
- [x] Generates displayInfo.json with `"type": "file"`
- [x] Creates panels/ directory with PNG files
- [x] metadata.csv contains correct data

### ✅ Browser Testing
1. Open `simple_static_viewer.html` in browser
2. Check DevTools Console - should see:
   - "Loading viewer module..."
   - "Module loaded..."
   - "✓ Viewer initialized"
3. Check DevTools Network tab - should see:
   - GET displayInfo.json (200 OK)
   - GET metadata.csv (200 OK)
   - GET panels/panel_0.png (200 OK)
   - GET panels/panel_1.png (200 OK)
   - etc.
4. Visual check:
   - 5 panels displayed in 3-column grid
   - Each panel shows a bar chart
   - Labels show category and value
   - Can filter by category
   - Can sort by value

---

## Advantages of This Approach

1. **Simplicity**: No forked viewer, no panel server, just files
2. **Reliability**: Uses stable CDN version (0.7.16)
3. **Speed**: No HTTP requests for panels (direct file access)
4. **Deployment**: Just copy files to web server
5. **Offline**: Works without internet (if viewer cached)

---

## Python Code Pattern

```python
# Complete working example:

import pandas as pd
import matplotlib.pyplot as plt
from pathlib import Path
from trelliscope import Display

# 1. Create data
data = pd.DataFrame({
    'id': [0, 1, 2],
    'value': [10, 20, 30],
    'category': ['A', 'B', 'C'],
})

# 2. Generate panels as PNG files
output_dir = Path("output/my_display/panels")
output_dir.mkdir(parents=True, exist_ok=True)

panel_paths = []
for idx, row in data.iterrows():
    fig, ax = plt.subplots(figsize=(5, 5))
    ax.bar([row['category']], [row['value']])
    panel_path = output_dir / f"panel_{idx}.png"
    fig.savefig(panel_path)
    plt.close(fig)
    panel_paths.append(str(panel_path.name))

data['panel'] = panel_paths

# 3. Create display WITHOUT setting panel_interface
# This defaults to local file-based panels
display = (Display(data, name="my_display")
    .set_panel_column("panel")
    .infer_metas()
    .set_default_layout(ncol=3))

# 4. Write display (panels already rendered)
display.write(output_path="output/my_display", render_panels=False, force=True)

# 5. Create HTML viewer
html = '''
<!DOCTYPE html>
<html>
<head>
    <link rel="stylesheet" href="https://unpkg.com/trelliscopejs-lib@0.7.16/dist/assets/index.css">
</head>
<body>
    <div id="trelliscope_root" class="trelliscope-not-spa"></div>
    <script type="module">
        const module = await import('https://unpkg.com/trelliscopejs-lib@0.7.16/dist/assets/index.js');
        (window.trelliscopeApp || module.trelliscopeApp)('trelliscope_root', './my_display');
    </script>
</body>
</html>
'''

with open("output/my_display_viewer.html", "w") as f:
    f.write(html)

# 6. Open in browser
# open output/my_display_viewer.html
```

---

## Troubleshooting

### Issue: Panels not showing in viewer

**Check:**
1. DevTools Console - any errors?
2. DevTools Network - are panel PNGs loading?
3. displayInfo.json - is `"type": "file"` set correctly?
4. Panel paths - do they match metadata panel column?

**Solution:**
- Ensure panel column in data has correct filenames (just filename, not full path)
- Check panels/ directory exists and contains PNG files
- Verify PNG files are named correctly (panel_0.png, panel_1.png, etc.)

### Issue: Viewer shows "No displays found"

**Check:**
1. Is HTML viewer in correct location (parent of display dir)?
2. Is path to display correct in initFunc call?

**Solution:**
```html
<!-- If HTML is in output/ and display is in output/simple_static/ -->
<script>
initFunc('trelliscope_root', './simple_static');  // Correct
// NOT: '/simple_static' (absolute)
// NOT: 'simple_static' (no ./)
</script>
```

---

## Next Steps

1. **Test in browser** - Open `simple_static_viewer.html` and verify panels load
2. **Use the template** - See [templates/static_display_template.py](../../templates/static_display_template.py) for reusable template
3. **Quick start** - Follow [templates/QUICK_START.md](../../templates/QUICK_START.md) for 5-minute tutorial
4. **Create more examples** - Try with different data/visualizations
5. **Deploy** - Copy files to web server (no special configuration needed)

---

## Comparison to test_html_panels.html

The `test_html_panels.html` that worked before used:
- Same CDN viewer (v0.7.16)
- Same local file approach
- config.json + displays/ structure

Our Approach 2 is essentially the same pattern, just with cleaner Python generation.

---

## Status: ✅ COMPLETE

Approach 2 implementation is complete and ready for testing. This provides a simpler, more reliable alternative to the REST panel approach.

**Created:** 2025-11-03

**Example Files:**
- `examples/simple_static_example.py` - Working example
- `examples/output/simple_static/` - Generated display
- `examples/output/simple_static_viewer.html` - HTML viewer
- `examples/output/simple_static_test.html` - Debug viewer with interceptors
- `examples/output/APPROACH_2_IMPLEMENTATION.md` - This document

**Reusable Templates:**
- `examples/templates/static_display_template.py` - Complete template for static displays
- `examples/templates/README.md` - Template usage guide
- `examples/templates/QUICK_START.md` - 5-minute quick start tutorial

## Resources

- **Quick Start**: [templates/QUICK_START.md](../../templates/QUICK_START.md)
- **Template Guide**: [templates/README.md](../../templates/README.md)
- **Working Example**: [simple_static_example.py](../../simple_static_example.py)
- **trelliscopejs-lib Docs**: https://hafen.github.io/trelliscopejs-lib/
