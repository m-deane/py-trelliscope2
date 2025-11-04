# Trelliscope Viewer - Quick Start Guide

## 🚀 Getting Started

### Basic Usage

```python
import pandas as pd
import matplotlib.pyplot as plt
from trelliscope import Display
from trelliscope.viewer import generate_viewer_html, write_index_html

# 1. Create your data with panels
def make_plot(row):
    fig, ax = plt.subplots(figsize=(4, 3))
    ax.bar(['Value'], [row['value']], color='steelblue')
    ax.set_title(f"{row['category']}")
    plt.tight_layout()
    return fig

df = pd.DataFrame({
    'category': ['A', 'B', 'C'],
    'value': [10, 20, 30],
    'score': [1.5, 2.3, 3.1]
})

df['panel'] = df.apply(make_plot, axis=1)

# 2. Create and write display
display = Display(df, name='my_display', path='./output')
display.set_panel_column('panel')
display.infer_metas()
display.write()

# 3. Generate viewer HTML
html = generate_viewer_html('my_display')
write_index_html('./output/index.html', html)

# 4. View in browser
print("Open: http://localhost:8000/index.html")
```

### Start Local Server

```bash
cd output
python -m http.server 8000
```

Then open: http://localhost:8000/index.html

---

## 📋 Key Requirements

### Data Structure

Your DataFrame must have:
- **Panel column**: Contains matplotlib figures, plotly figures, or file paths
- **Metadata columns**: Additional columns become filterable/sortable cognostics

### File Organization

```
output/
├── index.html              # Viewer entry point (generated)
└── my_display/
    ├── displayInfo.json    # Display configuration (auto-generated)
    ├── metadata.csv        # Data + panel references (auto-generated)
    └── panels/
        ├── 0.png           # Rendered panels (auto-generated)
        ├── 1.png
        └── 2.png
```

---

## 🔧 Advanced Configuration

### Custom Viewer Config

```python
from trelliscope.viewer import generate_viewer_html, write_index_html

html = generate_viewer_html(
    'my_display',
    viewer_version='0.7.16',  # Specific version
    config={
        'spa': False,  # Not a single-page app
        'theme': 'dark'  # Custom theme (if supported)
    }
)
```

### Panel Options

```python
display = Display(df, name='my_display')
display.set_panel_column('panel')
display.set_panel_options(
    width=400,
    height=300,
    aspect=1.33
)
```

### Layout Options

```python
display.set_default_layout(ncol=4, nrow=3)  # 4 columns, 3 rows per page
```

---

## 🐛 Troubleshooting

### Viewer Shows Blank Page

**Check**:
1. Server is running from correct directory (where index.html is)
2. Browser console for errors (F12 → Console tab)
3. Network tab shows displayInfo.json loads successfully (HTTP 200)

**Common Fixes**:
```bash
# Make sure you're in the output directory
cd output  # NOT in the display subdirectory!
python -m http.server 8000
```

### 404 Error on displayInfo.json

**Problem**: Server running from wrong directory

**Fix**: Server must run from directory containing `index.html`, not the display folder

```bash
# WRONG
cd output/my_display
python -m http.server 8000

# CORRECT
cd output
python -m http.server 8000
```

### Panels Not Showing

**Check metadata.csv**:
```bash
head output/my_display/metadata.csv
```

Should include `panel` column with IDs:
```csv
category,value,score,panel
A,10,1.5,0
B,20,2.3,1
C,30,3.1,2
```

If panel column is missing, regenerate display with latest code.

### CORS Errors

**Problem**: Opening file:// URLs directly

**Fix**: Must use http server
```bash
cd output
python -m http.server 8000
# Open http://localhost:8000/index.html (not file:///...)
```

---

## 📖 Examples

### Example 1: Basic Bar Charts

```python
import pandas as pd
import matplotlib.pyplot as plt
from trelliscope import Display
from trelliscope.viewer import generate_viewer_html, write_index_html

# Data
df = pd.DataFrame({
    'id': range(10),
    'category': ['A', 'B', 'C'] * 3 + ['A'],
    'value': [10, 15, 20, 25, 30, 35, 40, 45, 50, 55]
})

# Create panels
def make_bar(row):
    fig, ax = plt.subplots(figsize=(4, 3))
    ax.bar([row['category']], [row['value']], color='steelblue')
    ax.set_ylabel('Value')
    plt.tight_layout()
    return fig

df['panel'] = df.apply(make_bar, axis=1)

# Create display
display = Display(df, name='bar_charts', path='./output')
display.set_panel_column('panel')
display.infer_metas()
display.write()

# Generate viewer
html = generate_viewer_html('bar_charts')
write_index_html('./output/index.html', html)
```

### Example 2: Time Series Plots

```python
import pandas as pd
import matplotlib.pyplot as plt
import numpy as np
from trelliscope import Display
from trelliscope.viewer import generate_viewer_html, write_index_html

# Generate time series data
categories = ['Product A', 'Product B', 'Product C']
data = []

for cat in categories:
    dates = pd.date_range('2024-01-01', periods=100, freq='D')
    values = np.cumsum(np.random.randn(100)) + 100

    data.append({
        'category': cat,
        'start_date': dates[0],
        'end_date': dates[-1],
        'mean_value': values.mean(),
        'dates': dates,
        'values': values
    })

df = pd.DataFrame(data)

# Create time series panels
def make_timeseries(row):
    fig, ax = plt.subplots(figsize=(6, 3))
    ax.plot(row['dates'], row['values'], linewidth=2)
    ax.set_title(row['category'])
    ax.set_ylabel('Value')
    ax.grid(True, alpha=0.3)
    plt.tight_layout()
    return fig

df['panel'] = df.apply(make_timeseries, axis=1)

# Keep only scalar columns for display metadata
display_df = df[['category', 'start_date', 'end_date', 'mean_value', 'panel']].copy()

# Create display
display = Display(display_df, name='timeseries', path='./output')
display.set_panel_column('panel')
display.infer_metas()
display.write()

# Generate viewer
html = generate_viewer_html('timeseries')
write_index_html('./output/index.html', html)
```

### Example 3: Plotly Interactive Panels

```python
import pandas as pd
import plotly.graph_objects as go
from trelliscope import Display
from trelliscope.viewer import generate_viewer_html, write_index_html

# Data
df = pd.DataFrame({
    'country': ['USA', 'China', 'India', 'Japan'],
    'population': [331, 1439, 1380, 126],  # millions
    'gdp': [21.4, 14.7, 2.9, 5.0]  # trillion USD
})

# Create Plotly panels
def make_plotly_bar(row):
    fig = go.Figure(data=[
        go.Bar(
            x=['Population (M)', 'GDP (T)'],
            y=[row['population'], row['gdp'] * 100],  # Scale GDP
            marker_color=['lightblue', 'lightgreen']
        )
    ])
    fig.update_layout(
        title=row['country'],
        yaxis_title='Value',
        height=300,
        width=400
    )
    return fig

df['panel'] = df.apply(make_plotly_bar, axis=1)

# Create display
display = Display(df, name='plotly_demo', path='./output')
display.set_panel_column('panel')
display.infer_metas()
display.write()

# Generate viewer
html = generate_viewer_html('plotly_demo')
write_index_html('./output/index.html', html)
```

---

## 🎯 Best Practices

### 1. Data Preparation

```python
# ✅ DO: Keep scalar metadata
df = pd.DataFrame({
    'id': [1, 2, 3],
    'category': ['A', 'B', 'C'],  # Scalar
    'mean_value': [10.5, 20.3, 30.1],  # Scalar
    'panel': [fig1, fig2, fig3]  # Figure objects
})

# ❌ DON'T: Include arrays/lists in metadata
df['raw_data'] = [[1,2,3], [4,5,6], [7,8,9]]  # Will cause issues
```

### 2. Panel Creation

```python
# ✅ DO: Close figures to save memory
def make_plot(row):
    fig, ax = plt.subplots()
    ax.plot(row['data'])
    plt.tight_layout()
    # Figure will be rendered then closed automatically
    return fig

# ❌ DON'T: Keep all figures in memory
figures = []
for i in range(1000):
    fig = plt.figure()  # Creates 1000 figures in memory!
    figures.append(fig)
```

### 3. File Organization

```python
# ✅ DO: Organize by project
output/
├── project1/
│   ├── index.html
│   └── display1/
├── project2/
│   ├── index.html
│   └── display2/

# ✅ DO: Use descriptive names
Display(df, name='sales_by_region_2024')  # Clear
Display(df, name='data')  # Vague
```

---

## 📚 API Reference

### Display Creation

```python
from trelliscope import Display

display = Display(
    data,                    # pandas DataFrame
    name='my_display',       # Display name (alphanumeric + underscore)
    description='...',       # Optional description
    path='./output',         # Output directory
    key_cols=None,          # Optional key columns
    panel_column=None        # Will be set with set_panel_column()
)
```

### Display Configuration

```python
# Set panel column
display.set_panel_column('panel')

# Configure panel rendering
display.set_panel_options(
    width=400,
    height=300,
    aspect=1.33
)

# Set default layout
display.set_default_layout(
    ncol=4,
    nrow=3,
    page=1,
    arrangement='row'  # or 'col'
)

# Infer metadata types
display.infer_metas()

# Write to disk
display.write(force=False)  # Set force=True to overwrite
```

### Viewer HTML Generation

```python
from trelliscope.viewer import generate_viewer_html, write_index_html

# Generate HTML
html = generate_viewer_html(
    display_name='my_display',
    viewer_version='0.7.16',  # or 'latest'
    config={}  # Optional viewer config
)

# Write to file
write_index_html(
    output_path='./output/index.html',
    html=html
)
```

---

## 🔗 Related Documentation

- **[Complete Fix Summary](./.claude_plans/VIEWER_FIX_SUMMARY.md)** - Technical details of viewer implementation
- **[Project Plan](./.claude_plans/projectplan.md)** - Overall project roadmap
- **[Trelliscope Analysis](../.claude_research/TRELLISCOPE_TECHNICAL_ANALYSIS.md)** - Architecture deep dive

---

## 💡 Tips

1. **Start Simple**: Begin with a small DataFrame (10-20 rows) to test your setup
2. **Check Console**: Browser console (F12) shows helpful error messages
3. **Incremental Development**: Test viewer after each major change
4. **Use Examples**: Adapt the examples above to your use case
5. **Read Errors**: Error messages usually indicate exactly what's wrong

---

## ✅ Verification Checklist

Before opening the viewer:

- [ ] Display written successfully (no errors during `display.write()`)
- [ ] index.html generated in output directory
- [ ] displayInfo.json exists in display subdirectory
- [ ] metadata.csv includes panel column
- [ ] panels/ directory contains PNG/HTML files
- [ ] Local server running from correct directory
- [ ] Opening http://localhost URL (not file://)

---

**Need Help?** Check the [Troubleshooting](#-troubleshooting) section or review the [Complete Fix Summary](./VIEWER_FIX_SUMMARY.md) for technical details.
