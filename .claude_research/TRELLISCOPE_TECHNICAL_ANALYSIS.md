# Trelliscope Technical Research Analysis

## Executive Summary

Trelliscope is an R package enabling interactive exploration of large collections of visualizations through small multiples. It addresses the scalability limitations of traditional faceting by providing filtering, sorting, and pagination capabilities for potentially thousands of plots organized as data frames.

**Core Value Proposition**: Transform data frame rows into explorable visualization panels with rich metadata for navigation.

**Architecture**: Two-tier design with R backend for data processing/specification and standalone JavaScript viewer (React/Redux) for interactive exploration.

**Key Innovation**: Language-agnostic JSON specification enables creation of displays from any programming language while reusing the same viewer.

**Python Port Feasibility**: High - JSON specification is well-defined, viewer is reusable, focus needed on Python API design and integration with matplotlib/plotly/altair.

---

## 1. Architecture Deep Dive

### System Components

```
┌─────────────────────────────────────────────────────────────────┐
│                     TRELLISCOPE ARCHITECTURE                     │
├─────────────────────────────────────────────────────────────────┤
│                                                                  │
│  ┌────────────────────────────────────────────────────────┐    │
│  │              R BACKEND (Data Layer)                    │    │
│  ├────────────────────────────────────────────────────────┤    │
│  │                                                         │    │
│  │  • Display Class (R6)                                   │    │
│  │    - Metadata registry                                  │    │
│  │    - State management                                   │    │
│  │    - View configurations                                │    │
│  │                                                         │    │
│  │  • Meta Classes (R6)                                    │    │
│  │    - NumberMeta, StringMeta, FactorMeta                │    │
│  │    - PanelMeta, DateMeta, CurrencyMeta                 │    │
│  │    - GeoMeta, GraphMeta, HrefMeta                      │    │
│  │                                                         │    │
│  │  • State Classes (R6)                                   │    │
│  │    - DisplayState, LayoutState, LabelState             │    │
│  │    - SortState, FilterState variants                   │    │
│  │                                                         │    │
│  │  • Panel Classes (vctrs)                                │    │
│  │    - ggpanel_vec: ggplot2 objects                      │    │
│  │    - panel_lazy_vec: lazy evaluation                   │    │
│  │    - panel_local_vec: local file refs                  │    │
│  │    - panel_url_vec: URL references                     │    │
│  │                                                         │    │
│  └────────────────────────────────────────────────────────┘    │
│                          ↓                                      │
│                   JSON Serialization                            │
│                          ↓                                      │
│  ┌────────────────────────────────────────────────────────┐    │
│  │            FILE SYSTEM (Persistence Layer)              │    │
│  ├────────────────────────────────────────────────────────┤    │
│  │                                                         │    │
│  │  app_path/                                              │    │
│  │  ├── config.jsonp                (App configuration)    │    │
│  │  ├── id                          (Unique app ID)        │    │
│  │  └── displays/                                          │    │
│  │      ├── displayList.jsonp       (All displays)         │    │
│  │      └── {display_name}/                                │    │
│  │          ├── displayInfo.jsonp   (Display metadata)     │    │
│  │          ├── metaData.js         (Panel metadata)       │    │
│  │          ├── info.html           (Optional info page)   │    │
│  │          └── panels/                                    │    │
│  │              └── {panel_name}/                          │    │
│  │                  └── {key}.{format}  (Panel files)      │    │
│  │                                                         │    │
│  └────────────────────────────────────────────────────────┘    │
│                          ↓                                      │
│                    HTTP/WebSocket                               │
│                          ↓                                      │
│  ┌────────────────────────────────────────────────────────┐    │
│  │         JAVASCRIPT VIEWER (Presentation Layer)          │    │
│  ├────────────────────────────────────────────────────────┤    │
│  │                                                         │    │
│  │  React Components:                                      │    │
│  │  • GridView: Panel grid layout                         │    │
│  │  • TableView: Tabular data view                        │    │
│  │  • FilterSidebar: Filter controls                      │    │
│  │  • SortControls: Sort interface                        │    │
│  │  • LabelDisplay: Panel labels                          │    │
│  │                                                         │    │
│  │  Redux Store:                                           │    │
│  │  • State: layout, filters, sorts, labels               │    │
│  │  • Actions: user interactions                          │    │
│  │  • Reducers: state updates                             │    │
│  │                                                         │    │
│  │  Libraries:                                             │    │
│  │  • Material-UI: UI components                          │    │
│  │  • Crossfilter: Fast filtering                         │    │
│  │  • D3: Visualizations                                   │    │
│  │                                                         │    │
│  └────────────────────────────────────────────────────────┘    │
│                                                                  │
└─────────────────────────────────────────────────────────────────┘
```

### Key Design Patterns

#### 1. R6 Class-Based Architecture
```r
Display <- R6::R6Class(
  public = list(
    initialize = function(name, description, tags, keycols, path, ...),
    set_meta = function(obj, trdf),
    set_state = function(obj),
    as_list = function(),
    as_json = function()
  ),
  private = list(
    name = NULL,
    metas = list(),
    state = NULL,
    views = list()
  )
)
```

**Purpose**: Encapsulation of display configuration with mutable state
**Benefits**: Method dispatch, private fields, cloneable objects
**Python Equivalent**: Python classes with @property decorators and __dict__ serialization

#### 2. Vctrs Custom Vector Types
```r
ggpanel_vec <- vctrs::new_rcrd(
  fields = list(by = by_vals),
  plot_fn = make_plot_obj,
  class = "ggpanel_vec"
)
```

**Purpose**: Store complex objects (plots) in data frame columns
**Benefits**: Maintains data frame structure, custom formatting, lazy evaluation
**Python Equivalent**: Pandas extension types or object dtype with custom accessors

#### 3. Pipe-Friendly Functional Composition
```r
result <- data %>%
  as_panels_df() %>%
  as_trelliscope_df(name = "display") %>%
  set_var_labels(...) %>%
  set_default_sort(...) %>%
  view_trelliscope()
```

**Purpose**: Intuitive, readable workflow composition
**Python Equivalent**: Method chaining with returning self

#### 4. Lazy Panel Evaluation
```r
panel_lazy_vec <- panel_lazy(plot_fn, data, by)
```

**Purpose**: Defer panel generation until needed
**Benefits**: Memory efficiency, progressive rendering
**Python Equivalent**: Generator expressions or callable objects

---

## 2. Core Concepts

### Data Model

#### Panel-Centric Architecture
- Each row in the data frame = one panel (visualization)
- Columns contain panel objects + metadata for filtering/sorting
- Key columns uniquely identify each panel

#### Meta Variables
Typed metadata describing each column:

| Meta Type | Purpose | Filterable | Sortable | Example |
|-----------|---------|-----------|----------|---------|
| panel | Visualization reference | No | No | Plot objects, image URLs |
| number | Numeric values | Yes | Yes | Population, GDP |
| string | Text values | Yes | Yes | Country names |
| factor | Categorical with levels | Yes | Yes | Continent |
| date | Date values | Yes | Yes | Year |
| datetime | Timestamp values | Yes | Yes | Updated timestamp |
| currency | Monetary values | Yes | Yes | Price ($) |
| href | Hyperlinks | No | No | Documentation URL |
| geo | Geographic coordinates | No | No | Lat/long pairs |
| graph | Network relationships | Yes | No | Node connections |

#### State Management
Display state includes:
- **Layout**: Grid dimensions, page number, sidebar visibility, view type
- **Labels**: Visible panel labels
- **Sort**: Multi-column sort specifications
- **Filter**: Active filters per variable
- **FilterView**: Visible filters in sidebar

#### Views
Named state configurations enabling:
- Pre-configured navigation states
- Shareable display configurations
- Quick switching between perspectives

---

## 3. API Design & User Interface

### Core Functions

#### Creation Pipeline
```r
# Step 1: Convert to trelliscope data frame
trdf <- as_trelliscope_df(
  df,                    # Data frame with panel column
  name = "Display Name",
  description = "...",
  key_cols = c("id"),
  path = "./output"
)

# Step 2: Configure metadata
trdf <- trdf %>%
  set_var_labels(
    var1 = "Human Label 1",
    var2 = "Human Label 2"
  ) %>%
  set_tags(
    var1 = c("tag1", "tag2")
  )

# Step 3: Set default state
trdf <- trdf %>%
  set_default_layout(ncol = 3) %>%
  set_default_sort(var1, dir = "desc") %>%
  set_default_filters(
    filter_range(var2, min = 0, max = 100)
  )

# Step 4: Add views
trdf <- trdf %>%
  add_view(
    name = "Top 10",
    state_sort("var1", dir = "desc"),
    state_layout(ncol = 2)
  )

# Step 5: Write and view
trdf <- write_trelliscope(trdf)
view_trelliscope(trdf)
```

#### ggplot2 Integration
```r
# Automatic panel generation from facets
panels <- ggplot(gap, aes(year, life_exp)) +
  geom_point() +
  facet_panels(vars(country, continent)) %>%
  as_panels_df()

# Scales control
facet_panels(
  vars(country),
  scales = "free"     # Options: "same", "free", "sliced"
)
```

#### Panel Sources

**Pre-generated Images**
```r
# URL references
df$panel <- panel_url(image_urls)

# Local files
df$panel <- panel_local(file_paths)
```

**R-generated Plots**
```r
# Lazy generation
df$panel <- panel_lazy(
  plot_fn = function(x) { ggplot(x) + ... },
  data = "data_col",
  by = c("group_var")
)
```

**htmlwidgets**
```r
# Interactive widgets as panels
df$panel <- lapply(data_list, function(d) {
  plotly::plot_ly(d, ...)
})
```

### Configuration Options

#### Panel Options
```r
set_panel_options(
  trdf,
  panel_col = "panel",
  width = 600,
  height = 400,
  format = "png",    # or "svg"
  aspect = 1.5
)
```

#### Input Collection
```r
add_inputs(
  trdf,
  input_text(name = "notes", label = "Notes"),
  input_radio(name = "quality", options = c("good", "bad")),
  input_checkbox(name = "flags", options = c("outlier", "error"))
)
```

---

## 4. Technical Implementation Details

### JSON Specification Format

#### Display Configuration
```json
{
  "name": "Display Name",
  "description": "Description",
  "tags": ["tag1", "tag2"],
  "keycols": ["country", "continent"],
  "metas": [
    {
      "varname": "panel",
      "type": "panel",
      "paneltype": "img",
      "aspect": 1.5,
      "source": {
        "type": "file",
        "isLocal": true
      }
    },
    {
      "varname": "population",
      "type": "number",
      "label": "Population",
      "digits": 0,
      "log": true,
      "locale": true,
      "filterable": true,
      "sortable": true
    }
  ],
  "state": {
    "layout": {
      "ncol": 3,
      "page": 1,
      "viewtype": "grid",
      "sidebarActive": false
    },
    "labels": {
      "varnames": ["country"]
    },
    "sort": [
      {
        "varname": "population",
        "dir": "desc"
      }
    ],
    "filter": []
  }
}
```

#### Panel Metadata
```javascript
window.metaData = [
  {
    "country": "Afghanistan",
    "continent": "Asia",
    "population": 31889923,
    "panel": "panels/panel/Afghanistan_Asia.png"
  },
  // ... more rows
]
```

### Panel Source Types

#### 1. File Source (Static)
```typescript
interface IFilePanelSource {
  type: "file";
  isLocal: boolean;  // true for relative paths
}
```
- Pre-generated images on disk
- Referenced by relative path
- Loaded as `<img>` or `<iframe>`

#### 2. REST Source (API)
```typescript
interface IRESTPanelSource {
  type: "REST";
  url: string;
  apiKey?: string;
  headers?: string;
}
```
- Fetched from API endpoint
- Supports authentication
- Dynamic generation server-side

#### 3. Local WebSocket Source (On-demand)
```typescript
interface ILocalWebSocketPanelSource {
  type: "localWebSocket";
  port: number;
}
```
- Bi-directional communication
- Panels generated on-demand
- R server responds to requests

### WebSocket Protocol

**Client Request**
```json
{
  "panelName": "panel",
  "panelURL": "panels/panel/Afghanistan_Asia.png"
}
```

**Server Response**
- Generates panel if not exists
- Writes to file system
- Returns empty JSON `{}`
- Client polls/loads from file path

### Rendering Pipeline

#### ggplot2 Panels
1. Store plot object in vctrs column
2. On write: iterate rows, render each plot
3. Save as PNG/SVG via `svglite` or base graphics
4. Record relative paths in metadata

#### htmlwidget Panels
1. Store widget object in column
2. Extract dependencies (JS/CSS)
3. Write dependencies to shared `libs/` directory
4. Render widget to HTML iframe
5. Reference iframe path in metadata

---

## 5. Frontend JavaScript Viewer

### Technology Stack
- **React**: Component architecture
- **Redux**: State management
- **Material-UI**: UI components
- **Crossfilter**: Fast multi-dimensional filtering
- **D3**: Custom visualizations
- **Webpack**: Bundling

### Key Components

#### GridView Component
- Renders panels in responsive grid
- Virtual scrolling for performance
- Pagination controls
- Click handlers for panel selection

#### FilterSidebar Component
- Dynamic filter controls based on meta types
- Number range sliders
- Category checkboxes
- Date range pickers
- Regex search for strings

#### Redux Store Structure
```javascript
{
  config: {
    name: "App Name",
    displays: [...]
  },
  display: {
    name: "Display Name",
    metas: [...],
    state: {...}
  },
  data: {
    rows: [...],
    filtered: [...]
  },
  ui: {
    layout: {...},
    sort: [...],
    filter: [...]
  }
}
```

### Data Loading Strategy

#### JSONP for Static Hosting
```javascript
// Callback function defined in HTML
window.__loadDisplayInfo__abc123 = function(data) {
  // Process display info
}
```

#### JSON for Server Hosting
```javascript
fetch('/displays/displayInfo.json')
  .then(r => r.json())
  .then(data => { /* process */ })
```

---

## 6. Implementation Insights for Python Port

### Core Requirements

#### 1. Class Structure
```python
# Equivalent to R6 classes
class Display:
    def __init__(self, name, description, ...):
        self.name = name
        self.metas = []
        self.state = DisplayState()

    def set_meta(self, meta):
        self.metas.append(meta)
        return self

    def as_dict(self):
        return {
            'name': self.name,
            'metas': [m.as_dict() for m in self.metas],
            'state': self.state.as_dict()
        }

class Meta:
    def __init__(self, varname, type, ...):
        self.varname = varname
        self.type = type

    def as_dict(self):
        return self.__dict__

class NumberMeta(Meta):
    def __init__(self, varname, digits=None, log=None, ...):
        super().__init__(varname, 'number')
        self.digits = digits
        self.log = log
```

#### 2. DataFrame Integration
```python
import pandas as pd

class TrelliscopeDataFrame:
    def __init__(self, df, name, description, ...):
        self.df = df
        self.display = Display(name, description, ...)
        self._infer_metas()

    def _infer_metas(self):
        # Automatic metadata inference from column types
        for col in self.df.columns:
            if pd.api.types.is_numeric_dtype(self.df[col]):
                self.display.set_meta(NumberMeta(col))
            elif pd.api.types.is_string_dtype(self.df[col]):
                self.display.set_meta(StringMeta(col))
            # ... more types

    def set_var_labels(self, **kwargs):
        for var, label in kwargs.items():
            meta = self._get_meta(var)
            meta.label = label
        return self

    def write(self, path):
        # Write JSON files
        # Write panels
        # Return self for viewing
        pass
```

#### 3. Panel Handling

**Panel Column Type**
```python
from typing import Callable, Any

class PanelColumn:
    def __init__(self, data, render_fn=None):
        self.data = data
        self.render_fn = render_fn

    def render(self, index, path, width, height):
        # Render panel at index to path
        if self.render_fn:
            fig = self.render_fn(self.data[index])
            fig.savefig(path, width=width, height=height)
        # Handle other sources
```

**Integration with Plotting Libraries**
```python
# Matplotlib
def create_panel_column_matplotlib(figure_fn, data_col, by_cols):
    def render_fn(row):
        fig, ax = plt.subplots()
        figure_fn(ax, row)
        return fig
    return PanelColumn(df, render_fn)

# Plotly
def create_panel_column_plotly(figure_fn, data_col, by_cols):
    def render_fn(row):
        fig = figure_fn(row)
        return fig.to_image(format='png')
    return PanelColumn(df, render_fn)

# Altair
def create_panel_column_altair(chart_fn, data_col, by_cols):
    def render_fn(row):
        chart = chart_fn(row)
        chart.save('temp.png')
        return 'temp.png'
    return PanelColumn(df, render_fn)
```

#### 4. State Management
```python
class DisplayState:
    def __init__(self):
        self.layout = LayoutState()
        self.labels = LabelState()
        self.sort = []
        self.filter = []

    def as_dict(self):
        return {
            'layout': self.layout.as_dict(),
            'labels': self.labels.as_dict(),
            'sort': [s.as_dict() for s in self.sort],
            'filter': [f.as_dict() for f in self.filter]
        }

class FilterState:
    def __init__(self, varname, filtertype):
        self.varname = varname
        self.filtertype = filtertype

class NumberRangeFilterState(FilterState):
    def __init__(self, varname, min=None, max=None):
        super().__init__(varname, 'numberrange')
        self.min = min
        self.max = max
```

#### 5. File Writing
```python
import json
from pathlib import Path

def write_trelliscope(trdf, path, jsonp=True):
    display_path = Path(path) / 'displays' / sanitize(trdf.display.name)
    display_path.mkdir(parents=True, exist_ok=True)

    # Write display info
    display_info = trdf.display.as_dict()
    if jsonp:
        content = f"__loadDisplayInfo__abc123({json.dumps(display_info)})"
        (display_path / 'displayInfo.jsonp').write_text(content)
    else:
        (display_path / 'displayInfo.json').write_text(json.dumps(display_info))

    # Write metadata
    metadata = trdf.df.to_dict('records')
    js_content = f"window.metaData = {json.dumps(metadata)}"
    (display_path / 'metaData.js').write_text(js_content)

    # Write panels
    write_panels(trdf, display_path)

    # Update display list
    update_display_list(path, jsonp)
```

### Integration Strategies

#### Option 1: Pure Python Implementation
- Replicate R package functionality in Python
- Support matplotlib, plotly, altair
- Use existing trelliscopejs-lib viewer
- **Pros**: Native Python experience, flexible
- **Cons**: Significant development effort

#### Option 2: Thin Python Wrapper
- Minimal Python API
- Call R package via rpy2
- **Pros**: Leverage existing implementation
- **Cons**: R dependency, limited customization

#### Option 3: Hybrid Approach
- Python classes for data handling
- Generate JSON specification directly
- Reuse JavaScript viewer
- Extend viewer for Python-specific needs
- **Pros**: Best of both worlds
- **Cons**: Maintenance of viewer customizations

---

## 7. Code Examples from Documentation

### Basic Usage
```r
library(ggplot2)
library(dplyr)

# Create panels from ggplot facets
panel_dat <- (
  ggplot(gap, aes(year, life_exp)) +
    geom_point() +
    facet_panels(vars(country, continent))
) |>
  as_panels_df()

# Add metadata
meta_dat <- gap |>
  group_by(country, continent) |>
  summarise(
    mean_life_exp = mean(life_exp),
    min_life_exp = min(life_exp),
    max_life_exp = max(life_exp),
    .groups = "drop"
  )

# Create display
joined_dat <- left_join(panel_dat, meta_dat) |>
  as_trelliscope_df(name = "life_expectancy") |>
  set_var_labels(
    mean_life_exp = "Mean Life Expectancy",
    min_life_exp = "Min Life Expectancy"
  ) |>
  set_default_layout(ncol = 4) |>
  set_default_sort("mean_life_exp", dir = "desc")

view_trelliscope(joined_dat)
```

### Advanced Configuration
```r
# Custom panel generation
df <- data.frame(
  group = letters[1:10],
  value = runif(10)
)

df$panel <- panel_lazy(
  plot_fn = function(x) {
    ggplot(x, aes(x = 1, y = value)) +
      geom_bar(stat = "identity")
  },
  data = df,
  by = "group"
)

# Multiple views
trdf <- as_trelliscope_df(df, name = "bars") |>
  add_view(
    name = "Ascending",
    state_sort("value", dir = "asc"),
    state_layout(ncol = 5)
  ) |>
  add_view(
    name = "Descending",
    state_sort("value", dir = "desc"),
    state_layout(ncol = 2)
  )

# User inputs
trdf <- add_inputs(
  trdf,
  input_radio(
    name = "quality",
    label = "Data Quality",
    options = c("good", "questionable", "bad")
  ),
  input_text(
    name = "notes",
    label = "Notes",
    height = 6
  )
)
```

### Pre-generated Images
```r
# From URLs
df <- data.frame(
  name = c("Image 1", "Image 2"),
  img = panel_url(c(
    "https://example.com/img1.png",
    "https://example.com/img2.png"
  ))
)

# From local files
df <- data.frame(
  name = paste("Image", 1:10),
  img = panel_local(paste0("images/img", 1:10, ".png"))
)

as_trelliscope_df(df, name = "images") |>
  view_trelliscope()
```

---

## 8. Design Decisions & Rationale

### Key Architectural Choices

#### 1. Language-Agnostic JSON Specification
**Decision**: Separate data generation (R/Python) from visualization (JavaScript)
**Rationale**:
- Enables multi-language support
- JavaScript ecosystem better for interactive web UIs
- Viewer can be improved independently
- Static file deployment without server

#### 2. R6 Classes Over S3
**Decision**: Use R6 object system for core classes
**Rationale**:
- Mutable state needed for configuration
- Method dispatch clearer than S3 generics
- Encapsulation of private fields
- Easier to reason about object lifecycle

#### 3. Vctrs for Panel Columns
**Decision**: Custom vector types for panel storage
**Rationale**:
- Maintains data frame structure
- Custom formatting in tibble printing
- Type safety for panel operations
- Enables lazy evaluation

#### 4. JSONP for Static Deployment
**Decision**: Support JSONP format alongside JSON
**Rationale**:
- Static hosting (GitHub Pages, S3) without CORS issues
- No server required for deployment
- Simple deployment model for users

#### 5. WebSocket for Dynamic Panels
**Decision**: Optional WebSocket server for on-demand rendering
**Rationale**:
- Memory efficiency for large display counts
- Progressive enhancement (static fallback)
- Real-time generation during exploration
- Decoupled from main display serving

#### 6. Automatic Metadata Inference
**Decision**: Infer meta types from R data types by default
**Rationale**:
- Reduce boilerplate for users
- Sensible defaults for common cases
- Override-able when needed
- Fail loudly on ambiguity

#### 7. Pipe-Friendly API
**Decision**: All configuration functions return modified object
**Rationale**:
- Integrates with tidyverse ecosystem
- Readable, declarative configuration
- Incremental composition of complex displays

---

## 9. Performance Considerations

### Scalability Strategies

#### Panel Count
- **100s of panels**: Pre-generate all, static files
- **1000s of panels**: Use pagination, lazy loading
- **10000+ panels**: WebSocket on-demand, aggressive caching

#### File Size Optimization
- SVG for vector graphics (smaller, scalable)
- PNG with compression for raster
- Thumbnail generation for grid view
- Full resolution on panel click

#### Memory Management
- Vctrs for efficient column storage
- Lazy evaluation defers computation
- Streaming write for large datasets
- Chunk processing for panel generation

#### Frontend Performance
- Crossfilter for O(1) filtering
- Virtual scrolling in grid
- Web workers for heavy computation
- IndexedDB for client-side caching

---

## 10. Security Considerations

### File Path Sanitization
```r
sanitize <- function(x) {
  # Remove special characters
  # Prevent directory traversal
  # Ensure valid filenames
}
```

### JSONP vs JSON Trade-offs
- **JSONP**: Easier deployment, potential XSS risk
- **JSON**: More secure, requires CORS configuration

### WebSocket Authentication
- Local-only by default (127.0.0.1)
- Port randomization
- No authentication implemented (trust local environment)

---

## 11. Testing Strategy

### Unit Tests
- Meta class creation and validation
- State class serialization
- Panel rendering functions
- File path sanitization

### Integration Tests
- End-to-end display creation
- File writing and structure
- JSON schema validation
- Viewer loading

### Visual Regression Tests
- Panel rendering consistency
- Layout preservation
- Filter/sort behavior

---

## 12. Python Implementation Roadmap

### Phase 1: Core Infrastructure (4-6 weeks)
1. Meta class hierarchy (NumberMeta, StringMeta, etc.)
2. State classes (DisplayState, FilterState, etc.)
3. Display class with configuration methods
4. TrelliscopeDataFrame wrapper
5. JSON serialization

### Phase 2: Panel Handling (4-6 weeks)
1. Panel column abstraction
2. Matplotlib integration
3. Plotly integration
4. Image URL/local file support
5. Panel writing utilities

### Phase 3: Advanced Features (3-4 weeks)
1. View management
2. Input specifications
3. Automatic metadata inference
4. State utilities (filters, sorts)

### Phase 4: Server & Deployment (2-3 weeks)
1. Optional WebSocket server (FastAPI/Flask)
2. Static file generation
3. CLI for serving displays

### Phase 5: Polish & Documentation (2-3 weeks)
1. API documentation
2. Example gallery
3. Migration guides from R
4. Performance optimization

**Total Estimated Effort**: 15-22 weeks (1 developer)

---

## 13. Comparison with Alternatives

### vs Plotly Dash
- **Trelliscope**: Static generation, file-based, viewer-focused
- **Dash**: Server-required, callback-based, app-focused
- **Use Trelliscope for**: Exploration of pre-computed visualizations
- **Use Dash for**: Interactive apps with computation on-demand

### vs Panel + hvPlot
- **Trelliscope**: Grid navigation, filtering UI, state management
- **Panel**: General purpose dashboards, streaming data
- **Use Trelliscope for**: Faceted plot exploration at scale
- **Use Panel for**: Custom dashboards with diverse widgets

### vs Observable Plot
- **Trelliscope**: Multi-panel displays, rich metadata
- **Observable**: Single-page reactive documents
- **Use Trelliscope for**: Collections of related visualizations
- **Use Observable for**: Exploratory notebooks with interactivity

---

## 14. Key Takeaways for Python Port

### Must-Haves
1. Clean, pipe-friendly API
2. Automatic metadata inference
3. Support for matplotlib/plotly/altair
4. JSON specification generation
5. File writing utilities

### Should-Haves
1. WebSocket server for lazy panels
2. Integration with pandas/polars
3. CLI for serving displays
4. State management utilities

### Nice-to-Haves
1. Custom JavaScript viewer extensions
2. Cloud deployment helpers (S3, Azure, GCS)
3. Notebook integration (Jupyter widgets)
4. Comparison with R implementation

### Don't Need (Initially)
1. htmlwidget equivalent (focus on images)
2. Shiny/RMarkdown integration (Python-specific)
3. Complex graph/geo metadata (add later)

---

## References

1. Hafen, Ryan. "trelliscope - R Trelliscope package." GitHub, 2024. https://github.com/trelliscope/trelliscope
2. Hafen, Ryan. "trelliscopejs-lib - JavaScript viewer for Trelliscope displays." GitHub/npm, 2024. https://github.com/trelliscope/trelliscopejs-lib
3. "Trelliscope Documentation." Trelliscope.org, 2024. https://trelliscope.org/trelliscope/articles/trelliscope.html
4. "Introduction to trelliscopejs." CRAN, 2024. https://cran.r-project.org/web/packages/trelliscopejs/vignettes/trelliscopejs.html

---

## Appendix A: File Structure Example

```
trelliscope_app/
├── config.jsonp                    # App-level configuration
├── id                              # Unique app identifier
└── displays/
    ├── displayList.jsonp           # List of all displays
    ├── libs/                       # Shared JavaScript libraries
    │   └── htmlwidgets-1.5.4/
    └── life_expectancy/            # Display directory
        ├── displayInfo.jsonp       # Display metadata
        ├── metaData.js             # Panel data
        ├── info.html               # Optional info page
        └── panels/
            └── panel/              # Panel images
                ├── Afghanistan_Asia.png
                ├── Albania_Europe.png
                └── ...
```

## Appendix B: TypeScript Interface Summary

```typescript
// Core types
interface IDisplay {
  name: string;
  description: string;
  tags: string[];
  keycols: string[];
  metas: IMeta[];
  state: IDisplayState;
  views: IView[];
  inputs: IInputs;
}

interface IMeta {
  varname: string;
  type: MetaType;
  label: string;
  tags: string[];
  filterable: boolean;
  sortable: boolean;
}

interface IDisplayState {
  layout: ILayoutState;
  labels: ILabelState;
  sort: ISortState[];
  filter: IFilterState[];
  filterView: string[];
}
```

## Appendix C: Python API Mockup

```python
import trelliscope as tr
import matplotlib.pyplot as plt
import pandas as pd

# Load data
df = pd.read_csv('data.csv')

# Create panels
def plot_fn(row):
    fig, ax = plt.subplots()
    ax.plot(row['x'], row['y'])
    ax.set_title(row['name'])
    return fig

df_panels = df.groupby('group').apply(
    lambda g: tr.create_panel(plot_fn, g)
)

# Create display
display = (
    tr.TrelliscopeDataFrame(df_panels, name='My Display')
    .set_var_labels(
        mean_value='Mean Value',
        group='Group Name'
    )
    .set_default_layout(ncol=3)
    .set_default_sort('mean_value', ascending=False)
    .add_filter(tr.filter_range('mean_value', min=0, max=100))
)

# Write and view
display.write('output/')
display.view()
```
