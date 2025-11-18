# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

## Project Overview

**py-trelliscope2** is a Python implementation of Trelliscope for creating interactive, scalable visualization displays. The project uses a 3-tier hybrid architecture where Python generates JSON specifications consumed by the existing trelliscopejs-lib (v0.7.16) JavaScript viewer.

**Key Architecture**: Python Backend → JSON Specification → JavaScript Viewer (React/Redux)

**Purpose**: Enable interactive exploration of large collections of plots (hundreds to millions) through automatic faceting, rich filtering/sorting via metadata (cognostics), and a self-contained HTML viewer.

## Critical Discoveries

### 1. File-Based Panel Requirements

**IMPORTANT**: The trelliscopejs-lib viewer requires THREE files for file-based static panels to function:

1. `displayInfo.json` - Full display configuration with embedded cogData
2. `metaData.json` - Separate cogData array file
3. **`metaData.js`** - JavaScript file with `window.metaData = [...]` wrapper

Even though cogData is embedded in displayInfo.json, metaData.js is MANDATORY. The viewer makes explicit requests for this file and won't load panels without it.

See `.claude_plans/FILE_BASED_PANELS_SOLUTION.md` for complete working structure.

### 2. Factor Indexing Must Be 1-Based

**IMPORTANT**: The trelliscopejs-lib viewer expects **R-style 1-based factor indexing**, not Python/JavaScript 0-based.

#### The Issue:
- Python/pandas use 0-based indices for categoricals: [0, 1, 2, ...]
- R uses 1-based indices for factors: [1, 2, 3, ...]
- The viewer was built for R and expects 1-based indices

#### The Solution:
Factor indices are automatically converted from 0-based to 1-based during JSON serialization in `trelliscope/serialization.py`:

```python
# Convert factor indices from 0-based to 1-based (R-style)
if meta and meta.type == "factor" and isinstance(value, (int, float)):
    value = int(value) + 1  # Convert 0-based to 1-based
```

#### Example:
```json
{
  "cogData": [
    {"country": 1},  // ✅ 1-based (maps to levels[0] = "Algeria")
    {"country": 2},  // ✅ 1-based (maps to levels[1] = "Denmark")
  ],
  "metas": [{
    "type": "factor",
    "levels": ["Algeria", "Denmark", "Germany"]
  }]
}
```

**Why**: The viewer code does `levels[factor - 1]`, expecting 1-based input. With 0-based indices, the first item (0) would calculate as `levels[-1]` → undefined → "[missing]".

See `.claude_plans/FACTOR_INDEXING_SOLUTION.md` for complete details.

## Development Commands

### Environment Setup

```bash
# Create virtual environment
conda create -n py-trelliscope python=3.10
conda activate py-trelliscope

# Install package in development mode
pip install -e .

# Install with visualization extras
pip install -e ".[viz]"  # matplotlib, plotly

# Install with Dash viewer
pip install -e ".[dash]"  # dash, dash-bootstrap-components

# Install Jupyter integration
pip install -e ".[jupyter]"  # jupyter-dash

# Install all extras
pip install -e ".[all]"
```

### Testing

```bash
# Run all tests
pytest

# Run with coverage
pytest --cov=trelliscope --cov-report=html

# Run specific module tests
pytest tests/unit/test_display.py
pytest tests/unit/test_meta.py

# Run Dash viewer tests
pytest tests/dash_viewer/

# Run single test
pytest tests/unit/test_display.py::test_display_creation -v
```

### Viewer Testing

**Static HTML Viewer** (trelliscopejs-lib):
```bash
# Start HTTP server for examples
cd examples/output
python3 -m http.server 8000

# View displays at:
# http://localhost:8000/
# http://localhost:8000/{display_name}/
```

**Interactive Dash Viewer**:
```bash
# Run Dash viewer demo
python examples/phase3_complete_demo.py

# Access at:
# http://localhost:8053
```

### Panel Server (REST API)

```bash
# Start Flask panel server (for REST-based panels)
cd examples
python3 panel_server.py

# Server runs on port 5001 by default
# Endpoints:
#   http://localhost:5001/api/health
#   http://localhost:5001/api/panels/<display>/<id>
```

Note: macOS AirPlay uses port 5000, use 5001 or 8000+ for servers.

## Core Architecture

### Package Structure

```
trelliscope/
├── __init__.py              # Package exports
├── display.py               # Display class (main entry point)
├── meta.py                  # Meta variable type system
├── inference.py             # DataFrame type inference
├── serialization.py         # JSON writers (handles 1-based conversion)
├── panel_interface.py       # Panel interface abstractions
├── config.py                # Configuration management
├── export.py                # Export utilities
├── server.py                # Development server
├── viewer.py                # Viewer integration
├── viewer_html.py           # HTML generation
├── multi_display.py         # Multi-display support
├── panels/                  # Panel rendering (matplotlib, plotly)
│   ├── __init__.py
│   ├── matplotlib_adapter.py
│   ├── plotly_adapter.py
│   └── manager.py
├── dash_viewer/             # Interactive Dash viewer
│   ├── __init__.py
│   ├── app.py               # Main Dash application
│   ├── state.py             # State management
│   ├── loader.py            # Display loading utilities
│   ├── performance.py       # Performance monitoring
│   ├── views_manager.py     # Views persistence
│   ├── assets/
│   │   └── style.css        # Responsive CSS
│   └── components/          # UI components
│       ├── filters.py       # Filter controls
│       ├── sorts.py         # Sort controls
│       ├── controls.py      # Control bar
│       ├── layout.py        # Panel grid
│       ├── views.py         # Views management
│       ├── search.py        # Global search
│       ├── panel_detail.py  # Detail modal
│       ├── layout_controls.py # Layout configuration
│       ├── label_config.py  # Label configuration
│       ├── keyboard.py      # Keyboard shortcuts
│       ├── export.py        # Export functionality
│       ├── notifications.py # Toast notifications
│       └── help.py          # Help documentation
└── utils/                   # Utility functions
    ├── __init__.py
    └── validation.py
```

### Key Classes

**Display** (`display.py`): Main class for creating trelliscope displays
- Fluent API with method chaining
- DataFrame-centric data model (each row = one panel + cognostics)
- Generates displayInfo.json, metaData.json, metaData.js

**Meta Variables** (`meta.py`): Type system for cognostics
- 8 types: factor, number, currency, date, time, href, graph, base
- Auto-inference from pandas dtypes
- Manual override capability

**PanelInterface** (`panel_interface.py`): Abstractions for panel sources
- LocalPanelInterface: File-based panels (static PNG/HTML)
- RESTPanelInterface: REST API panels (dynamic loading)
- WebSocketPanelInterface: WebSocket panels (streaming)

**PanelManager** (`panels/manager.py`): Coordinates panel rendering
- Delegates to visualization library adapters (matplotlib, plotly)
- Handles figure object conversion to files
- Error-resilient rendering

**DashViewer** (`dash_viewer/app.py`): Interactive Plotly Dash viewer application
- Complete web-based interface for exploring displays
- Features: filters, sorting, search, views, panel details, keyboard shortcuts
- Responsive design (mobile/tablet/desktop)
- 15+ modular components with 20+ callbacks

**DisplayState** (`dash_viewer/state.py`): State management for Dash viewer
- Centralized state (filters, sorts, layout, labels, views)
- State serialization/deserialization
- Validation and type checking

**ViewsManager** (`dash_viewer/views_manager.py`): Views persistence layer
- Save/load/delete named views
- JSON-based storage
- View metadata tracking

## displayInfo.json Required Fields

For file-based panels to work with trelliscopejs-lib v0.7.16:

```javascript
{
  "name": str,
  "group": "common",           // Required
  "description": str,
  "keysig": str,
  "n": int,                    // Number of panels
  "height": 500,               // Required
  "width": 500,                // Required
  "tags": [],                  // Required (can be empty)
  "keycols": [],               // Required (can be empty)
  "metas": [...],              // Array of meta definitions
  "inputs": null,              // Required
  "cogInterface": {            // Required
    "name": str,
    "group": "common",
    "type": "JSON"
  },
  "cogInfo": {...},            // Required - detailed meta info
  "cogDistns": {},             // Required (can be empty object)
  "cogData": [...],            // Required - embedded data (1-based factors!)
  "state": {...},              // Layout, filters, sorts
  "views": [],                 // Saved views
  "primarypanel": "panel",     // Which meta is the panel
  "panelInterface": {          // Required
    "type": "file",
    "base": "panels",
    "panelCol": "panel"
  },
  "imgSrcLookup": {}           // Required (empty object)
}
```

## Panel File Naming

**Correct**: `0.png`, `1.png`, `2.png` (ID only)
**Wrong**: `panel_0.png`, `panel_1.png` (prefix not used)

Panel filenames must match `panelKey` values in cogData.

## metaData Files Structure

**metaData.json**:
```json
[
  {
    "id": 0,
    "value": 10,
    "category": 1,            // 1-based if factor!
    "panelKey": "0",
    "panel": "panels/0.png"   // Relative path
  }
]
```

**metaData.js**:
```javascript
window.metaData = [
  {
    "id": 0,
    "value": 10,
    "category": 1,            // 1-based if factor!
    "panelKey": "0",
    "panel": "panels/0.png"   // Relative path
  }
];
```

Panel paths are RELATIVE: `"panels/0.png"`, not full URLs.

## Viewer Compatibility

### Target: trelliscopejs-lib v0.7.16

- Pure JSON data format
- React/Redux frontend
- File-based OR REST API panels
- CDN: `https://unpkg.com/trelliscopejs-lib@0.7.16/dist/assets/`

### DO NOT USE: Old Viewer (trelliscopejs_widget v0.3.2)

R examples in `examples/output/r_example_static/` use this:
- JSONP format with callback wrappers
- htmlwidgets framework
- Incompatible with modern viewer

## Dash Viewer Architecture

### Component Organization

The Dash viewer follows a modular component architecture with clear separation of concerns:

**State Layer** (`state.py`, `loader.py`):
- `DisplayState`: Centralized state management (filters, sorts, layout, labels, views)
- `DisplayLoader`: Load display data from JSON files
- Immutable state updates with validation

**Component Layer** (`components/`):
- Each component is self-contained (layout, callbacks, styling)
- Components communicate through Dash callbacks
- No direct component-to-component dependencies

**Callback Pattern**:
```python
@callback(
    Output('component-id', 'property'),
    Input('trigger-id', 'property'),
    State('state-id', 'property')
)
def update_component(trigger_value, current_state):
    # Update logic here
    return updated_value
```

### Adding New Components

1. Create new file in `components/` (e.g., `my_component.py`)
2. Define layout function returning dash components
3. Define callback functions decorated with `@callback`
4. Import and integrate in `app.py`
5. Add tests in `tests/dash_viewer/`

### State Management Pattern

```python
# Get current state
state = DisplayState.from_dict(state_dict)

# Update state immutably
new_state = state.apply_filter(filter_spec)

# Serialize for storage
state_json = state.to_dict()
```

## Common Development Tasks

### Creating a Display

```python
import pandas as pd
from trelliscope import Display

df = pd.DataFrame({
    'panel_id': ['A', 'B', 'C'],
    'category': ['cat1', 'cat2', 'cat3'],
    'value': [10, 20, 30]
})

display = (
    Display(df, name="my_display")
    .set_panel_column('panel_id')
    .infer_metas()
    .write()
)
```

### Running the Dash Viewer

```python
from trelliscope.dash_viewer import create_app

# Load display and create app
app = create_app(display_path="path/to/my_display")

# Run server
app.run(debug=True, port=8053)

# Access at: http://localhost:8053
```

### Testing File-Based Panels

1. Generate display with panel files
2. Start HTTP server: `python3 -m http.server 8000`
3. Open browser: `http://localhost:8000/`
4. Check browser console for errors
5. Verify Network tab shows requests for:
   - `displayInfo.json`
   - `metaData.js`
   - `panels/0.png`, `panels/1.png`, etc.

### Debugging Panel Loading Issues

**HTML Viewer** (if viewer shows "0 of 0"):
1. Check `displayInfo.json` has all required fields
2. Verify `metaData.js` exists and is accessible
3. Confirm `metaData.json` exists
4. Check panel file naming (`0.png` not `panel_0.png`)
5. Verify panel paths in metaData are relative
6. **Check factor indices are 1-based** (not 0-based)
7. Check browser DevTools Console for JavaScript errors
8. Check Network tab for 404 errors

**Dash Viewer** (if panels don't display):
1. Check display path is correct in `create_app()`
2. Verify `displayInfo.json` exists and is valid JSON
3. Check console for Python exceptions
4. Verify all required meta variables are defined
5. Check filter/sort state for conflicts
6. Look for toast notifications showing errors
7. Test with `debug=True` for detailed error messages
8. Verify port is not already in use (try different port)

### Debugging Dash Callback Issues

**Circular dependencies**:
- Dash will raise `CircularDependency` error
- Solution: Use `dash.no_update` or restructure callbacks
- Check that Input/Output pairs don't create cycles

**Missing IDs**:
- Error: "A component that doesn't exist was used in a callback"
- Solution: Ensure component ID exists in layout before callback registration
- Check for typos in component IDs

**State updates not reflecting**:
- Verify callback is registered (check console on startup)
- Ensure Output targets the correct component property
- Use browser DevTools to inspect component state
- Check if `prevent_initial_call=True` is blocking updates

## File Organization

### Safe to Modify
- `/trelliscope/` - Python package source
- `/tests/` - Test files
- `/examples/` - Example scripts and notebooks
- `/.claude_plans/` - Progress tracking and planning docs

### Never Modify
- `/reference/` - R package source (reference only)
- `/py-trelliscope/` or `/py-trelliscope-env/` - Virtual environment
- `/examples/output/r_example*/` - R-generated examples (old format)
- Output directories created by displays

### Output Structure (Generated)

```
{appdir}/
├── config.json
├── displays/
│   ├── displayList.json
│   └── {display_name}/
│       ├── displayInfo.json
│       ├── metaData.json      # REQUIRED
│       ├── metaData.js         # REQUIRED
│       └── panels/
│           ├── 0.png
│           ├── 1.png
│           └── ...
└── index.html
```

## Python Code Style

- **Variables/Functions**: `snake_case`
- **Classes**: `PascalCase`
- **Constants**: `SCREAMING_SNAKE_CASE`
- **Type hints**: Required for all function signatures
- **Docstrings**: NumPy-style for all public APIs
- **PEP 8**: Followed strictly

## Meta Variable Types

| Type | Python Type | Use Case |
|------|-------------|----------|
| factor | categorical | Categories with levels (1-based in JSON!) |
| number | numeric | Continuous values |
| currency | numeric | Monetary values |
| date | datetime | Dates without time |
| time | datetime | Dates with time |
| href | str | URLs/links |
| graph | any | Sparklines/mini-plots |
| base | any | Generic metadata |

## Common Pitfalls

### HTML Viewer Issues
1. **Missing metaData.js**: Viewer requires this even with embedded cogData
2. **Wrong panel naming**: Use `0.png` not `panel_0.png`
3. **Full URLs in metaData**: Use relative paths `panels/0.png`
4. **Missing required fields**: displayInfo.json needs all fields listed above
5. **Using R examples**: Old JSONP format is incompatible
6. **0-based factor indices**: Factors must be 1-based in JSON (automatic conversion in serialization.py)

### Dash Viewer Issues
7. **Port conflicts**: macOS AirPlay uses port 5000, use 5001 or 8000+
8. **Missing Dash dependencies**: Install with `pip install -e ".[dash]"`
9. **Circular callbacks**: Use `dash.no_update` to break cycles
10. **State initialization**: DisplayState handles None values, don't assume all fields are populated
11. **Component ID conflicts**: Each component needs unique ID across entire app
12. **Callback order**: Dash executes callbacks in dependency order, not definition order
13. **DataFrame modifications**: Always work with copies to avoid modifying original data

### Development Workflow Issues
14. **Virtual environment**: Always activate `py-trelliscope` before development
15. **Package installation**: Use `pip install -e .` for development mode
16. **Test data**: Don't commit test outputs to git (add to .gitignore)
17. **Browser caching**: Hard refresh (Cmd+Shift+R) when CSS/JS doesn't update

## Key Reference Files

**Always consult**:
- `.claude_plans/FILE_BASED_PANELS_SOLUTION.md` - Working panel structure
- `.claude_plans/FACTOR_INDEXING_SOLUTION.md` - Factor indexing details
- `.claude/CLAUDE.md` - Project directives and patterns
- `README.md` - User-facing documentation

**Technical references**:
- `.claude_research/TRELLISCOPE_TECHNICAL_ANALYSIS.md` - Architecture details
- R source in `/reference/` - Behavior reference only

## Viewer Options

### 1. Static HTML Viewer (trelliscopejs-lib v0.7.16)

**Use when**: Deploying static displays without a server
**How to use**:
```python
display = Display(df, name="my_display").write()
# Generates: displayInfo.json, metaData.json, metaData.js, panels/
# Serve via: python3 -m http.server 8000
```

**Features**:
- Self-contained HTML + JavaScript
- No server required after generation
- React/Redux frontend
- Fast initial load

**Limitations**:
- Static files only
- No server-side filtering
- Limited to file-based panels

### 2. Interactive Dash Viewer (Recommended)

**Use when**: Need interactive exploration with live updates
**How to use**:
```python
from trelliscope.dash_viewer import create_app

app = create_app(display_path="path/to/display")
app.run(debug=True, port=8053)
```

**Features**:
- Full interactivity (filters, sorts, search, views)
- Responsive design (mobile/tablet/desktop)
- Keyboard shortcuts
- Export functionality (CSV, JSON)
- Panel details modal
- Help documentation
- Toast notifications
- Performance monitoring

**Enhancements over HTML viewer**:
1. Dynamic layout controls (ncol, nrow, arrangement)
2. Label configuration UI
3. Performance optimization with loading states
4. Comprehensive keyboard navigation
5. Enhanced export (CSV + JSON)
6. User-friendly error handling
7. Mobile-responsive design
8. In-app help documentation

## Current Implementation Status

**Phase 1**: Core infrastructure - ✅ COMPLETE
- Display class with fluent API
- Meta variable type system (8 types)
- DataFrame type inference
- JSON serialization with 1-based factor conversion

**Phase 2**: Panel rendering - ✅ COMPLETE
- File-based static panels working
- REST API panels working
- Matplotlib adapter (PNG/JPEG/SVG/PDF)
- Plotly adapter (interactive HTML)
- PanelManager with error resilience

**Phase 3**: Viewer integration - ✅ COMPLETE
- HTML viewer generation (trelliscopejs-lib)
- Dash viewer with full feature set
- Multiple display support
- Static export utilities

**Phase 4**: Dash viewer enhancements - ✅ COMPLETE
- Dynamic layout controls
- Label configuration
- Performance optimization
- Keyboard navigation
- Export & share
- Error handling & notifications
- Responsive design
- Help documentation

**Future Enhancements** (Planned):
- Parallel panel rendering
- Panel caching
- Large dataset optimization (100k+ panels)
- Virtual scrolling for massive displays
- Real-time collaboration
