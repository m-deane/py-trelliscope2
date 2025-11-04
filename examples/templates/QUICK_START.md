# Quick Start: Static Trelliscope Displays

Create your first trelliscope display in 5 minutes.

## 1. Copy the Template

```bash
cd examples
cp templates/static_display_template.py my_first_display.py
```

## 2. Minimal Customization

Edit `my_first_display.py` and change just 3 things:

```python
# Line 20-22: Update display name
DISPLAY_NAME = "my_first_display"
DISPLAY_DESCRIPTION = "My first trelliscope visualization"

# Line 43-54: Replace with your data
def generate_data() -> pd.DataFrame:
    return pd.DataFrame({
        'id': range(10),
        'value': [10, 25, 15, 30, 20, 18, 22, 28, 12, 16],
        'category': ['A', 'B', 'C', 'D', 'E', 'A', 'B', 'C', 'D', 'E'],
    })

# Line 76-91: Customize your visualization
def create_panel(row: pd.Series, panel_dir: Path, panel_id: int) -> str:
    fig, ax = plt.subplots(figsize=(5, 5))
    ax.bar([row['category']], [row['value']], color='steelblue')
    # ... your plotting code here
```

## 3. Run It

```bash
python my_first_display.py
```

Output:
```
======================================================================
Creating Static Trelliscope Display: my_first_display
======================================================================

Step 1: Loading data...
✓ Loaded 10 rows with 3 columns

Step 2: Setting up output directory...
  Output path: /path/to/output/my_first_display

Step 3: Generating panels...
Generating 10 panels...
  Generated 10/10 panels
✓ Generated all 10 panels

Step 4: Creating display configuration...
✓ Display configuration created

Step 5: Writing display files...
✓ Display files written to: /path/to/output/my_first_display

Step 6: Creating viewer HTML...
✓ Viewer HTML created: /path/to/output/my_first_display_viewer.html

======================================================================
✓ Display creation complete!
======================================================================
```

## 4. View It

```bash
cd output
python3 -m http.server 8000
```

Open browser: http://localhost:8000/my_first_display_viewer.html

## 5. What You'll See

- Grid of panels (3 columns by default)
- Category and value labels on each panel
- Sidebar with:
  - Filter controls
  - Sort controls
  - Layout controls
- Interactive filtering/sorting capabilities

## Next Steps

### Add More Cognostics

```python
data = pd.DataFrame({
    'id': range(10),
    'value': [10, 25, 15, 30, 20, 18, 22, 28, 12, 16],
    'category': ['A', 'B', 'C', 'D', 'E', 'A', 'B', 'C', 'D', 'E'],
    'region': ['North', 'South', 'East', 'West', 'North', 'South', 'East', 'West', 'North', 'South'],
    'date': pd.date_range('2024-01-01', periods=10),
    'score': [0.85, 0.92, 0.78, 0.95, 0.88, 0.91, 0.79, 0.93, 0.81, 0.87],
})
```

Now you can filter by region, date range, or score threshold!

### Customize Panel Visualization

```python
def create_panel(row: pd.Series, panel_dir: Path, panel_id: int) -> str:
    fig, ax = plt.subplots(figsize=(6, 4))

    # More complex visualization
    ax.bar([row['category']], [row['value']], color='steelblue', alpha=0.7)
    ax.axhline(y=row['value'], color='red', linestyle='--', alpha=0.5)
    ax.text(0, row['value'], f"{row['score']:.2f}", ha='center', va='bottom')

    ax.set_ylabel('Value', fontsize=12)
    ax.set_title(f"{row['region']} - {row['category']}", fontsize=14, fontweight='bold')
    ax.set_ylim(0, 40)
    ax.grid(True, alpha=0.3)

    plt.tight_layout()

    panel_filename = f"panel_{panel_id}.png"
    fig.savefig(panel_dir / panel_filename, dpi=120, bbox_inches='tight')
    plt.close(fig)

    return panel_filename
```

### Add Default Filters and Sorts

```python
display = (Display(data, name="my_first_display", description="My analysis")
    .set_panel_column("panel")
    .infer_metas()
    .set_default_layout(ncol=4)
    .set_default_labels(["category", "region", "score"])
    .set_default_sort([("score", "desc")])  # Sort by score descending
    .set_default_filter(varname="region", values=["North", "South"])  # Filter to North/South
)
```

### Use Different Visualization Libraries

**Plotly:**
```python
import plotly.graph_objects as go

def create_panel(row: pd.Series, panel_dir: Path, panel_id: int) -> str:
    fig = go.Figure()
    fig.add_trace(go.Bar(x=[row['category']], y=[row['value']]))
    fig.update_layout(title=f"{row['category']}: {row['value']}")

    panel_filename = f"panel_{panel_id}.png"
    fig.write_image(panel_dir / panel_filename)
    return panel_filename
```

**Seaborn:**
```python
import seaborn as sns

def create_panel(row: pd.Series, panel_dir: Path, panel_id: int) -> str:
    fig, ax = plt.subplots(figsize=(5, 5))

    sns.barplot(x=[row['category']], y=[row['value']], ax=ax, palette='viridis')
    ax.set_title(f"{row['category']}: {row['value']}")

    panel_filename = f"panel_{panel_id}.png"
    fig.savefig(panel_dir / panel_filename, dpi=100)
    plt.close(fig)
    return panel_filename
```

## Common Patterns

### Time Series Panels

```python
data = pd.DataFrame({
    'ticker': ['AAPL', 'GOOGL', 'MSFT', 'AMZN'],
    'data': [stock_data_aapl, stock_data_googl, stock_data_msft, stock_data_amzn],
    'return_pct': [15.2, 22.1, 18.5, 12.8],
    'volatility': [0.25, 0.30, 0.22, 0.28],
})

def create_panel(row, panel_dir, panel_id):
    fig, ax = plt.subplots(figsize=(6, 4))
    ax.plot(row['data']['date'], row['data']['price'])
    ax.set_title(f"{row['ticker']} - Return: {row['return_pct']}%")
    ax.set_xlabel('Date')
    ax.set_ylabel('Price')

    panel_filename = f"panel_{panel_id}.png"
    fig.savefig(panel_dir / panel_filename)
    plt.close(fig)
    return panel_filename
```

### Scatter Plots

```python
def create_panel(row, panel_dir, panel_id):
    fig, ax = plt.subplots(figsize=(5, 5))
    ax.scatter(row['x_data'], row['y_data'], alpha=0.6, s=50)
    ax.set_title(f"{row['group']} - R²: {row['r_squared']:.3f}")
    ax.set_xlabel('X Variable')
    ax.set_ylabel('Y Variable')

    # Add regression line
    z = np.polyfit(row['x_data'], row['y_data'], 1)
    p = np.poly1d(z)
    ax.plot(row['x_data'], p(row['x_data']), "r--", alpha=0.8)

    panel_filename = f"panel_{panel_id}.png"
    fig.savefig(panel_dir / panel_filename, dpi=100)
    plt.close(fig)
    return panel_filename
```

### Heatmaps

```python
def create_panel(row, panel_dir, panel_id):
    fig, ax = plt.subplots(figsize=(6, 5))

    sns.heatmap(row['matrix'], annot=True, fmt='.2f', cmap='coolwarm', ax=ax)
    ax.set_title(f"{row['category']} Correlation Matrix")

    panel_filename = f"panel_{panel_id}.png"
    fig.savefig(panel_dir / panel_filename, dpi=120)
    plt.close(fig)
    return panel_filename
```

## Tips for Success

1. **Start small**: Test with 5-10 panels first before generating thousands
2. **Use meaningful cognostics**: Include metadata that helps you explore the data
3. **Choose appropriate layout**: 3-4 columns works well for most displays
4. **Label wisely**: Show 2-3 most important variables as panel labels
5. **Test interactivity**: Try filtering and sorting to ensure cognostics work as expected

## Where to Go Next

- Read [Approach 2 Implementation Guide](../output/APPROACH_2_IMPLEMENTATION.md) for detailed documentation
- Check [Templates README](README.md) for customization guide
- Explore [examples/](../) directory for more complex examples
- See main [py-trelliscope documentation](../../docs/) for API reference
