# Plotly Dash Interactive Viewer Development Specification

## Project Goal

Create an **interactive Plotly Dash application** that replicates the functionality and user interface of the existing trelliscopejs-lib HTML viewer, but runs as a native Python application that can be launched directly from Jupyter notebooks.

## Context

### Current Implementation
- **Static HTML Viewer**: Uses trelliscopejs-lib v0.7.16 (React/Redux) loaded from CDN
- **Data Format**: JSON-based (displayInfo.json, metaData.json, metaData.js)
- **Panel Types**: PNG images (matplotlib) and interactive HTML iframes (Plotly)
- **Deployment**: Requires HTTP server (python -m http.server)
- **Launch**: Opens in external browser via webbrowser.open()

### Target Implementation
- **Interactive Python App**: Plotly Dash application running in Python
- **Data Format**: Same JSON format for compatibility
- **Panel Types**: Native Plotly figures (no iframes needed), matplotlib images
- **Deployment**: Runs as Dash server directly from Python
- **Launch**: Embeddable in Jupyter notebooks via IFrame or opens in browser

## Core Requirements

### 1. Exact UI/UX Parity

The Dash viewer must replicate ALL functionality from trelliscopejs-lib:

#### Layout Controls
- **Grid Layout**: Dynamic ncol × nrow grid with configurable columns/rows
- **Page Size**: Adjustable panels per page (12, 24, 48, etc.)
- **Arrangement**: Row-wise or column-wise panel ordering
- **Responsive Resizing**: Panels resize when layout changes
- **Pagination**: Previous/Next page navigation with page number display

#### Filter System
- **Per-Variable Filters**: Each meta variable gets appropriate filter widget:
  - **Factor**: Multi-select dropdown with level counts
  - **Number**: Range slider with min/max
  - **Currency**: Range slider with currency formatting
  - **Date**: Date range picker
  - **Time**: DateTime range picker
  - **String**: Text search with contains/equals/regex
- **Active Filter Display**: Show which filters are active
- **Clear All**: Reset all filters at once
- **Filter Counts**: Show "N of M panels" matching current filters

#### Sort System
- **Multi-Column Sort**: Sort by multiple variables with priority
- **Sort Direction**: Ascending/descending for each sort key
- **Drag to Reorder**: Change sort priority by dragging
- **Visual Indicators**: Show active sorts with arrows (↑↓)

#### Label System
- **Panel Labels**: Display metadata beneath each panel
- **Customizable Labels**: Choose which variables to display
- **Label Ordering**: Drag to reorder label variables
- **Formatting**: Respect meta variable formatting (digits, locale, etc.)

#### Panel Display
- **Image Panels**: Display PNG/JPEG from matplotlib with proper sizing
- **Plotly Panels**: Render Plotly figures natively (no iframes!)
- **Lazy Loading**: Only load visible panels (pagination)
- **Loading States**: Show skeleton/spinner while panels load
- **Panel Keys**: Maintain panelKey association for data integrity

#### Views System
- **Save Views**: Save current state (filters, sorts, layout, labels)
- **Load Views**: Restore saved configurations
- **Named Views**: User-provided names for each view
- **View Management**: List, rename, delete views
- **Default View**: Initial state when display loads

#### Search & Discovery
- **Global Search**: Search across all text fields
- **Quick Filters**: Predefined common filter combinations
- **Panel Info**: Click panel to see all metadata details
- **Download Panel**: Export individual panels

### 2. Architecture Design

#### Component Structure

```
trelliscope/
├── dash_viewer/
│   ├── __init__.py
│   ├── app.py                    # Main Dash app factory
│   ├── components/
│   │   ├── __init__.py
│   │   ├── layout.py             # Grid layout component
│   │   ├── filters.py            # Filter panel components
│   │   ├── sorts.py              # Sort panel components
│   │   ├── labels.py             # Label panel components
│   │   ├── controls.py           # Pagination, layout controls
│   │   ├── panels.py             # Panel rendering (image/plotly)
│   │   └── header.py             # Display header/title
│   ├── callbacks/
│   │   ├── __init__.py
│   │   ├── filter_callbacks.py   # Filter interaction logic
│   │   ├── sort_callbacks.py     # Sort interaction logic
│   │   ├── layout_callbacks.py   # Layout change logic
│   │   ├── pagination_callbacks.py # Page navigation
│   │   └── view_callbacks.py     # Save/load views
│   ├── state.py                  # State management (filters, sorts, etc.)
│   ├── loader.py                 # Load displayInfo.json, panels
│   └── utils.py                  # Helper functions
├── display.py                    # Add .show_interactive() method
└── jupyter_integration.py        # Jupyter notebook helpers
```

#### Data Flow

```
displayInfo.json → loader.py → state.py → components/ → callbacks/ → UI updates
     ↓                                          ↓
Panel files/figures                      User interactions
     ↓                                          ↓
panels.py component                   State changes → Re-render
```

### 3. Technical Specifications

#### Dependencies

```python
# Core
plotly>=6.0.0
dash>=2.18.0
dash-bootstrap-components>=1.6.0
pandas>=2.0.0

# Optional
jupyter-dash>=0.4.2  # For Jupyter integration
```

#### Key Classes

**DashViewer** (Main application class)
```python
class DashViewer:
    """Interactive Plotly Dash viewer for Trelliscope displays."""

    def __init__(self, display_path: Path, mode: str = "external"):
        """
        Parameters
        ----------
        display_path : Path
            Path to display output directory (contains displayInfo.json)
        mode : str
            "external" - Launch in browser
            "inline" - Embed in Jupyter notebook
            "jupyterlab" - JupyterLab mode
        """

    def load_display(self) -> dict:
        """Load displayInfo.json and associated files."""

    def create_app(self) -> dash.Dash:
        """Create and configure Dash application."""

    def run(self, port: int = 8050, debug: bool = False):
        """Start Dash server."""

    def show(self):
        """Show in appropriate mode (browser/notebook)."""
```

**DisplayState** (State management)
```python
@dataclass
class DisplayState:
    """Manages current display state (filters, sorts, layout, etc.)."""

    display_info: dict
    active_filters: Dict[str, Any]
    active_sorts: List[Tuple[str, str]]  # [(varname, direction), ...]
    current_page: int
    ncol: int
    nrow: int
    arrangement: str
    active_labels: List[str]

    def filter_data(self) -> pd.DataFrame:
        """Apply current filters to cogData."""

    def sort_data(self, data: pd.DataFrame) -> pd.DataFrame:
        """Apply current sorts to filtered data."""

    def get_page_data(self, data: pd.DataFrame) -> pd.DataFrame:
        """Get current page of panels."""

    def save_view(self, name: str) -> dict:
        """Save current state as named view."""

    def load_view(self, view: dict):
        """Restore state from saved view."""
```

**PanelRenderer** (Panel display logic)
```python
class PanelRenderer:
    """Handles rendering of different panel types."""

    @staticmethod
    def render_image_panel(panel_path: Path, width: int, height: int) -> html.Img:
        """Render PNG/JPEG image panel."""

    @staticmethod
    def render_plotly_panel(panel_path: Path, width: int, height: int) -> dcc.Graph:
        """Load and render Plotly HTML as native Plotly figure."""

    @staticmethod
    def extract_plotly_figure(html_path: Path) -> go.Figure:
        """Extract Plotly figure JSON from HTML file."""
```

#### Filter Components by Meta Type

**FactorFilter**
```python
def create_factor_filter(meta: dict, data: pd.Series) -> dcc.Dropdown:
    """Multi-select dropdown with level counts."""
    options = [
        {"label": f"{level} ({count})", "value": level}
        for level, count in data.value_counts().items()
    ]
    return dcc.Dropdown(
        id={"type": "filter", "varname": meta["varname"]},
        options=options,
        multi=True,
        placeholder=f"Filter {meta['label']}..."
    )
```

**NumberFilter**
```python
def create_number_filter(meta: dict, data: pd.Series) -> dcc.RangeSlider:
    """Range slider for numeric filtering."""
    return dcc.RangeSlider(
        id={"type": "filter", "varname": meta["varname"]},
        min=data.min(),
        max=data.max(),
        value=[data.min(), data.max()],
        marks={
            data.min(): f"{data.min():.{meta.get('digits', 1)}f}",
            data.max(): f"{data.max():.{meta.get('digits', 1)}f}",
        },
        tooltip={"placement": "bottom", "always_visible": True}
    )
```

**DateFilter**
```python
def create_date_filter(meta: dict, data: pd.Series) -> dcc.DatePickerRange:
    """Date range picker for date filtering."""
    return dcc.DatePickerRange(
        id={"type": "filter", "varname": meta["varname"]},
        start_date=data.min(),
        end_date=data.max(),
        display_format="YYYY-MM-DD"
    )
```

#### Layout Grid Component

```python
def create_panel_grid(
    panels: List[dict],
    ncol: int,
    nrow: int,
    panel_width: int,
    panel_height: int,
    labels: List[str],
    renderer: PanelRenderer
) -> html.Div:
    """
    Create responsive grid of panels.

    Uses CSS Grid for layout with proper sizing.
    Each panel shows figure + labels underneath.
    """
    grid_items = []

    for panel_data in panels:
        # Render panel based on type
        if panel_data["paneltype"] == "img":
            panel = renderer.render_image_panel(
                panel_data["panel_path"],
                panel_width,
                panel_height
            )
        else:  # iframe/plotly
            panel = renderer.render_plotly_panel(
                panel_data["panel_path"],
                panel_width,
                panel_height
            )

        # Create labels
        label_divs = [
            html.Div(
                f"{meta['label']}: {panel_data[varname]}",
                className="panel-label"
            )
            for varname in labels
            if varname in panel_data
        ]

        # Combine panel + labels
        grid_items.append(
            html.Div([
                panel,
                html.Div(label_divs, className="panel-labels")
            ], className="panel-container")
        )

    return html.Div(
        grid_items,
        style={
            "display": "grid",
            "gridTemplateColumns": f"repeat({ncol}, 1fr)",
            "gap": "20px",
            "padding": "20px"
        }
    )
```

### 4. Critical Implementation Details

#### Plotly HTML Panel Extraction

The existing viewer uses iframes for Plotly panels. The Dash viewer should extract the Plotly figure and render natively:

```python
def extract_plotly_figure_from_html(html_path: Path) -> go.Figure:
    """
    Extract Plotly figure from HTML file.

    Plotly HTML contains JSON config embedded as:
    Plotly.newPlot('div-id', [data], layout, config)

    Parse HTML to extract this JSON and reconstruct Figure.
    """
    with open(html_path, 'r') as f:
        html_content = f.read()

    # Extract JSON from Plotly.newPlot() call
    import re
    pattern = r'Plotly\.newPlot\([^,]+,\s*(\[.+?\]),\s*(\{.+?\}),\s*(\{.+?\})\)'
    match = re.search(pattern, html_content, re.DOTALL)

    if match:
        data_json = match.group(1)
        layout_json = match.group(2)

        import json
        data = json.loads(data_json)
        layout = json.loads(layout_json)

        return go.Figure(data=data, layout=layout)

    # Fallback: Parse as full HTML div
    import plotly.io as pio
    return pio.from_html(html_content)
```

#### State Persistence

Views must be saveable and loadable:

```python
def save_view_to_config(display_path: Path, view_name: str, state: DisplayState):
    """Save view to displayInfo.json."""
    config_path = display_path / "displays" / display_name / "displayInfo.json"

    with open(config_path, 'r') as f:
        display_info = json.load(f)

    # Add view to views array
    view = {
        "name": view_name,
        "state": state.to_dict()
    }

    if "views" not in display_info:
        display_info["views"] = []

    display_info["views"].append(view)

    with open(config_path, 'w') as f:
        json.dump(display_info, f, indent=2)
```

#### Responsive Panel Sizing

Panels must resize based on grid layout:

```python
def calculate_panel_dimensions(
    ncol: int,
    nrow: int,
    viewport_width: int = 1920,
    aspect_ratio: float = 1.0,
    padding: int = 20
) -> Tuple[int, int]:
    """
    Calculate panel width/height based on grid layout.

    Ensures panels fit viewport while maintaining aspect ratio.
    """
    grid_width = viewport_width - (padding * (ncol + 1))
    panel_width = grid_width // ncol
    panel_height = int(panel_width / aspect_ratio)

    return panel_width, panel_height
```

### 5. Integration with Display Class

Add new method to `Display` class:

```python
# In trelliscope/display.py

def show_interactive(
    self,
    mode: str = "external",
    port: int = 8050,
    debug: bool = False,
    **kwargs
) -> Optional[DashViewer]:
    """
    Launch interactive Plotly Dash viewer.

    Parameters
    ----------
    mode : str
        "external" - Open in browser (default)
        "inline" - Embed in Jupyter notebook
        "jupyterlab" - JupyterLab mode
    port : int
        Port for Dash server (default: 8050)
    debug : bool
        Enable Dash debug mode (default: False)
    **kwargs
        Additional arguments passed to DashViewer

    Returns
    -------
    DashViewer or None
        DashViewer instance if mode="external", None if mode="inline"

    Examples
    --------
    >>> display = Display(df, name="my_display")
    >>> display.write()
    >>> display.show_interactive()  # Opens in browser

    >>> # In Jupyter notebook
    >>> display.show_interactive(mode="inline")  # Embeds in notebook
    """
    from trelliscope.dash_viewer import DashViewer

    # Ensure display is written
    if not self._output_path.exists():
        raise RuntimeError("Display not written. Call .write() first.")

    viewer = DashViewer(
        display_path=self._output_path,
        mode=mode,
        **kwargs
    )

    viewer.run(port=port, debug=debug)

    return viewer if mode == "external" else None
```

### 6. Jupyter Notebook Integration

**Inline Mode** (using jupyter-dash):

```python
# In trelliscope/dash_viewer/app.py

class DashViewer:
    def run(self, port: int = 8050, debug: bool = False):
        """Run Dash app in appropriate mode."""
        if self.mode == "inline":
            from jupyter_dash import JupyterDash
            self.app = JupyterDash(__name__)
            self._setup_app()
            self.app.run_server(mode="inline", port=port, debug=debug)

        elif self.mode == "jupyterlab":
            from jupyter_dash import JupyterDash
            self.app = JupyterDash(__name__)
            self._setup_app()
            self.app.run_server(mode="jupyterlab", port=port, debug=debug)

        else:  # external
            self.app = dash.Dash(__name__)
            self._setup_app()

            import webbrowser
            import threading

            def open_browser():
                import time
                time.sleep(1.5)
                webbrowser.open(f"http://localhost:{port}")

            threading.Thread(target=open_browser, daemon=True).start()
            self.app.run_server(port=port, debug=debug)
```

### 7. Styling & Theming

Use Dash Bootstrap Components for consistent styling:

```python
# In trelliscope/dash_viewer/app.py

import dash_bootstrap_components as dbc

def create_app(self) -> dash.Dash:
    """Create Dash app with Bootstrap theme."""
    app = dash.Dash(
        __name__,
        external_stylesheets=[dbc.themes.BOOTSTRAP],
        suppress_callback_exceptions=True
    )

    return app
```

Custom CSS for trelliscope-specific styling:

```python
# In trelliscope/dash_viewer/assets/style.css

/* Panel grid */
.panel-container {
    border: 1px solid #e0e0e0;
    border-radius: 4px;
    overflow: hidden;
    background: white;
}

.panel-labels {
    padding: 10px;
    background: #f8f9fa;
    border-top: 1px solid #e0e0e0;
    font-size: 12px;
}

.panel-label {
    margin-bottom: 4px;
}

/* Filter panel */
.filter-panel {
    border-right: 1px solid #e0e0e0;
    padding: 20px;
    height: 100vh;
    overflow-y: auto;
}

/* Control bar */
.control-bar {
    border-bottom: 1px solid #e0e0e0;
    padding: 15px 20px;
    background: #f8f9fa;
}
```

### 8. Performance Optimizations

#### Lazy Loading Strategy

```python
# Only render visible panels (current page)
@app.callback(
    Output("panel-grid", "children"),
    Input("current-page", "data"),
    Input("panels-per-page", "value"),
    State("filtered-data", "data")
)
def update_visible_panels(current_page, per_page, filtered_data):
    """Render only current page of panels."""
    start_idx = (current_page - 1) * per_page
    end_idx = start_idx + per_page

    page_data = filtered_data[start_idx:end_idx]

    return create_panel_grid(
        panels=page_data,
        ncol=state.ncol,
        nrow=state.nrow,
        ...
    )
```

#### Caching

```python
from flask_caching import Cache

cache = Cache(app.server, config={
    'CACHE_TYPE': 'filesystem',
    'CACHE_DIR': 'cache-directory'
})

@cache.memoize(timeout=300)
def load_panel_figure(panel_path: str) -> go.Figure:
    """Load and cache Plotly figure from HTML."""
    return extract_plotly_figure_from_html(Path(panel_path))
```

### 9. Testing Strategy

#### Unit Tests

```python
# tests/dash_viewer/test_panel_renderer.py

def test_extract_plotly_figure():
    """Test extracting Plotly figure from HTML."""
    html_path = Path("test_data/panel_0.html")
    fig = PanelRenderer.extract_plotly_figure(html_path)

    assert isinstance(fig, go.Figure)
    assert len(fig.data) > 0

def test_render_image_panel():
    """Test rendering image panel."""
    panel = PanelRenderer.render_image_panel(
        Path("test_data/panel_0.png"),
        width=500,
        height=400
    )

    assert isinstance(panel, html.Img)
```

#### Integration Tests

```python
# tests/dash_viewer/test_app_integration.py

def test_filter_updates_panels():
    """Test that filter changes update displayed panels."""
    viewer = DashViewer(display_path)
    app = viewer.create_app()

    # Simulate filter change
    with app.test_client() as client:
        # Apply country filter
        response = client.post(
            "/_dash-update-component",
            json={"inputs": [{"id": "country-filter", "value": ["Germany"]}]}
        )

        # Check panels updated
        assert response.json()["response"]["panel-grid"]["children"]
```

### 10. Example Usage

#### From Python Script

```python
from pathlib import Path
from trelliscope import Display
import pandas as pd

# Create display
df = pd.DataFrame({...})
display = Display(df, name="my_display")
display.write()

# Launch interactive viewer
display.show_interactive()  # Opens in browser
```

#### From Jupyter Notebook

```python
# Cell 1: Create display
from trelliscope import Display
import pandas as pd

df = pd.DataFrame({...})
display = Display(df, name="my_display")
display.write()

# Cell 2: Show inline
display.show_interactive(mode="inline")  # Embedded in notebook
```

#### Standalone Dash App

```python
from pathlib import Path
from trelliscope.dash_viewer import DashViewer

# Create viewer
viewer = DashViewer(
    display_path=Path("output/my_display"),
    mode="external"
)

# Run on custom port
viewer.run(port=8888, debug=True)
```

### 11. Migration Path

To ensure smooth adoption:

1. **Keep HTML Viewer**: Don't remove existing HTML viewer
2. **Add New Method**: `show_interactive()` is new, `.write()` unchanged
3. **Same Data Format**: Use existing displayInfo.json
4. **Feature Parity**: Match all HTML viewer features before release
5. **Documentation**: Clear examples for both viewers

### 12. Success Criteria

✅ **Functional Requirements**
- [ ] All filter types working (factor, number, date, etc.)
- [ ] Multi-column sorting with drag-to-reorder
- [ ] Grid layout with dynamic ncol/nrow
- [ ] Pagination with proper page size
- [ ] Label display beneath panels
- [ ] Save/load views
- [ ] Search across metadata
- [ ] Panel detail view

✅ **Performance Requirements**
- [ ] <2s initial load for 100 panels
- [ ] <500ms filter/sort response
- [ ] Lazy loading for 1000+ panels
- [ ] Smooth grid resizing

✅ **Integration Requirements**
- [ ] Launches from Jupyter notebooks
- [ ] Works in JupyterLab
- [ ] Opens in external browser
- [ ] Uses existing displayInfo.json format

✅ **UX Requirements**
- [ ] Matches HTML viewer appearance
- [ ] Responsive design
- [ ] Keyboard shortcuts
- [ ] Mobile-friendly (optional)

### 13. Development Phases

**Phase 1: Core Infrastructure (Week 1)**
- [ ] DashViewer class structure
- [ ] DisplayState management
- [ ] Load displayInfo.json
- [ ] Basic panel grid layout
- [ ] Simple filter (factor only)

**Phase 2: Panel Rendering (Week 2)**
- [ ] PanelRenderer for images
- [ ] Extract Plotly figures from HTML
- [ ] Native Plotly rendering
- [ ] Panel labels
- [ ] Pagination

**Phase 3: Full Filters & Sorts (Week 3)**
- [ ] All filter types (number, date, etc.)
- [ ] Multi-column sorting
- [ ] Drag-to-reorder sorts
- [ ] Clear filters button
- [ ] Filter counts

**Phase 4: Advanced Features (Week 4)**
- [ ] Save/load views
- [ ] Layout controls (ncol/nrow)
- [ ] Panel detail modal
- [ ] Global search
- [ ] Download panel

**Phase 5: Integration & Polish (Week 5)**
- [ ] Jupyter notebook integration
- [ ] Add to Display class
- [ ] Performance optimization
- [ ] Caching
- [ ] Documentation

**Phase 6: Testing & Release (Week 6)**
- [ ] Unit tests
- [ ] Integration tests
- [ ] Example notebooks
- [ ] User documentation
- [ ] Release v1.0

### 14. Open Questions

1. **Plotly Figure Extraction**: Best method for parsing Plotly HTML files?
2. **State Persistence**: Store in displayInfo.json or separate file?
3. **Multi-Display**: Support switching between displays in same viewer?
4. **Theming**: Light/dark mode support?
5. **Export**: Allow exporting filtered dataset as CSV?

### 15. References

- **Current Viewer**: `examples/17_dual_display_demo.ipynb`
- **Display Class**: `trelliscope/display.py`
- **Viewer HTML**: `trelliscope/viewer_html.py`
- **Serialization**: `trelliscope/serialization.py`
- **Plotly Dash Docs**: https://dash.plotly.com/
- **Dash Bootstrap**: https://dash-bootstrap-components.opensource.faculty.ai/
- **Jupyter Dash**: https://github.com/plotly/jupyter-dash

---

## Implementation Prompt

Use this specification to build the Plotly Dash interactive viewer for py-trelliscope2. Start with Phase 1 (Core Infrastructure) and implement incrementally. Ensure each phase is fully tested before moving to the next. Maintain exact feature parity with the existing HTML viewer while leveraging Dash's native capabilities for improved performance and Jupyter integration.
