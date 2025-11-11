# Architecture Guide

## Overview

This document explains the design philosophy, architecture decisions, and implementation details of py-trelliscope.

## Table of Contents

1. [Design Philosophy](#design-philosophy)
2. [3-Tier Hybrid Architecture](#3-tier-hybrid-architecture)
3. [Core Components](#core-components)
4. [Data Flow](#data-flow)
5. [Type System](#type-system)
6. [JSON Specification](#json-specification)
7. [Key Design Decisions](#key-design-decisions)
8. [Performance Considerations](#performance-considerations)
9. [Testing Strategy](#testing-strategy)
10. [Future Architecture](#future-architecture)

---

## Design Philosophy

### Core Principles

1. **Separation of Concerns**: Python handles data processing, JavaScript handles visualization
2. **Declarative API**: Users describe what they want, not how to achieve it
3. **Type Safety**: Leverage Python type hints and attrs for validation
4. **Fluent Interface**: Method chaining for intuitive configuration
5. **Standard Output**: JSON specification enables platform independence
6. **Fail Fast**: Validate early and provide clear error messages

### Architecture Goals

- **Scalability**: Handle 1 to 1,000,000+ panels
- **Flexibility**: Support diverse visualization types
- **Maintainability**: Clean abstractions and comprehensive tests
- **Interoperability**: Compatible with R trelliscope ecosystem
- **Extensibility**: Easy to add new meta types and features

---

## 3-Tier Hybrid Architecture

py-trelliscope uses a hybrid architecture that bridges Python and JavaScript:

```
┌─────────────────────────────────────────────────────────────┐
│                     User's Python Code                       │
│  (Data preparation, analysis, display configuration)        │
└───────────────────────────┬─────────────────────────────────┘
                            │
                            ▼
┌─────────────────────────────────────────────────────────────┐
│                   py-trelliscope Library                     │
│                                                              │
│  ┌────────────┐  ┌─────────────┐  ┌──────────────┐        │
│  │  Display   │  │    Meta     │  │  Inference   │        │
│  │   Class    │  │  Variables  │  │   Engine     │        │
│  └────────────┘  └─────────────┘  └──────────────┘        │
│                                                              │
│  ┌────────────┐  ┌─────────────┐  ┌──────────────┐        │
│  │Validation  │  │Serialization│  │  Key Sig     │        │
│  └────────────┘  └─────────────┘  └──────────────┘        │
└───────────────────────────┬─────────────────────────────────┘
                            │
                            ▼
┌─────────────────────────────────────────────────────────────┐
│                     JSON Specification                       │
│                                                              │
│  displayInfo.json  ←  Schema defined by trelliscopejs-lib   │
│  metadata.csv      ←  Cognostics data                       │
└───────────────────────────┬─────────────────────────────────┘
                            │
                            ▼
┌─────────────────────────────────────────────────────────────┐
│                   JavaScript Viewer                          │
│                  (trelliscopejs-lib)                         │
│  (Interactive filtering, sorting, viewing)                   │
└─────────────────────────────────────────────────────────────┘
```

### Why This Architecture?

**Benefits:**

1. **Language Strengths**: Python for data processing, JavaScript for interaction
2. **Platform Independence**: JSON is universally compatible
3. **Decoupled Development**: Backend and frontend can evolve independently
4. **Browser Deployment**: Viewers run in any modern browser
5. **Ecosystem Integration**: Works with R trelliscope, Julia, etc.

**Trade-offs:**

1. **Two Codebases**: Requires coordination with JavaScript viewer
2. **Schema Maintenance**: JSON schema must stay synchronized
3. **Limited Python Viewing**: Cannot view directly in Python (by design)

---

## Core Components

### 1. Display Class

**Purpose**: Central orchestrator for creating trelliscope displays

**Responsibilities:**

- Hold DataFrame reference and configuration
- Manage meta variable definitions
- Coordinate validation, inference, and serialization
- Write output to disk

**Design Pattern**: Builder pattern with method chaining

```python
class Display:
    """
    Attributes:
        _data: DataFrame with panel data
        _name: Display name
        _description: Display description
        _path: Base output path
        _panel_column: Column containing panel IDs
        _meta_vars: Dict of meta variable definitions
        _panel_options: Panel rendering options
        _state: Display state (layout, labels, sorts, filters)
        _views: List of saved views
        _keysig: Unique display signature
    """
```

**Key Methods:**

- Configuration: `set_panel_column()`, `set_default_layout()`, etc.
- Meta Management: `add_meta_def()`, `infer_metas()`, `get_meta_variable()`
- Output: `write()`

### 2. Meta Variable System

**Purpose**: Type-safe representation of metadata with display semantics

**Class Hierarchy:**

```
BaseMeta (base class)
├── FactorMeta      (categorical)
├── NumberMeta      (numeric)
├── CurrencyMeta    (monetary)
├── DateMeta        (date only)
├── TimeMeta        (datetime)
├── HrefMeta        (links)
└── GraphMeta       (sparklines)
```

**Design Pattern**: Strategy pattern for type-specific behavior

**Implementation**: Uses `@attrs.define` for:

- Automatic `__init__`, `__repr__`, `__eq__`
- Type validation
- Immutability (if needed)
- Dictionary conversion (`attrs.asdict()`)

**Example:**

```python
@attrs.define
class NumberMeta(BaseMeta):
    type: str = "number"
    digits: int = 2
    log: bool = False

    def to_dict(self) -> Dict[str, Any]:
        """Convert to JSON-serializable dict."""
        return {
            "varname": self.varname,
            "type": self.type,
            "digits": self.digits,
            "log": self.log
        }
```

### 3. Inference Engine

**Purpose**: Automatically detect appropriate meta types from pandas dtypes

**Location**: `trelliscope/inference.py`

**Inference Rules:**

```python
def infer_meta_type(series: pd.Series, varname: str) -> BaseMeta:
    """
    Inference decision tree:

    1. CategoricalDtype → FactorMeta (extract levels)
    2. datetime64:
       a. Has time or timezone → TimeMeta
       b. Date only → DateMeta
    3. Numeric (int, float) → NumberMeta
    4. Boolean → BaseMeta
    5. Default → BaseMeta
    """
```

**Design Consideration**: Conservative inference

- Only infer types we're confident about
- Allow explicit override with `add_meta_def(..., replace=True)`
- Preserve original data types in metadata.csv

### 4. Serialization Layer

**Purpose**: Convert Display objects to JSON specification

**Location**: `trelliscope/serialization.py`

**Key Functions:**

- `serialize_display_info()`: Display → Dict
- `write_display_info()`: Dict → JSON file
- `validate_display_info()`: Verify schema compliance

**Schema Compliance**: Matches trelliscopejs-lib TypeScript interfaces

```typescript
// Target schema (TypeScript)
interface DisplayInfo {
  name: string;
  description: string;
  keysig: string;
  metas: Meta[];
  state: DisplayState;
  views: View[];
  panelInterface?: PanelInterface;
}
```

### 5. Validation System

**Purpose**: Ensure configuration is valid before execution

**Location**: `trelliscope/validation.py`

**Validation Layers:**

1. **Constructor Validation**: Immediate checks on object creation
2. **Method Validation**: Checks within setter methods
3. **Pre-Write Validation**: Comprehensive validation before `write()`
4. **Schema Validation**: Verify JSON output matches spec

**Error Handling Philosophy**: Fail fast with descriptive messages

```python
# Good error message
"panel_column must be set before writing. "
"Use set_panel_column() to specify which column contains panels."

# Bad error message
"Invalid configuration"
```

### 6. Key Signature Generation

**Purpose**: Create unique, stable identifier for display

**Implementation**: MD5 hash of:

- Display name
- DataFrame shape (rows, cols)
- Column names (sorted)
- Sample rows (first 3, last 3)

**Use Cases:**

- Detect display changes
- Cache invalidation
- Version tracking

```python
def _generate_keysig(self) -> str:
    """Generate MD5 hash from display characteristics."""
    components = [
        self.name,
        str(self._data.shape),
        ",".join(sorted(self._data.columns)),
        str(self._data.head(3).values.tolist()),
        str(self._data.tail(3).values.tolist())
    ]
    content = "|".join(components)
    return hashlib.md5(content.encode('utf-8')).hexdigest()
```

---

## Data Flow

### Creating a Display

```
User DataFrame
     │
     ▼
Display Constructor
     │
     ├──► Validate name
     ├──► Store DataFrame reference
     ├──► Initialize empty meta_vars dict
     ├──► Set default state/options
     └──► Generate keysig
     │
     ▼
Configuration Methods (chainable)
     │
     ├──► set_panel_column()
     │         └──► Validate column exists
     │
     ├──► infer_metas()
     │         ├──► For each column:
     │         │      └──► infer_meta_type()
     │         └──► Store in _meta_vars
     │
     ├──► add_meta_def()
     │         ├──► Validate meta type
     │         ├──► Create meta instance
     │         └──► Store in _meta_vars
     │
     └──► set_default_layout() / set_panel_options() / etc.
     │
     ▼
write() Method
     │
     ├──► Validate panel_column set
     ├──► Determine output path
     ├──► Check directory existence
     ├──► Create directory
     │
     ├──► Write displayInfo.json
     │         ├──► serialize_display_info()
     │         ├──► validate_display_info()
     │         └──► json.dump()
     │
     └──► Write metadata.csv
               └──► Extract non-panel columns
               └──► DataFrame.to_csv()
```

### Reading by JavaScript Viewer

```
Display Directory
     │
     ├──► displayInfo.json
     │         ├──► Load JSON
     │         ├──► Parse meta definitions
     │         ├──► Configure UI controls
     │         └──► Set layout
     │
     └──► metadata.csv
               ├──► Load CSV
               ├──► Map to meta types
               └──► Populate panel grid
```

---

## Type System

### Meta Variable Type System

py-trelliscope defines 8 meta variable types, each with specific display semantics:

| Type | Python Concept | Display Semantics | Example |
|------|---------------|-------------------|---------|
| `factor` | Categorical | Discrete filter, color coding | Product category |
| `number` | Numeric | Range filter, sorting | Temperature |
| `currency` | Monetary | Formatted with symbol | Price |
| `date` | Date only | Calendar filter | Birth date |
| `time` | Datetime | Timeline filter | Timestamp |
| `href` | URL | Clickable link | Documentation URL |
| `graph` | Array of numbers | Sparkline visualization | Trend data |
| `base` | Generic | Basic display | Any other type |

### Type Mapping Strategy

**From pandas dtype to meta type:**

```
pandas.CategoricalDtype    → FactorMeta
pd.Int64Dtype              → NumberMeta
pd.Float64Dtype            → NumberMeta
datetime64[ns]             → DateMeta (if date-only)
datetime64[ns]             → TimeMeta (if has time)
datetime64[ns, tz]         → TimeMeta (with timezone)
object (string)            → BaseMeta (default)
bool                       → BaseMeta
```

**Design Decision**: Conservative inference

- Only infer specific types when confident
- Allow users to override with explicit definitions
- Preserve original data in CSV

### Type Extensions

Adding new meta types requires:

1. Define new `@attrs.define` class inheriting from `BaseMeta`
2. Add to `META_TYPES` dict in `meta_variables.py`
3. Add inference logic in `inference.py` (if auto-detectable)
4. Add serialization in `to_dict()` method
5. Update tests and documentation

---

## JSON Specification

### Output Structure

py-trelliscope creates two files:

#### 1. displayInfo.json

**Purpose**: Display configuration and metadata definitions

**Schema**:

```json
{
  "name": "display_name",
  "description": "Human-readable description",
  "keysig": "md5_hash_32_chars",
  "metas": [
    {
      "varname": "column_name",
      "type": "meta_type",
      ... type-specific fields ...
    }
  ],
  "state": {
    "layout": {
      "ncol": 4,
      "nrow": 3,
      "arrangement": "row"
    },
    "labels": ["col1", "col2"],
    "sort": [],
    "filter": []
  },
  "views": [],
  "panelInterface": {
    "type": "panel_local",
    "panelCol": "panel_column_name",
    "width": 800,
    "height": 600
  }
}
```

#### 2. metadata.csv

**Purpose**: Actual cognostics data for each panel

**Structure**:

```csv
category,score,date,flag
A,85.5,2024-01-01,true
B,92.3,2024-01-02,false
C,78.9,2024-01-03,true
```

**Note**: Panel column is excluded (already in displayInfo.json)

### Schema Versioning

**Current Strategy**: Match trelliscopejs-lib v1.x schema

**Future Consideration**: Add schema version field for evolution

```json
{
  "schemaVersion": "1.0.0",
  "name": "display_name",
  ...
}
```

---

## Key Design Decisions

### 1. Why attrs Instead of dataclasses?

**Decision**: Use `@attrs.define` for meta variable classes

**Rationale**:

- More powerful validation
- Better default support
- Mature ecosystem
- Explicit control over equality, repr, etc.

**Alternative Considered**: Python dataclasses (built-in)

**Trade-off**: External dependency vs. functionality

### 2. Why Method Chaining?

**Decision**: Fluent API with method chaining

**Rationale**:

- Intuitive, readable code
- Common in modern Python libraries (pandas, polars)
- Self-documenting workflow

**Example**:

```python
# With chaining (chosen)
display = (
    Display(df, name="test")
    .set_panel_column('id')
    .infer_metas()
    .write()
)

# Without chaining (alternative)
display = Display(df, name="test")
display.set_panel_column('id')
display.infer_metas()
display.write()
```

### 3. Why Separate metadata.csv?

**Decision**: Split configuration (JSON) from data (CSV)

**Rationale**:

- CSV is universal, easily loaded in any tool
- Efficient for large datasets
- Clear separation of concerns
- Enables incremental loading

**Alternative Considered**: Embed all data in JSON

**Trade-off**: File count vs. format appropriateness

### 4. Why Conservative Type Inference?

**Decision**: Only infer types we're confident about

**Rationale**:

- Avoids incorrect assumptions
- Users can override explicitly
- Safer default behavior

**Example**:

```python
# String column → BaseMeta (not FactorMeta)
# Why? Might be free text, not categorical

# User can override:
.add_meta_def('category', 'factor')
```

### 5. Why Require panel_column?

**Decision**: Make `panel_column` mandatory before `write()`

**Rationale**:

- Every display needs panels
- Clear error message if forgotten
- Future: May support metadata-only displays

### 6. Why MD5 for keysig?

**Decision**: Use MD5 hash for display signatures

**Rationale**:

- Fast computation
- Fixed 32-character length
- Sufficient for uniqueness (not security-critical)
- Standard library support

**Alternative Considered**: SHA256 (overkill for this use case)

---

## Performance Considerations

### Memory Efficiency

**Strategy 1**: DataFrame references, not copies

```python
class Display:
    def __init__(self, data: pd.DataFrame, ...):
        self._data = data  # Reference, not copy
```

**Strategy 2**: Lazy keysig computation

```python
@property
def keysig(self) -> str:
    if self._keysig is None:
        self._keysig = self._generate_keysig()
    return self._keysig
```

### I/O Optimization

**Strategy 1**: Use pandas' optimized CSV writer

```python
metadata_df.to_csv(csv_path, index=False)  # Fast C implementation
```

**Strategy 2**: UTF-8 encoding without ASCII escaping

```python
json.dump(info, f, ensure_ascii=False)  # Preserves Unicode, smaller files
```

### Scalability Considerations

**Current Architecture**: Suitable for 1 - 100k panels

**For 100k - 1M panels**:

- Consider chunked metadata writing
- Add progress callbacks
- Implement incremental serialization

**For 1M+ panels**:

- Move to database backend (SQLite, Parquet)
- Implement lazy loading
- Add panel pagination

---

## Testing Strategy

### Test Organization

```
tests/
├── unit/                  # Fast, isolated tests
│   ├── test_display.py
│   ├── test_meta_variables.py
│   ├── test_inference.py
│   ├── test_serialization.py
│   └── test_validation.py
│
└── integration/           # End-to-end tests
    └── test_basic_workflow.py
```

### Test Coverage Goals

- **Unit Tests**: 95%+ coverage per module
- **Integration Tests**: Cover all major user workflows
- **Edge Cases**: Empty data, nulls, Unicode, large datasets

### Test Patterns

**1. Parametrized Tests**: Test multiple cases efficiently

```python
@pytest.mark.parametrize("meta_type,expected", [
    ("factor", FactorMeta),
    ("number", NumberMeta),
    ("currency", CurrencyMeta),
])
def test_add_meta_def_creates_correct_type(meta_type, expected):
    ...
```

**2. Temporary Directories**: Isolate file I/O tests

```python
def test_write():
    with tempfile.TemporaryDirectory() as tmpdir:
        output = display.write(output_path=tmpdir)
        assert output.exists()
```

**3. Fixtures**: Reuse common test data

```python
@pytest.fixture
def sample_dataframe():
    return pd.DataFrame({
        "panel": ["p1", "p2"],
        "value": [10, 20]
    })
```

### Continuous Integration

**Test Execution**:

- Run on every commit
- Test Python 3.8, 3.9, 3.10, 3.11
- Test on Linux, macOS, Windows

**Coverage Reporting**:

- Generate HTML reports
- Track coverage trends
- Require 90%+ coverage for PRs

---

## Future Architecture

### Phase 2: Panel Rendering

**Goal**: Add ability to render actual visualizations

**Architecture Addition**:

```python
class PanelRenderer:
    """Base class for panel rendering."""

    def render(self, data: Any, output_path: Path) -> Path:
        """Render panel and return path to image/HTML."""
        raise NotImplementedError

class MatplotlibRenderer(PanelRenderer):
    """Render panels with matplotlib."""
    pass

class PlotlyRenderer(PanelRenderer):
    """Render panels with plotly."""
    pass
```

**Integration**:

```python
display = (
    Display(df, name="viz")
    .set_panel_column('id')
    .set_panel_renderer(MatplotlibRenderer(figure_func=my_plot_func))
    .write()
)
```

### Phase 3: Viewer Integration

**Goal**: Launch JavaScript viewer from Python

**Architecture Addition**:

```python
class DisplayViewer:
    """Launch trelliscopejs viewer."""

    def view(self, display: Display, port: int = 8000):
        """Start local server and open browser."""
        # Start HTTP server
        # Open browser to localhost:8000
        # Serve displayInfo.json and metadata.csv
        pass
```

**Usage**:

```python
display.write()
display.view()  # Opens browser with interactive viewer
```

### Phase 4: Distributed Architecture

**Goal**: Handle massive datasets (1M+ panels)

**Architecture Change**: Database-backed storage

```
Python Backend
     ↓
PostgreSQL / SQLite / Parquet
     ↓
REST API
     ↓
JavaScript Viewer (with pagination)
```

**Benefits**:

- Incremental loading
- Efficient filtering/sorting
- Lower memory footprint

---

## Conclusion

py-trelliscope's architecture balances:

- **Simplicity**: Easy to understand and use
- **Flexibility**: Supports diverse use cases
- **Performance**: Handles typical datasets efficiently
- **Extensibility**: Easy to add features
- **Interoperability**: Compatible with existing ecosystem

The 3-tier hybrid design cleanly separates data processing (Python) from visualization (JavaScript), enabling each component to use the best tools for its purpose.

Future phases will add panel rendering and viewer integration while maintaining backward compatibility with the JSON specification.
