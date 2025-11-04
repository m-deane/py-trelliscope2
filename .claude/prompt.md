# py-trelliscope: Python Port of R Trelliscope Package

## Project Vision

Create a production-ready Python package that enables interactive exploration of large collections of plots (hundreds to millions) through a clean, pandas-integrated API that generates visualizations compatible with the existing trelliscopejs-lib viewer.

## ⚠️ CRITICAL ARCHITECTURAL DECISIONS

### 1. Hybrid Implementation Strategy - REUSE JS Viewer
**DO:**
- ✅ Build Python API to generate JSON specifications
- ✅ Reuse existing trelliscopejs-lib React/Redux viewer
- ✅ Focus implementation effort on Python backend and clean API
- ✅ Generate compatible displayInfo.json matching TypeScript interfaces

**DO NOT:**
- ❌ Reimplement React/Redux frontend from scratch
- ❌ Create custom JavaScript viewer
- ❌ Modify trelliscopejs-lib source (use as-is)

**Reason:** The existing viewer is sophisticated, well-tested, and works perfectly. The JSON specification format is language-agnostic by design. Building Python classes that output compatible JSON is far more efficient than reimplementing thousands of lines of React/Redux code.

### 2. Panel-Centric Data Model
**Strategy:**
- Each row in DataFrame represents one panel + its cognostics (metadata)
- Panel column contains plots (figures, file paths, lazy functions, or HTML)
- All other columns automatically become cognostics for filtering/sorting
- Meta variable types inferred from DataFrame dtypes with manual override

**Example:**
```python
import pandas as pd
from trelliscope import Display

# Create DataFrame where each row = one panel
df = pd.DataFrame({
    'plot': [fig1, fig2, fig3],           # Panel column (matplotlib figures)
    'country': ['USA', 'UK', 'France'],   # Factor cognostic
    'gdp': [21e12, 2.8e12, 2.7e12],      # Number cognostic
    'population': [331e6, 67e6, 65e6],   # Number cognostic
    'continent': ['NA', 'EU', 'EU'],     # Factor cognostic
})

# Create display - 'plot' column contains panels, others are cognostics
display = (
    Display(df, name="countries", description="Country statistics")
    .set_panel_column("plot")
    .set_default_layout(ncol=3)
    .write(path="./trelliscope_output")
)
```

### 3. Integration with Python Visualization Ecosystem
**Supported Libraries:**
- **matplotlib**: Primary integration, save figures to PNG/JPEG
- **plotly**: Export to HTML or static images
- **altair/vega**: Export to HTML with vega-embed
- **Custom**: Any callable returning image bytes or HTML string

**Integration Strategy:**
- Adapters for each library in `trelliscope.integrations`
- Automatic format detection from figure type
- Configurable export options (DPI, size, format)
- Lazy evaluation support for expensive plots

## Core Functionality Requirements

### Display Creation Workflow

**Basic Workflow:**
```python
from trelliscope import Display
import pandas as pd
import matplotlib.pyplot as plt

# 1. Prepare data with panel column
data = pd.DataFrame({
    'plot': plot_objects,      # Figures or file paths
    'category': categories,    # Cognostic 1
    'score': scores,          # Cognostic 2
})

# 2. Create and configure display
display = (
    Display(data, name="my_analysis")
    .set_panel_column("plot")
    .add_meta_variable("score", type="number", desc="Quality score")
    .set_default_layout(ncol=4, nrow=3)
    .set_default_labels(["category", "score"])
    .set_default_sort("score", dir="desc")
    .write(path="./output")
)

# 3. View in browser
display.view()  # Opens local server and launches browser
```

**Advanced Workflow with Lazy Evaluation:**
```python
def generate_plot(row):
    """Generate plot on-demand from row data"""
    fig, ax = plt.subplots()
    ax.plot(row['x_data'], row['y_data'])
    ax.set_title(f"{row['name']}")
    return fig

# Panel column contains lazy callables
data['plot'] = data.apply(lambda row: lambda: generate_plot(row), axis=1)

display = Display(data, name="lazy_plots").set_panel_column("plot")
display.write()  # Calls each function and generates panels
```

### Meta Variable System (Cognostics)

**9 Meta Variable Types:**

1. **factor** - Categorical with defined levels
   ```python
   .add_meta_variable("region", type="factor", levels=["North", "South", "East", "West"])
   ```

2. **number** - Numeric continuous
   ```python
   .add_meta_variable("price", type="number", digits=2, locale=True)
   ```

3. **currency** - Formatted monetary values
   ```python
   .add_meta_variable("revenue", type="currency", code="USD")
   ```

4. **date** - Date values (no time component)
   ```python
   .add_meta_variable("report_date", type="date")
   ```

5. **time** - Datetime with time component
   ```python
   .add_meta_variable("timestamp", type="time", timezone="UTC")
   ```

6. **href** - Hyperlinks with display labels
   ```python
   .add_meta_variable("link", type="href", label_col="link_text")
   ```

7. **graph** - Sparklines or micro-visualizations
   ```python
   .add_meta_variable("trend", type="graph", direction="up")
   ```

8. **panel_local** - Panel-specific URLs (relative paths)
   ```python
   # Auto-generated for local panel files
   ```

9. **panel_src** - Panel source paths
   ```python
   # Auto-generated when panels are files
   ```

**Type Inference:**
- `object` dtype → `factor` (if unique values < threshold) or text
- `int64`, `float64` → `number`
- `datetime64` → `time` (or `date` if no time component)
- `bool` → `factor` with levels [True, False]
- URL patterns → `href`
- File path patterns → `panel_src` or `panel_local`

### Display Configuration Options

**Layout Configuration:**
```python
display.set_default_layout(
    ncol=4,              # Number of columns
    nrow=3,              # Number of rows (optional)
    page=1,              # Starting page
    arrangement="row"    # "row" or "col"
)
```

**Panel Configuration:**
```python
display.set_panel_options(
    width=600,           # Panel width in pixels
    height=400,          # Panel height in pixels
    aspect=None,         # Aspect ratio (overrides height if set)
    force_size=True      # Force exact dimensions
)
```

**Filter Configuration:**
```python
# Add default filter
display.add_filter(
    varname="score",
    type="range",
    min_val=0.5,
    max_val=1.0
)

# Add categorical filter
display.add_filter(
    varname="category",
    type="category",
    values=["A", "B", "C"]
)
```

**Sort Configuration:**
```python
# Sort by single variable
display.set_default_sort("score", dir="desc")

# Sort by multiple variables
display.set_default_sorts([
    {"varname": "category", "dir": "asc"},
    {"varname": "score", "dir": "desc"}
])
```

**Label Configuration:**
```python
# Show meta variables as panel labels
display.set_default_labels(["category", "score"])

# Custom label template
display.set_label_template("{category}: {score:.2f}")
```

**Multiple Views:**
```python
# Define different view configurations
display.add_view(
    name="high_scores",
    filters=[{"varname": "score", "type": "range", "min": 0.8}],
    sorts=[{"varname": "score", "dir": "desc"}],
    labels=["category", "score"]
)

display.add_view(
    name="by_category",
    sorts=[{"varname": "category", "dir": "asc"}],
    labels=["category"]
)
```

## Core Python Package Structure

### Package Organization

```
trelliscope/
├── __init__.py                    # Public API exports
├── display.py                     # Display class (main interface)
├── meta.py                        # Meta variable classes
├── panels/
│   ├── __init__.py
│   ├── base.py                   # PanelSource abstract base
│   ├── file.py                   # FilePanelSource
│   ├── lazy.py                   # LazyPanelSource
│   ├── url.py                    # URLPanelSource
│   └── websocket.py              # WebSocketPanelSource
├── integrations/
│   ├── __init__.py
│   ├── matplotlib_adapter.py     # matplotlib figure handling
│   ├── plotly_adapter.py         # plotly figure handling
│   └── altair_adapter.py         # altair chart handling
├── writers/
│   ├── __init__.py
│   ├── json_writer.py            # JSON serialization
│   ├── file_writer.py            # File system operations
│   └── html_writer.py            # HTML index generation
├── utils/
│   ├── __init__.py
│   ├── validation.py             # Input validation
│   ├── inference.py              # Type inference
│   └── hash.py                   # Key signature generation
└── server/
    ├── __init__.py
    └── dev_server.py             # Local development server
```

### Core Classes

#### 1. Display Class

**Primary interface for creating trelliscope displays.**

```python
from typing import Optional, Union, List, Dict, Any, Callable
import pandas as pd
from pathlib import Path

class Display:
    """
    Interactive visualization display for exploring collections of plots.

    Each row in the input DataFrame represents one panel with associated
    metadata (cognostics) for filtering and sorting.

    Parameters
    ----------
    data : pd.DataFrame
        DataFrame where one column contains panels (plots/figures) and
        other columns contain cognostics (metadata).
    name : str
        Unique identifier for this display.
    description : str, optional
        Human-readable description.
    keysig : str, optional
        Unique key signature. Auto-generated from data if not provided.
    path : Path, optional
        Output directory path. Defaults to './trelliscope_output'.

    Examples
    --------
    >>> import pandas as pd
    >>> from trelliscope import Display
    >>>
    >>> df = pd.DataFrame({
    ...     'plot': [fig1, fig2, fig3],
    ...     'category': ['A', 'B', 'C'],
    ...     'value': [10, 20, 30]
    ... })
    >>>
    >>> display = Display(df, name="my_display")
    >>> display.set_panel_column("plot")
    >>> display.write()
    """

    def __init__(
        self,
        data: pd.DataFrame,
        name: str,
        description: str = "",
        keysig: Optional[str] = None,
        path: Optional[Union[str, Path]] = None
    ):
        pass

    def set_panel_column(self, column: str) -> "Display":
        """
        Specify which column contains panel data (plots/figures).

        Parameters
        ----------
        column : str
            Column name containing panels.

        Returns
        -------
        Display
            Self for method chaining.
        """
        pass

    def add_meta_variable(
        self,
        varname: str,
        type: Optional[str] = None,
        label: Optional[str] = None,
        desc: Optional[str] = None,
        **kwargs
    ) -> "Display":
        """
        Add or configure a meta variable (cognostic).

        Parameters
        ----------
        varname : str
            Column name in DataFrame.
        type : str, optional
            Meta type: factor, number, currency, date, time, href, graph.
            Auto-inferred if not specified.
        label : str, optional
            Display label. Defaults to varname.
        desc : str, optional
            Description for tooltip.
        **kwargs
            Type-specific parameters (digits, levels, code, etc.).

        Returns
        -------
        Display
            Self for method chaining.
        """
        pass

    def set_default_layout(
        self,
        ncol: int = 4,
        nrow: Optional[int] = None,
        page: int = 1,
        arrangement: str = "row"
    ) -> "Display":
        """Configure default grid layout."""
        pass

    def set_panel_options(
        self,
        width: Optional[int] = None,
        height: Optional[int] = None,
        aspect: Optional[float] = None,
        force_size: bool = False
    ) -> "Display":
        """Configure panel dimensions."""
        pass

    def add_filter(
        self,
        varname: str,
        type: str,
        **kwargs
    ) -> "Display":
        """Add a default filter."""
        pass

    def set_default_sort(
        self,
        varname: str,
        dir: str = "asc"
    ) -> "Display":
        """Set default sort order."""
        pass

    def set_default_labels(
        self,
        labels: List[str]
    ) -> "Display":
        """Set which meta variables to show as labels."""
        pass

    def add_view(
        self,
        name: str,
        filters: Optional[List[Dict]] = None,
        sorts: Optional[List[Dict]] = None,
        labels: Optional[List[str]] = None
    ) -> "Display":
        """Add a named view configuration."""
        pass

    def write(self, path: Optional[Union[str, Path]] = None) -> "Display":
        """
        Write display to disk (JSON spec + panels).

        This generates:
        - displayInfo.json with complete configuration
        - Panel files (PNG/JPEG/HTML) in panels/ directory
        - index.html with viewer

        Parameters
        ----------
        path : str or Path, optional
            Output directory. Uses instance path if not specified.

        Returns
        -------
        Display
            Self for further operations.
        """
        pass

    def view(self, port: int = 8000, open_browser: bool = True) -> None:
        """
        Launch local development server and open in browser.

        Parameters
        ----------
        port : int
            Server port. Default 8000.
        open_browser : bool
            Automatically open browser. Default True.
        """
        pass
```

#### 2. Meta Variable Classes

**Hierarchy for different meta variable types:**

```python
from typing import Optional, List, Any
from dataclasses import dataclass
import pandas as pd

@dataclass
class MetaVariable:
    """Base class for meta variables (cognostics)."""

    varname: str
    label: Optional[str] = None
    desc: Optional[str] = None

    def to_dict(self) -> dict:
        """Convert to JSON-serializable dictionary."""
        pass

    @classmethod
    def from_series(cls, series: pd.Series, **kwargs) -> "MetaVariable":
        """Infer meta variable from pandas Series."""
        pass


@dataclass
class FactorMeta(MetaVariable):
    """Categorical meta variable with levels."""

    type: str = "factor"
    levels: Optional[List[str]] = None

    def __post_init__(self):
        if self.levels is None:
            # Will be inferred from data
            pass


@dataclass
class NumberMeta(MetaVariable):
    """Numeric continuous meta variable."""

    type: str = "number"
    digits: int = 2
    locale: bool = False
    log: bool = False


@dataclass
class CurrencyMeta(MetaVariable):
    """Currency/monetary meta variable."""

    type: str = "currency"
    code: str = "USD"
    digits: int = 2
    locale: bool = True


@dataclass
class DateMeta(MetaVariable):
    """Date meta variable (no time component)."""

    type: str = "date"
    format: Optional[str] = None  # e.g., "%Y-%m-%d"


@dataclass
class TimeMeta(MetaVariable):
    """Datetime meta variable with time component."""

    type: str = "time"
    timezone: Optional[str] = None
    format: Optional[str] = None


@dataclass
class HrefMeta(MetaVariable):
    """Hyperlink meta variable."""

    type: str = "href"
    label_col: Optional[str] = None  # Column for link text


@dataclass
class GraphMeta(MetaVariable):
    """Sparkline/micro-visualization meta variable."""

    type: str = "graph"
    direction: Optional[str] = None  # "up", "down", "neutral"
    idvarname: Optional[str] = None


@dataclass
class PanelSrcMeta(MetaVariable):
    """Panel source path meta variable."""

    type: str = "panel_src"


@dataclass
class PanelLocalMeta(MetaVariable):
    """Panel local URL meta variable."""

    type: str = "panel_local"
```

#### 3. Panel Source Classes

**Abstract base and concrete implementations:**

```python
from abc import ABC, abstractmethod
from typing import Any, Optional, Callable
from pathlib import Path

class PanelSource(ABC):
    """Abstract base for panel sources."""

    @abstractmethod
    def generate_panels(self, output_dir: Path) -> List[str]:
        """
        Generate panel files and return list of filenames.

        Parameters
        ----------
        output_dir : Path
            Directory to write panel files.

        Returns
        -------
        List[str]
            List of generated filenames.
        """
        pass

    @abstractmethod
    def to_interface_dict(self) -> dict:
        """Convert to panelInterface JSON structure."""
        pass


class FilePanelSource(PanelSource):
    """Panels stored as pre-generated files."""

    def __init__(
        self,
        paths: List[Union[str, Path]],
        extension: str = "png"
    ):
        self.paths = [Path(p) for p in paths]
        self.extension = extension

    def generate_panels(self, output_dir: Path) -> List[str]:
        """Copy files to output directory."""
        pass

    def to_interface_dict(self) -> dict:
        return {"type": "file", "extension": self.extension}


class LazyPanelSource(PanelSource):
    """Panels generated on-demand from callables."""

    def __init__(
        self,
        generators: List[Callable],
        format: str = "png",
        **export_kwargs
    ):
        self.generators = generators
        self.format = format
        self.export_kwargs = export_kwargs

    def generate_panels(self, output_dir: Path) -> List[str]:
        """Call each generator and save result."""
        pass

    def to_interface_dict(self) -> dict:
        return {"type": "file", "extension": self.format}


class URLPanelSource(PanelSource):
    """Panels loaded from URLs."""

    def __init__(self, urls: List[str]):
        self.urls = urls

    def generate_panels(self, output_dir: Path) -> List[str]:
        """No generation needed - panels served from URLs."""
        return []

    def to_interface_dict(self) -> dict:
        return {"type": "url"}


class WebSocketPanelSource(PanelSource):
    """Panels streamed via WebSocket."""

    def __init__(self, endpoint: str):
        self.endpoint = endpoint

    def generate_panels(self, output_dir: Path) -> List[str]:
        """No generation - panels streamed on demand."""
        return []

    def to_interface_dict(self) -> dict:
        return {"type": "websocket", "endpoint": self.endpoint}
```

#### 4. Visualization Library Adapters

**Adapters for matplotlib, plotly, and altair:**

```python
from typing import Union, Optional
from pathlib import Path
import matplotlib.figure
import plotly.graph_objects as go

class MatplotlibAdapter:
    """Adapter for matplotlib figures."""

    @staticmethod
    def save_figure(
        fig: matplotlib.figure.Figure,
        path: Path,
        format: str = "png",
        dpi: int = 100,
        **kwargs
    ) -> Path:
        """
        Save matplotlib figure to file.

        Parameters
        ----------
        fig : matplotlib.figure.Figure
            Figure to save.
        path : Path
            Output file path.
        format : str
            Image format (png, jpeg, svg).
        dpi : int
            Resolution in dots per inch.

        Returns
        -------
        Path
            Path to saved file.
        """
        fig.savefig(path, format=format, dpi=dpi, bbox_inches='tight', **kwargs)
        return path


class PlotlyAdapter:
    """Adapter for plotly figures."""

    @staticmethod
    def save_figure(
        fig: go.Figure,
        path: Path,
        format: str = "html",
        **kwargs
    ) -> Path:
        """
        Save plotly figure to file.

        Parameters
        ----------
        fig : plotly.graph_objects.Figure
            Figure to save.
        path : Path
            Output file path.
        format : str
            Output format (html, png, jpeg, svg).

        Returns
        -------
        Path
            Path to saved file.
        """
        if format == "html":
            fig.write_html(path, **kwargs)
        else:
            fig.write_image(path, format=format, **kwargs)
        return path


class AltairAdapter:
    """Adapter for altair charts."""

    @staticmethod
    def save_chart(
        chart,  # altair.Chart
        path: Path,
        format: str = "html",
        **kwargs
    ) -> Path:
        """
        Save altair chart to file.

        Parameters
        ----------
        chart : altair.Chart
            Chart to save.
        path : Path
            Output file path.
        format : str
            Output format (html, png, svg).

        Returns
        -------
        Path
            Path to saved file.
        """
        if format == "html":
            chart.save(str(path), embed_options={'renderer': 'svg'}, **kwargs)
        else:
            chart.save(str(path), format=format, **kwargs)
        return path
```

## JSON Specification Format

### displayInfo.json Structure

**Complete specification matching TypeScript interfaces:**

```json
{
  "name": "display_name",
  "description": "Human-readable description",
  "keySig": "unique_key_signature_hash",
  "metas": [
    {
      "varname": "country",
      "label": "Country",
      "type": "factor",
      "levels": ["USA", "UK", "France", "Germany"],
      "nnna": 4
    },
    {
      "varname": "gdp",
      "label": "GDP (USD)",
      "type": "currency",
      "code": "USD",
      "digits": 0,
      "locale": true,
      "log": false,
      "nnna": 4
    },
    {
      "varname": "report_date",
      "label": "Report Date",
      "type": "date",
      "nnna": 4
    }
  ],
  "panelInterface": {
    "type": "file",
    "extension": "png"
  },
  "panelOptions": {
    "width": 600,
    "height": 400,
    "aspect": null,
    "forceSize": false
  },
  "state": {
    "layout": {
      "ncol": 4,
      "nrow": 3,
      "page": 1,
      "arrangement": "row"
    },
    "labels": ["country", "gdp"],
    "filters": [
      {
        "type": "category",
        "varname": "country",
        "values": ["USA", "UK"]
      },
      {
        "type": "range",
        "varname": "gdp",
        "min": 1000000000,
        "max": 25000000000
      }
    ],
    "sorts": [
      {
        "varname": "gdp",
        "dir": "desc"
      }
    ]
  },
  "views": [
    {
      "name": "default",
      "state": {
        "layout": {"ncol": 4, "nrow": 3, "page": 1},
        "labels": ["country"],
        "filters": [],
        "sorts": []
      }
    },
    {
      "name": "high_gdp",
      "state": {
        "layout": {"ncol": 3, "nrow": 2, "page": 1},
        "labels": ["country", "gdp"],
        "filters": [
          {"type": "range", "varname": "gdp", "min": 10000000000}
        ],
        "sorts": [{"varname": "gdp", "dir": "desc"}]
      }
    }
  ],
  "n": 4,
  "thumbnail": "panels/panel_1.png"
}
```

### Key Signature Generation

**Unique identifier based on data content:**

```python
import hashlib
import json

def generate_keysig(data: pd.DataFrame, name: str) -> str:
    """
    Generate unique key signature for display.

    Based on:
    - Display name
    - Column names
    - First and last row values (sample)
    - Data shape

    Parameters
    ----------
    data : pd.DataFrame
        Input DataFrame.
    name : str
        Display name.

    Returns
    -------
    str
        MD5 hash as key signature.
    """
    components = {
        'name': name,
        'columns': list(data.columns),
        'shape': data.shape,
        'first_row': data.iloc[0].to_dict() if len(data) > 0 else {},
        'last_row': data.iloc[-1].to_dict() if len(data) > 0 else {}
    }

    content = json.dumps(components, sort_keys=True, default=str)
    return hashlib.md5(content.encode()).hexdigest()
```

## Implementation Phases

### Phase 1: Core Infrastructure (Weeks 1-4)

**Goal:** Basic display creation with file-based panels and type inference.

**Deliverables:**
1. **Core Classes**
   - `Display` class with basic API
   - Meta variable classes (FactorMeta, NumberMeta, DateMeta, TimeMeta)
   - `FilePanelSource` for pre-generated panels

2. **DataFrame Integration**
   - Validate DataFrame structure
   - Auto-infer meta types from dtypes
   - Extract panel column

3. **JSON Writer**
   - Serialize Display to displayInfo.json
   - Match TypeScript interface structure
   - Generate keysig

4. **matplotlib Integration**
   - `MatplotlibAdapter` for saving figures
   - Support PNG and JPEG formats
   - Configurable DPI and size

5. **File System Management**
   - Create appdir structure
   - Write displayInfo.json
   - Copy/save panel files

**Example Use Case:**
```python
import pandas as pd
import matplotlib.pyplot as plt
from trelliscope import Display

# Generate sample plots
figures = []
for i in range(10):
    fig, ax = plt.subplots()
    ax.plot([1, 2, 3], [i, i*2, i*3])
    ax.set_title(f"Plot {i}")
    figures.append(fig)

df = pd.DataFrame({
    'plot': figures,
    'id': range(10),
    'category': ['A', 'B'] * 5,
    'value': [i * 10 for i in range(10)]
})

display = Display(df, name="simple_demo")
display.set_panel_column("plot")
display.write(path="./output")
```

**Success Criteria:**
- ✅ Create display from DataFrame with matplotlib figures
- ✅ Generate valid displayInfo.json
- ✅ Save 10 panel PNG files correctly
- ✅ Auto-infer factor, number types
- ✅ All tests passing

### Phase 2: Advanced Panel Sources (Weeks 5-8)

**Goal:** Support lazy evaluation, plotly/altair, and HTML panels.

**Deliverables:**
1. **Lazy Panel Generation**
   - `LazyPanelSource` with callable generators
   - Execute functions on-demand during write()
   - Progress tracking for long operations

2. **Additional Visualization Libraries**
   - `PlotlyAdapter` for plotly figures
   - `AltairAdapter` for altair charts
   - Auto-detect figure type
   - HTML export support

3. **HTML Panel Support**
   - Export plotly to interactive HTML
   - Embed altair with vega-embed
   - Handle raw HTML strings

4. **Advanced Meta Types**
   - `CurrencyMeta` with currency codes
   - `HrefMeta` for hyperlinks
   - `GraphMeta` for sparklines
   - `PanelSrcMeta` and `PanelLocalMeta`

5. **Performance Optimizations**
   - Parallel panel generation
   - Configurable batch size
   - Memory-efficient streaming

**Example Use Case:**
```python
import plotly.graph_objects as go

def create_plotly_chart(row):
    """Generate plotly chart on-demand."""
    fig = go.Figure()
    fig.add_trace(go.Scatter(x=row['x'], y=row['y'], mode='lines'))
    fig.update_layout(title=row['title'])
    return fig

df = pd.DataFrame({
    'title': [f"Chart {i}" for i in range(100)],
    'x': [[1, 2, 3, 4, 5] for _ in range(100)],
    'y': [list(range(i, i+5)) for i in range(100)],
    'category': ['A', 'B', 'C', 'D'] * 25
})

# Lazy evaluation - functions called during write()
df['plot'] = df.apply(lambda row: lambda: create_plotly_chart(row), axis=1)

display = Display(df, name="lazy_plotly")
display.set_panel_column("plot")
display.write(parallel=True, n_jobs=4)  # Parallel generation
```

**Success Criteria:**
- ✅ Lazy generation of 100+ panels
- ✅ Plotly HTML panels work in viewer
- ✅ Altair charts export correctly
- ✅ Parallel generation 3-4x speedup
- ✅ Memory usage < 1GB for 1000 panels

### Phase 3: State Management & Configuration (Weeks 9-12)

**Goal:** Full display configuration with filters, sorts, labels, and views.

**Deliverables:**
1. **Layout Configuration**
   - Set ncol, nrow, page, arrangement
   - Validate layout parameters
   - Calculate total pages

2. **Filter System**
   - Range filters for numbers
   - Category filters for factors
   - Date range filters
   - Multiple active filters

3. **Sort Configuration**
   - Single and multi-variable sorts
   - Ascending/descending order
   - Sort precedence

4. **Label System**
   - Select meta variables for labels
   - Custom label templates
   - Dynamic label formatting

5. **Multiple Views**
   - Named view configurations
   - Different filter/sort/label combinations
   - Default view selection

6. **Panel Options**
   - Configure width, height, aspect ratio
   - Force specific dimensions
   - Responsive sizing options

**Example Use Case:**
```python
display = (
    Display(df, name="configured_display", description="Fully configured example")
    .set_panel_column("plot")

    # Configure meta variables
    .add_meta_variable("revenue", type="currency", code="USD")
    .add_meta_variable("profit_margin", type="number", digits=1)
    .add_meta_variable("region", type="factor", levels=["North", "South", "East", "West"])

    # Panel options
    .set_panel_options(width=800, height=600)

    # Default layout
    .set_default_layout(ncol=3, nrow=2, arrangement="row")

    # Default filters
    .add_filter("revenue", type="range", min_val=1000000)
    .add_filter("region", type="category", values=["North", "East"])

    # Default sorts
    .set_default_sorts([
        {"varname": "revenue", "dir": "desc"},
        {"varname": "profit_margin", "dir": "desc"}
    ])

    # Default labels
    .set_default_labels(["region", "revenue"])

    # Additional views
    .add_view(
        name="high_performers",
        filters=[{"varname": "profit_margin", "type": "range", "min": 15.0}],
        sorts=[{"varname": "profit_margin", "dir": "desc"}],
        labels=["region", "profit_margin"]
    )
    .add_view(
        name="by_region",
        sorts=[{"varname": "region", "dir": "asc"}],
        labels=["region"]
    )

    .write()
)
```

**Success Criteria:**
- ✅ All layout options work correctly
- ✅ Filters apply correctly in viewer
- ✅ Multi-variable sorting works
- ✅ Custom labels display properly
- ✅ Multiple views switchable in viewer

### Phase 4: Viewer Integration & Polish (Weeks 13-16)

**Goal:** Production-ready package with viewer, server, and documentation.

**Deliverables:**
1. **Viewer Integration**
   - Bundle trelliscopejs-lib or reference via CDN
   - Generate index.html with viewer
   - Configure viewer initialization

2. **Development Server**
   - Local HTTP server for testing
   - Auto-reload on changes
   - Port configuration
   - Open browser automatically

3. **Deployment Utilities**
   - Static HTML export
   - Server deployment (Flask/FastAPI integration)
   - Docker containerization
   - Cloud deployment guides (AWS S3, Azure, GCP)

4. **Advanced Panel Sources**
   - `URLPanelSource` for remote panels
   - `WebSocketPanelSource` for streaming
   - REST API panel source

5. **Documentation**
   - Complete API reference
   - Tutorial notebooks
   - Example gallery
   - Deployment guides

6. **Performance & Polish**
   - Optimize JSON serialization
   - Thumbnail generation
   - Error handling improvements
   - Progress bars for long operations

**Example Development Server:**
```python
# Built into Display class
display.view(port=8000)  # Launches server and opens browser

# Or standalone server
from trelliscope.server import serve

serve(
    appdir="./trelliscope_output",
    port=8000,
    open_browser=True,
    auto_reload=True
)
```

**Success Criteria:**
- ✅ Viewer loads correctly with all display types
- ✅ Dev server works reliably
- ✅ Static export deployable to any host
- ✅ Complete documentation published
- ✅ 10+ example notebooks

## Environment Setup Requirements

### Python Virtual Environment - MANDATORY

**Environment Name:** `py-trelliscope`

**Setup Steps:**

```bash
# 1. Create virtual environment
python -m venv py-trelliscope

# 2. Activate environment
# macOS/Linux:
source py-trelliscope/bin/activate
# Windows:
py-trelliscope\Scripts\activate

# 3. Upgrade pip
pip install --upgrade pip setuptools wheel

# 4. Install core dependencies
pip install pandas numpy scipy
pip install matplotlib plotly altair
pip install attrs dataclasses-json
pip install orjson  # Fast JSON serialization

# 5. Install development dependencies
pip install pytest pytest-cov black flake8 mypy
pip install jupyter ipykernel

# 6. Register Jupyter kernel
python -m ipykernel install --user --name=py-trelliscope --display-name "Python (py-trelliscope)"

# 7. Create requirements.txt
pip freeze > requirements.txt
```

### Environment Usage Rules

**ALWAYS activate before work:**
```bash
# Verify active
echo $VIRTUAL_ENV  # Should show path to py-trelliscope

# Run scripts
python examples/basic_demo.py

# Run tests
pytest tests/ -v --cov=trelliscope
```

### Dependency Files

**requirements.txt (Core):**
```
pandas>=2.0.0
numpy>=1.24.0
matplotlib>=3.7.0
plotly>=5.14.0
altair>=5.0.0
attrs>=23.0.0
orjson>=3.9.0
```

**requirements-dev.txt:**
```
pytest>=7.4.0
pytest-cov>=4.1.0
black>=23.7.0
flake8>=6.0.0
mypy>=1.4.0
jupyter>=1.0.0
ipykernel>=6.25.0
```

**requirements-optional.txt:**
```
# Web server
flask>=2.3.0
fastapi>=0.100.0
uvicorn>=0.23.0

# Deployment
docker>=6.1.0
boto3>=1.28.0  # AWS
azure-storage-blob>=12.17.0  # Azure
google-cloud-storage>=2.10.0  # GCP

# Performance
joblib>=1.3.0  # Parallel processing
```

### .gitignore Configuration

```gitignore
# Virtual environment
py-trelliscope/
venv/
env/

# Python artifacts
__pycache__/
*.py[cod]
*$py.class
*.so
build/
dist/
*.egg-info/

# Testing
.pytest_cache/
.coverage
htmlcov/

# Jupyter
.ipynb_checkpoints/

# IDE
.vscode/
.idea/
*.swp

# Output
trelliscope_output/
**/displays/

# OS
.DS_Store
```

## Testing Strategy

### Unit Tests

**Test Coverage Requirements: >90%**

```python
# tests/test_display.py
import pytest
import pandas as pd
from trelliscope import Display

def test_display_creation():
    """Test basic display creation."""
    df = pd.DataFrame({'plot': [1, 2, 3], 'value': [10, 20, 30]})
    display = Display(df, name="test")
    assert display.name == "test"
    assert len(display.data) == 3

def test_panel_column_validation():
    """Test panel column must exist."""
    df = pd.DataFrame({'value': [10, 20, 30]})
    display = Display(df, name="test")

    with pytest.raises(ValueError, match="Column 'plot' not found"):
        display.set_panel_column("plot")

def test_meta_type_inference():
    """Test automatic type inference."""
    df = pd.DataFrame({
        'plot': [1, 2, 3],
        'category': ['A', 'B', 'C'],
        'value': [10.5, 20.3, 30.1],
        'date': pd.to_datetime(['2024-01-01', '2024-01-02', '2024-01-03'])
    })

    display = Display(df, name="test").set_panel_column("plot")
    metas = display._infer_metas()

    assert metas['category'].type == 'factor'
    assert metas['value'].type == 'number'
    assert metas['date'].type == 'date'
```

### Integration Tests

```python
# tests/integration/test_matplotlib_integration.py
import matplotlib.pyplot as plt
from pathlib import Path
from trelliscope import Display

def test_matplotlib_display_creation(tmp_path):
    """Test end-to-end display creation with matplotlib."""
    # Create figures
    figures = []
    for i in range(5):
        fig, ax = plt.subplots()
        ax.plot([1, 2, 3], [i, i*2, i*3])
        figures.append(fig)

    # Create display
    df = pd.DataFrame({
        'plot': figures,
        'id': range(5),
        'category': ['A', 'B', 'C', 'D', 'E']
    })

    display = Display(df, name="matplotlib_test")
    display.set_panel_column("plot")
    display.write(path=tmp_path)

    # Verify output
    display_path = tmp_path / "displays" / "matplotlib_test"
    assert (display_path / "displayInfo.json").exists()
    assert (display_path / "panels").exists()
    assert len(list((display_path / "panels").glob("*.png"))) == 5

    # Verify JSON structure
    import json
    with open(display_path / "displayInfo.json") as f:
        info = json.load(f)

    assert info['name'] == "matplotlib_test"
    assert info['n'] == 5
    assert len(info['metas']) == 2  # id and category
```

### Performance Tests

```python
# tests/performance/test_scalability.py
import time
import memory_profiler

def test_10k_panel_generation(benchmark):
    """Benchmark 10k panel generation."""
    df = create_large_dataframe(n=10000)
    display = Display(df, name="perf_test")
    display.set_panel_column("plot")

    start = time.time()
    display.write()
    elapsed = time.time() - start

    assert elapsed < 120  # Under 2 minutes
    print(f"Generated 10k panels in {elapsed:.2f}s")

@memory_profiler.profile
def test_memory_usage_1000_panels():
    """Profile memory usage for 1000 panels."""
    df = create_large_dataframe(n=1000)
    display = Display(df, name="memory_test")
    display.write()
    # Memory should stay under 1GB
```

## Reference Materials

**CRITICAL - Always Consult:**

1. **`.claude_research/TRELLISCOPE_TECHNICAL_ANALYSIS.md`**
   - Complete architecture analysis (14 sections)
   - Core concepts and design patterns
   - Python implementation guide with class structures
   - TypeScript interfaces for JSON schema
   - 15-22 week detailed implementation roadmap

2. **`.claude_research/TRELLISCOPE_RESEARCH.json`**
   - Structured technical specifications
   - Repository analysis with citations
   - Common patterns and expert insights

3. **`reference/trelliscope/` (R package source)**
   - Reference implementation behavior
   - R6 class structure
   - Example usage from R documentation

**Key Sections to Reference:**

- **Section 3: Core Concepts** - Panel model, Meta types, State management
- **Section 4: API Design** - R patterns to adapt for Python
- **Section 7: Python Implementation Guide** - Class structures, DataFrame integration, examples
- **Section 11: TypeScript Interfaces** - JSON schema requirements (displayInfo.json structure)
- **Section 14: Implementation Roadmap** - Week-by-week task breakdown

## Next Steps

1. **Review this specification** with stakeholder/user
2. **Create detailed project plan** in `.claude_plans/projectplan.md`
3. **Set up py-trelliscope environment** following setup instructions above
4. **Begin Phase 1 implementation** starting with core Display class
5. **Write tests continuously** after each feature
6. **Reference research documents** for architecture decisions

---

**Implementation Philosophy:** Direct, complete implementations. No mocks, no TODOs, no placeholders. Build production-ready code from the start following patterns in @.claude/CLAUDE.md.
