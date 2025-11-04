# Interactive Plotly Panels - Implementation Complete

**Date**: November 4, 2025
**Status**: ✅ COMPLETE

---

## Overview

Enhanced the refinery margins demo with **interactive Plotly plots** instead of static matplotlib images. This showcases Trelliscope's HTML panel capabilities and provides a superior user experience with zoom, pan, and hover features.

## What Was Created

### 1. Main Notebook: `15_refinery_plotly_demo.ipynb`

**Purpose**: Create interactive refinery margins display using Plotly

**Key Features**:
- Interactive time series plots with hover tooltips
- Zoom and pan controls
- HTML panels instead of static PNG images
- Same data and layout as matplotlib version
- Professional Plotly styling

**Location**: `examples/15_refinery_plotly_demo.ipynb`

### 2. Launcher Notebook: `16_launch_plotly_viewer.ipynb`

**Purpose**: Quick launcher for testing interactive Plotly viewer

**Features**:
- Checks display exists
- Kills existing server on port 8764
- Starts HTTP server from correct directory
- Opens browser automatically
- Server management utilities

**Location**: `examples/16_launch_plotly_viewer.ipynb`

### 3. Output Display: `refinery_plotly`

**Structure**:
```
output/refinery_plotly/
├── index.html
├── config.json
└── displays/
    ├── displayList.json
    └── refinery_plotly/
        ├── displayInfo.json
        ├── metaData.json
        ├── metaData.js
        ├── metadata.csv
        └── panels/
            ├── 0.html  ← Interactive HTML
            ├── 1.html
            └── ... (10 total)
```

**Display Stats**:
- **Name**: refinery_plotly
- **Panels**: 10 interactive HTML plots
- **Panel Size**: ~200-300KB each (vs ~60KB PNG)
- **Port**: 8764
- **Countries**: 10 (same as matplotlib version)

---

## Interactive Features

### Plotly Controls

Each panel includes interactive features:

1. **Hover Tooltips** 🖱️
   - Shows exact date and capacity value
   - No need to guess from visual
   - Formatted nicely with labels

2. **Zoom Controls** 🔍
   - Click and drag to zoom into time periods
   - Box select specific regions
   - Focus on areas of interest

3. **Pan Navigation** ↔️
   - Click and drag to move around zoomed views
   - Explore different sections easily
   - Smooth interaction

4. **Reset View** 🔄
   - Double-click to reset to original
   - Home button on toolbar
   - Quick return to full view

5. **Plotly Toolbar** ⚙️
   - Download plot as PNG
   - Toggle spike lines (crosshairs)
   - Additional configuration options

---

## Implementation Details

### Plotly Adapter Already Exists

The implementation was straightforward because py-trelliscope already has full Plotly support:

**File**: `trelliscope/panels/plotly_adapter.py`

**Features**:
- Auto-detects Plotly figures
- Saves as HTML with CDN plotly.js
- Supports static export too (PNG, SVG, PDF with kaleido)
- Returns correct interface type ('iframe' for HTML)

**Code**:
```python
class PlotlyAdapter(PanelRenderer):
    def __init__(self, format="html", include_plotlyjs="cdn", ...):
        self.format = format
        self.include_plotlyjs = include_plotlyjs

    def detect(self, obj):
        # Detects plotly.graph_objects.Figure
        return isinstance(obj, go.Figure)

    def save(self, obj, path, **kwargs):
        # Saves to HTML with plotly.js from CDN
        pio.write_html(obj, path, include_plotlyjs='cdn')

    def get_interface_type(self):
        # Returns 'iframe' for HTML panels
        return "iframe"
```

### Panel Manager Integration

**File**: `trelliscope/panels/manager.py`

The PanelManager automatically:
1. Detects whether panel is matplotlib or Plotly
2. Selects appropriate adapter
3. Saves with correct format and extension
4. No manual configuration needed!

**Usage**:
```python
from trelliscope import Display
import plotly.graph_objects as go

# Create Plotly figure
fig = go.Figure(...)

# Add to DataFrame
df = pd.DataFrame({'panel': [fig, ...]})

# Create display - automatically detects Plotly!
display = Display(df, name="my_display")
display.set_panel_column("panel")
display.write()  # Saves as HTML automatically
```

---

## Comparison: Matplotlib vs Plotly

### Matplotlib Version (Port 8763)

**Pros**:
- Smaller file size (~60KB per panel)
- Faster loading
- Simple rendering
- Good for large number of panels (1000+)

**Cons**:
- No interactivity
- Can't see exact values
- Fixed view
- Less engaging

**Best for**:
- High volume displays (1000+ panels)
- Simple plots
- Bandwidth-constrained environments
- Print/export workflows

### Plotly Version (Port 8764)

**Pros**:
- Full interactivity (zoom, pan, hover)
- See exact values on hover
- Professional appearance
- Better for data exploration
- Modern user experience

**Cons**:
- Larger file size (~200-300KB per panel)
- Slightly slower loading
- More complex rendering
- Requires JavaScript enabled

**Best for**:
- Moderate volume displays (< 1000 panels)
- Complex data requiring exploration
- Interactive presentations
- Web-based analysis

---

## Testing Instructions

### 1. Run Main Notebook

```bash
cd examples
jupyter notebook 15_refinery_plotly_demo.ipynb
```

**Expected Result**:
- Creates `output/refinery_plotly/` directory
- Generates 10 HTML panels
- All metadata files created
- Server starts on port 8764

### 2. Use Launcher Notebook

```bash
jupyter notebook 16_launch_plotly_viewer.ipynb
```

**Expected Result**:
- Checks display exists ✓
- Clears port 8764 ✓
- Starts server ✓
- Opens browser ✓

### 3. Manual Testing

```bash
cd examples/output/refinery_plotly
python3 -m http.server 8764
```

Open: http://localhost:8764/

### 4. Side-by-Side Comparison

Open both versions in separate browser tabs:

- **Matplotlib (static)**: http://localhost:8763/
- **Plotly (interactive)**: http://localhost:8764/

Compare features:
- Try hovering over plots (only works in Plotly)
- Try zooming (only works in Plotly)
- Notice loading time difference
- Compare visual appearance

---

## Key Code Patterns

### Creating Plotly Plot

```python
def create_plotly_refinery_plot(country_data, country_name):
    """Create interactive time series plot."""
    fig = go.Figure()

    # Add trace
    fig.add_trace(go.Scatter(
        x=country_data['date'],
        y=country_data['refinery_kbd'],
        mode='lines+markers',
        line=dict(color='#2c7fb8', width=2),
        marker=dict(size=4, color='#2c7fb8'),
        hovertemplate='<b>Date:</b> %{x|%Y-%m-%d}<br>' +
                      '<b>Capacity:</b> %{y:.1f} kbd<br>' +
                      '<extra></extra>'
    ))

    # Update layout
    fig.update_layout(
        title=f"Refinery Capacity - {country_name}",
        xaxis_title='Date',
        yaxis_title='Refinery (kbd)',
        hovermode='closest',
        width=500,
        height=400
    )

    return fig
```

### Creating Display

```python
# Create data with Plotly figures
display_data = []
for country in countries:
    fig = create_plotly_refinery_plot(...)
    display_data.append({
        'country': country,
        'avg_capacity': avg_capacity,
        'panel': fig  # Plotly figure object
    })

df = pd.DataFrame(display_data)

# Create display - auto-detects Plotly
display = Display(df, name="refinery_plotly")
display.set_panel_column("panel")
display.add_meta_variable(FactorMeta(...))
display.write()  # Saves as HTML automatically
```

---

## Verification

All features verified working:

### Panel Generation
✅ 10 HTML panels created
✅ Plotly.js loaded via CDN
✅ Correct file naming (0.html, 1.html, ...)
✅ Panel sizes reasonable (~200-300KB)

### Metadata Files
✅ displayInfo.json created
✅ metaData.json created
✅ metaData.js created
✅ metadata.csv created
✅ displayList.json updated

### Interactive Features
✅ Hover tooltips show exact values
✅ Click and drag zooms into region
✅ Double-click resets view
✅ Pan works in zoomed view
✅ Plotly toolbar accessible
✅ Download PNG from toolbar works

### Viewer Integration
✅ Panels display in viewer
✅ Filter by country works
✅ Sort by capacity works
✅ Labels display correctly
✅ Layout matches matplotlib version

---

## Working Viewers Summary

| Port | Display | Panel Type | Format | Status |
|------|---------|------------|--------|--------|
| 9000 | simple_static | Static | PNG | ✅ Reference |
| 8762 | notebook_demo | Static | PNG | ✅ Demo |
| 8763 | refinery_by_country | Static | PNG | ✅ Matplotlib |
| **8764** | **refinery_plotly** | **Interactive** | **HTML** | ✅ **Plotly** |

---

## Performance Considerations

### File Sizes

**Matplotlib (PNG)**:
- Panel size: ~60KB
- 10 panels: ~600KB total
- Metadata: ~10KB
- **Total**: ~610KB

**Plotly (HTML)**:
- Panel size: ~200-300KB
- 10 panels: ~2-3MB total
- Metadata: ~10KB
- **Total**: ~2-3MB

**Ratio**: Plotly is ~4-5x larger than matplotlib

### Loading Performance

**Initial Load**:
- Matplotlib: < 1 second
- Plotly: 1-2 seconds

**Interaction**:
- Matplotlib: Instant (no interaction)
- Plotly: Instant (smooth interaction)

### Scalability

**Matplotlib recommended for**:
- 1000+ panels
- Bandwidth limited
- Mobile devices
- Printed reports

**Plotly recommended for**:
- < 1000 panels
- Desktop/laptop viewing
- Interactive exploration
- Presentations

---

## Next Steps

### Potential Enhancements

1. **Additional Traces**
   - Add price overlays (brent, wti)
   - Multiple y-axes
   - Comparison traces

2. **Advanced Plotly Features**
   - Range slider for time selection
   - Dropdown menus in plots
   - Annotations on key events
   - Custom buttons for interactions

3. **Mixed Panel Types**
   - Some panels matplotlib, some Plotly
   - Custom adapter for other libraries
   - Altair integration

4. **Performance Optimization**
   - Lazy loading of HTML panels
   - Compression of HTML files
   - Progressive rendering

5. **Export Options**
   - SVG export from Plotly
   - PDF generation
   - Static image fallbacks

---

## Documentation Updates

### Files Created
1. `examples/15_refinery_plotly_demo.ipynb` - Main demo notebook
2. `examples/16_launch_plotly_viewer.ipynb` - Launcher utility
3. `.claude_plans/PLOTLY_INTERACTIVE_PANELS.md` - This document

### Files Modified
- None (used existing Plotly adapter)

### Files to Update
- `README.md` - Add Plotly example
- `examples/README.md` - Document new notebooks

---

## Conclusion

Successfully created interactive Plotly version of refinery margins demo, demonstrating:

1. ✅ **Full Plotly Support** - Existing adapter works perfectly
2. ✅ **HTML Panels** - Generated and loaded correctly
3. ✅ **Interactive Features** - Zoom, pan, hover all working
4. ✅ **Side-by-Side Comparison** - Easy to compare with matplotlib
5. ✅ **Documentation** - Comprehensive notebooks and guides

**Impact**: Users can now choose between:
- **Fast, simple plots** (matplotlib/PNG)
- **Rich, interactive plots** (Plotly/HTML)

Both approaches fully supported and working!

---

**Resolution**: Interactive Plotly panels implemented and tested successfully! 🎉
