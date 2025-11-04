# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

## Project Overview

**py-trelliscope2** is a Python implementation of Trelliscope for creating interactive, scalable visualization displays. The project uses a 3-tier hybrid architecture where Python generates JSON specifications consumed by the existing trelliscopejs-lib (v0.7.16) JavaScript viewer.

**Key Architecture**: Python Backend → JSON Specification → JavaScript Viewer (React/Redux)

## Critical Discovery: File-Based Panel Requirements

**IMPORTANT**: The trelliscopejs-lib viewer requires THREE files for file-based static panels to function:

1. `displayInfo.json` - Full display configuration with embedded cogData
2. `metaData.json` - Separate cogData array file
3. **`metaData.js`** - JavaScript file with `window.metaData = [...]` wrapper

Even though cogData is embedded in displayInfo.json, metaData.js is MANDATORY. The viewer makes explicit requests for this file and won't load panels without it.

See `.claude_plans/FILE_BASED_PANELS_SOLUTION.md` for complete working structure.

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

# Run single test
pytest tests/unit/test_display.py::test_display_creation -v
```

### Viewer Testing

```bash
# Start HTTP server for examples
cd examples/output
python3 -m http.server 8000

# Start with specific port
python3 -m http.server 8001

# View displays at:
# http://localhost:8000/
# http://localhost:8000/test_static/  (clean test environment)
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

## Core Architecture

### Package Structure

```
trelliscope/
├── __init__.py              # Package exports
├── display.py               # Display class (main entry point)
├── meta.py                  # Meta variable type system
├── inference.py             # DataFrame type inference
├── serialization.py         # JSON writers for displayInfo.json
├── panel_interface.py       # Panel interface abstractions
├── config.py                # Configuration management
├── export.py                # Export utilities
├── server.py                # Development server
├── viewer.py                # Viewer integration
├── panels/                  # Panel rendering (matplotlib, plotly)
├── viewer/                  # Viewer assets and templates
├── utils/                   # Utility functions
├── core/                    # Core abstractions (empty)
├── integrations/            # Library integrations (empty)
├── server/                  # Server components (empty)
└── writers/                 # Additional writers (empty)
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
- File-based panels (static PNG/HTML)
- REST API panels (dynamic loading)
- WebSocket panels (streaming)

## Critical Implementation Details

### displayInfo.json Required Fields

For file-based panels to work with trelliscopejs-lib v0.7.16:

```python
{
  "name": str,
  "group": "common",           # Required
  "description": str,
  "keysig": str,
  "n": int,                    # Number of panels
  "height": 500,               # Required
  "width": 500,                # Required
  "tags": [],                  # Required (can be empty)
  "keycols": [],               # Required (can be empty)
  "metas": [...],              # Array of meta definitions
  "inputs": null,              # Required
  "cogInterface": {            # Required
    "name": str,
    "group": "common",
    "type": "JSON"
  },
  "cogInfo": {...},            # Required - detailed meta info
  "cogDistns": {},             # Required (can be empty object)
  "cogData": [...],            # Required - embedded data
  "state": {...},              # Layout, filters, sorts
  "views": [],                 # Saved views
  "primarypanel": "panel",     # Which meta is the panel
  "panelInterface": {          # Required
    "type": "file",
    "base": "panels",
    "panelCol": "panel"
  },
  "imgSrcLookup": {}           # Required (empty object)
}
```

### Panel File Naming

**Correct**: `0.png`, `1.png`, `2.png` (ID only)
**Wrong**: `panel_0.png`, `panel_1.png` (prefix not used)

Panel filenames must match `panelKey` values in cogData.

### metaData Files Structure

**metaData.json**:
```json
[
  {
    "id": 0,
    "value": 10,
    "category": "A",
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
    "category": "A",
    "panelKey": "0",
    "panel": "panels/0.png"   // Relative path
  }
];
```

Panel paths are RELATIVE: `"panels/0.png"`, not full URLs.

## Viewer Architectures

### Modern Viewer (trelliscopejs-lib v0.7.16)

**What we're targeting**:
- Pure JSON data format
- React/Redux frontend
- File-based OR REST API panels
- CDN: `https://unpkg.com/trelliscopejs-lib@0.7.16/dist/assets/`

### Old Viewer (trelliscopejs_widget v0.3.2)

**DO NOT USE** - R examples in `examples/output/r_example_static/` use this:
- JSONP format with callback wrappers
- htmlwidgets framework
- Incompatible with modern viewer
- Ignore for Python implementation

## Common Development Tasks

### Creating a Simple Display

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

If viewer shows "0 of 0":
1. Check `displayInfo.json` has all required fields
2. Verify `metaData.js` exists and is accessible
3. Confirm `metaData.json` exists
4. Check panel file naming (`0.png` not `panel_0.png`)
5. Verify panel paths in metaData are relative
6. Check browser DevTools Console for JavaScript errors
7. Check Network tab for 404 errors

## File Organization

### Safe to Modify
- `/trelliscope/` - Python package source
- `/tests/` - Test files
- `/examples/` - Example scripts and notebooks
- `/.claude_plans/` - Progress tracking and planning docs

### Never Modify
- `/reference/` - R package source (reference only)
- `/py-trelliscope/` - Virtual environment
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

## Testing Strategy

### Unit Tests
- Meta variable type inference
- DataFrame validation
- JSON serialization
- Panel interface abstractions

### Integration Tests
- End-to-end display creation
- Panel rendering (matplotlib, plotly)
- Viewer compatibility

### Manual Testing
- Browser-based viewer testing
- Panel image loading verification
- Interactive filtering/sorting

## Key Reference Files

**Always consult**:
- `.claude_plans/FILE_BASED_PANELS_SOLUTION.md` - Working panel structure
- `.claude/CLAUDE.md` - Project directives and patterns
- `README.md` - User-facing documentation

**Technical references**:
- `.claude_research/TRELLISCOPE_TECHNICAL_ANALYSIS.md` - Architecture details
- R source in `/reference/` - Behavior reference only

## Common Pitfalls

1. **Missing metaData.js**: Viewer requires this even with embedded cogData
2. **Wrong panel naming**: Use `0.png` not `panel_0.png`
3. **Full URLs in metaData**: Use relative paths `panels/0.png`
4. **Missing required fields**: displayInfo.json needs all fields listed above
5. **Using R examples**: Old JSONP format is incompatible
6. **Port conflicts**: macOS AirPlay uses port 5000, use 5001 or 8000+

## Workflow Guidelines

1. Write tests FIRST for new features
2. Run full test suite before committing
3. Update `.claude_plans/projectplan.md` after major changes
4. Clean up orphan files regularly
5. Use descriptive commit messages
6. Never commit mock/placeholder code

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
| factor | categorical | Categories with levels |
| number | numeric | Continuous values |
| currency | numeric | Monetary values |
| date | datetime | Dates without time |
| time | datetime | Dates with time |
| href | str | URLs/links |
| graph | any | Sparklines/mini-plots |
| base | any | Generic metadata |

## Performance Considerations

- Lazy panel generation for large datasets
- Streaming writes to avoid memory issues
- Parallel processing for panel rendering (future)
- Pagination in viewer (configurable page size)

## Current Status

**Phase 1**: Core infrastructure - COMPLETE
**Phase 2**: Panel rendering - IN PROGRESS
  - ✅ File-based static panels working
  - ✅ REST API panels working
  - ⏳ Metadata file generation
  - ⏳ Python API updates

**Phase 3**: Viewer integration - PLANNED
**Phase 4**: Advanced features - PLANNED
