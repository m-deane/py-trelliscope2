# Trelliscope Demo Notebooks

Comprehensive Jupyter notebooks demonstrating all features of the py-trelliscope2 interactive Dash viewer.

## Overview

These notebooks showcase **production-ready workflows** combining Plotly interactivity, matplotlib quality, keyboard shortcuts, state management, and data export capabilities.

### What's Included

| Notebook | Features | Panels | Port | Duration |
|----------|----------|--------|------|----------|
| **01_plotly_interactive_charts** | Plotly chart types, native rendering, responsive design | 80 | 8054 | 10 min |
| **02_mixed_panel_types** | Plotly + Matplotlib mixed, automatic detection | 72 | 8055 | 15 min |
| **03_keyboard_shortcuts_navigation** | Full keyboard workflow, power user features | 100 | 8056 | 10 min |
| **04_views_export_workflows** | Views, CSV/JSON export, state management | 50 | 8057 | 15 min |
| **05_financial_portfolio_analysis** | Real-world use case, complete workflow | 120 | 8058 | 20 min |

**Total**: 5 notebooks, 422 interactive panels, 70 minutes of comprehensive tutorials

---

## Notebook Descriptions

### 1. Plotly Interactive Charts (`01_plotly_interactive_charts.ipynb`)

**What You'll Learn:**
- Create fully interactive Plotly visualizations
- Time series with dual y-axes
- Scatter plots with color gradients
- Grouped bar charts with error bands
- Statistical box plots

**Key Features:**
- ✅ Native `dcc.Graph` rendering (no iframes)
- ✅ Full interactivity: hover, zoom, pan
- ✅ Responsive design - charts resize with layout
- ✅ Plotly modebar integration
- ✅ Custom hover templates

**Use Case**: Refinery capacity analysis across countries with 4 different chart types (80 panels total)

**Time**: ~10 minutes

---

### 2. Mixed Panel Types (`02_mixed_panel_types.ipynb`)

**What You'll Learn:**
- Combine Plotly and matplotlib in one display
- Automatic panel type detection
- When to use each library
- Unified browsing experience

**Visualization Types:**
- **Matplotlib**: Statistical diagnostics (Q-Q plots, autocorrelation, histograms)
- **Matplotlib**: Correlation heatmaps with seaborn
- **Plotly**: Interactive time series with subplots

**Key Features:**
- ✅ PNG (static) + HTML (interactive) in same display
- ✅ Viewer automatically detects format
- ✅ Seamless navigation across types
- ✅ Best of both libraries

**Use Case**: Statistical analysis workflow with 4-panel diagnostics + interactive exploration

**Time**: ~15 minutes

---

### 3. Keyboard Shortcuts & Navigation (`03_keyboard_shortcuts_navigation.ipynb`)

**What You'll Learn:**
- Master all keyboard shortcuts
- Navigate 100-panel display without mouse
- Power user workflows
- Performance benefits of keyboard navigation

**Keyboard Shortcuts Covered:**
- `←` / `→` - Page navigation
- `Home` / `End` - Jump to first/last page
- `/` - Quick search
- `Esc` - Clear search
- `+` / `-` - Adjust grid size
- `Ctrl+S` - Save views
- `Ctrl+R` - Reset filters
- `?` - Help modal

**Key Features:**
- ✅ Step-by-step keyboard tutorial
- ✅ 100 panels across ~17 pages for practice
- ✅ Performance comparison: keyboard vs mouse
- ✅ Muscle memory training

**Use Case**: Time series portfolio with focus on rapid navigation and filtering

**Time**: ~10 minutes (but master it for life!)

---

### 4. Views & Export Workflows (`04_views_export_workflows.ipynb`)

**What You'll Learn:**
- Create and manage named views
- Export filtered data to CSV
- Export view configurations as JSON
- Share analysis configurations with team
- Build repeatable analysis workflows

**Workflows Demonstrated:**
1. **Create Custom Views** - Save filter/sort combinations
2. **Navigate Between Views** - One-click context switching
3. **Export Filtered Data** - CSV for further analysis
4. **Export Configurations** - Share setups with colleagues
5. **Iterative Analysis Pattern** - Complete investigation workflow

**Export Formats:**
- **CSV**: Filtered data with all metadata
- **View JSON**: Filter/sort/label configuration
- **Config JSON**: Display structure and metadata

**Key Features:**
- ✅ Pre-configured views for common scenarios
- ✅ `Ctrl+S` quick save
- ✅ View restoration across sessions
- ✅ Export for reports and presentations

**Use Case**: Product sales analysis with 50 products across categories and regions

**Time**: ~15 minutes

---

### 5. Financial Portfolio Analysis (`05_financial_portfolio_analysis.ipynb`)

**What You'll Learn:**
- Complete real-world workflow
- Portfolio management dashboard
- Risk-return analysis
- Interactive candlestick charts
- Statistical diagnostics
- Client reporting workflows

**Features Integration:**
- ✅ Plotly candlesticks with OHLCV data
- ✅ Matplotlib returns analysis (4-panel diagnostics)
- ✅ Mixed interactive + static panels
- ✅ Advanced filtering (asset class, region, risk profile)
- ✅ Multiple saved views for different analyses
- ✅ CSV export for client reports
- ✅ Keyboard navigation for rapid review

**Generated Data:**
- 60 assets across 5 asset classes
- 252 days of OHLCV price history
- Realistic metrics: Sharpe ratio, max drawdown, volatility
- Performance tiers: Star, Good, Neutral, Underperformer

**Workflows:**
1. **Morning Portfolio Check** (5 min)
2. **Client Reporting** (10 min)
3. **Deep Dive Analysis** (15 min)

**Key Features:**
- ✅ 120 panels (60 candlestick + 60 statistical)
- ✅ Complete portfolio command center
- ✅ Pre-configured views for common tasks
- ✅ Export-ready for presentations
- ✅ Interactive drill-down capabilities

**Use Case**: Portfolio manager dashboard with comprehensive analysis tools

**Time**: ~20 minutes

---

## Getting Started

### Prerequisites

```bash
# Required packages
pip install pandas numpy matplotlib plotly scipy seaborn

# Trelliscope (if not already installed)
pip install -e /path/to/py-trelliscope2
```

### Running the Notebooks

1. **Navigate to demo directory:**
   ```bash
   cd examples/demo_notebooks
   ```

2. **Start Jupyter:**
   ```bash
   jupyter notebook
   ```

3. **Open any notebook** and run all cells (Cell → Run All)

4. **Viewer launches automatically** at specified port (e.g., http://localhost:8054)

5. **Press `Ctrl+C` in terminal** to stop the viewer when done

### Recommended Order

**For Beginners:**
1. Start with `01_plotly_interactive_charts.ipynb` - Learn Plotly basics
2. Then `02_mixed_panel_types.ipynb` - See mixed formats
3. Practice `03_keyboard_shortcuts_navigation.ipynb` - Build muscle memory
4. Master `04_views_export_workflows.ipynb` - State management
5. Apply everything in `05_financial_portfolio_analysis.ipynb`

**For Power Users:**
- Jump straight to `05_financial_portfolio_analysis.ipynb` for complete workflow
- Reference `03_keyboard_shortcuts_navigation.ipynb` for shortcut cheatsheet

---

## Feature Coverage Matrix

| Feature | NB 01 | NB 02 | NB 03 | NB 04 | NB 05 |
|---------|-------|-------|-------|-------|-------|
| **Plotly Interactive** | ✅ PRIMARY | ✅ | - | - | ✅ |
| **Matplotlib Static** | - | ✅ PRIMARY | - | - | ✅ |
| **Mixed Panel Types** | - | ✅ PRIMARY | - | - | ✅ |
| **Keyboard Shortcuts** | ✅ | ✅ | ✅ PRIMARY | ✅ | ✅ |
| **Views (Save/Load)** | ✅ | ✅ | ✅ | ✅ PRIMARY | ✅ |
| **CSV Export** | ✅ | ✅ | ✅ | ✅ PRIMARY | ✅ |
| **JSON Export** | - | - | - | ✅ PRIMARY | ✅ |
| **Advanced Filtering** | ✅ | ✅ | ✅ | ✅ | ✅ PRIMARY |
| **Panel Details Modal** | ✅ | ✅ | ✅ | ✅ | ✅ |
| **Global Search** | ✅ | ✅ | ✅ PRIMARY | ✅ | ✅ |
| **Layout Controls** | ✅ | ✅ | ✅ PRIMARY | ✅ | ✅ |
| **Responsive Design** | ✅ PRIMARY | ✅ | ✅ | ✅ | ✅ |

**PRIMARY** = Main focus of notebook

---

## Common Workflows

### Quick Visualization Check
```python
# Create display, launch viewer
from trelliscope import Display
from trelliscope.dash_viewer import create_dash_app

display = Display(df, name="my_analysis").set_panel_column("plot").infer_metas()
app = create_dash_app(display)
app.run(debug=False, port=8060)
```

### Plotly Interactive Panel
```python
import plotly.graph_objects as go

fig = go.Figure()
fig.add_trace(go.Scatter(x=[1,2,3], y=[4,5,6], mode='lines+markers'))
fig.update_layout(autosize=True)  # Responsive

# Add to DataFrame, set as panel column
df['panel'] = fig
```

### Matplotlib Static Panel
```python
import matplotlib.pyplot as plt

fig, ax = plt.subplots(figsize=(8, 6))
ax.plot([1, 2, 3], [4, 5, 6])
ax.set_title('My Plot')

# Add to DataFrame, set as panel column
df['panel'] = fig
plt.close(fig)
```

### Save and Load Views
```python
# In viewer UI:
# 1. Apply filters/sorts
# 2. Click "Save View" button
# 3. Enter name: "My Analysis"
# 4. Load later from Views dropdown

# Or use keyboard:
# Ctrl+S → Enter name → Save
```

### Export Filtered Data
```python
# In viewer UI:
# 1. Apply desired filters
# 2. Scroll to "Export" section
# 3. Click "Export Data (CSV)"
# 4. Downloads: filtered_data.csv
```

---

## Troubleshooting

### Port Already in Use
```bash
# If port 8054 is busy, notebooks use different ports:
# NB 01: 8054
# NB 02: 8055
# NB 03: 8056
# NB 04: 8057
# NB 05: 8058

# Or change port in notebook:
app.run(debug=False, port=8060)  # Use any free port
```

### Viewer Not Loading
```python
# Check terminal for errors
# Common fixes:
# 1. Ensure all dependencies installed
# 2. Try different port
# 3. Clear browser cache
# 4. Restart Jupyter kernel
```

### ModuleNotFoundError
```bash
# Install missing packages:
pip install pandas numpy matplotlib plotly scipy seaborn dash dash-bootstrap-components

# Install trelliscope:
cd /path/to/py-trelliscope2
pip install -e .
```

### Plots Not Appearing
```python
# Ensure panel column set correctly:
display.set_panel_column("panel")

# Verify figures exist in DataFrame:
print(df['panel'].head())
```

---

## Data Sources

All notebooks use either:
- **Real data**: `examples/_data/refinery_margins.csv` (refinery capacity data)
- **Synthetic data**: Realistically generated with proper statistical properties

No external API calls or downloads required - everything works offline!

---

## Performance Notes

| Notebook | Panels | Generation Time | Viewer Load Time |
|----------|--------|-----------------|------------------|
| NB 01 | 80 | ~15s | <2s |
| NB 02 | 72 | ~25s | <2s |
| NB 03 | 100 | ~20s | <2s |
| NB 04 | 50 | ~10s | <1s |
| NB 05 | 120 | ~40s | <3s |

**Note**: Times approximate, vary by system. Plotly extraction may add 1-2s per page load.

---

## Next Steps

### After Completing Notebooks

1. **Apply to your data**:
   ```python
   # Replace synthetic data with your DataFrame
   my_df = pd.read_csv("my_data.csv")
   my_df['panel'] = my_df.apply(create_my_plot, axis=1)
   ```

2. **Customize visualizations**:
   - Modify chart functions to match your domain
   - Add domain-specific metrics
   - Create custom color schemes

3. **Build production dashboards**:
   - Deploy with Dash app server
   - Add authentication
   - Schedule automated updates

4. **Share with team**:
   - Export view configurations
   - Document common workflows
   - Create team-specific views

### Additional Resources

- **Phase 4 Showcase**: `examples/phase4_showcase/` - Production examples
- **API Documentation**: `docs/` - Complete API reference
- **Test Suite**: `tests/` - Example test patterns
- **Project README**: Root `README.md` - Project overview

---

## Contributing

Found a bug or have a feature idea for these demos?

1. Check existing issues: https://github.com/your-org/py-trelliscope2/issues
2. Create detailed bug report or feature request
3. Include notebook name and cell number if applicable

---

## License

Same license as py-trelliscope2 project.

---

## Summary

These 5 notebooks provide **70 minutes of comprehensive training** covering:

- ✅ 422 interactive panels across diverse use cases
- ✅ Plotly + Matplotlib integration
- ✅ Complete keyboard-driven workflows
- ✅ State management and export capabilities
- ✅ Real-world financial analysis example

**Start with notebook 01 and progress through 05 to master py-trelliscope2!**
