# API Reference

Complete API documentation for py-trelliscope.

## Table of Contents

- [Display Class](#display-class)
- [Meta Variable Classes](#meta-variable-classes)
  - [FactorMeta](#factormeta)
  - [NumberMeta](#numbermeta)
  - [CurrencyMeta](#currencymeta)
  - [DateMeta](#datemeta)
  - [TimeMeta](#timemeta)
  - [HrefMeta](#hrefmeta)
  - [GraphMeta](#graphmeta)
  - [BaseMeta](#basemeta)
- [Inference Functions](#inference-functions)
- [Serialization Functions](#serialization-functions)
- [Validation Functions](#validation-functions)

---

## Display Class

The main class for creating and configuring trelliscope displays.

### Constructor

```python
Display(
    data: pd.DataFrame,
    name: str,
    description: str = "",
    path: Union[str, Path] = Path.cwd()
)
```

**Parameters:**

- `data` (pd.DataFrame): DataFrame containing panel data and metadata columns
- `name` (str): Name of the display (used for directory name)
- `description` (str, optional): Human-readable description of the display. Default: ""
- `path` (Union[str, Path], optional): Base path where display will be written. Default: current working directory

**Returns:** Display instance

**Example:**

```python
from trelliscope import Display
import pandas as pd

df = pd.DataFrame({'panel': ['p1', 'p2'], 'value': [10, 20]})
display = Display(df, name="my_display", description="Example display")
```

---

### Properties

#### `data`

```python
@property
data -> pd.DataFrame
```

Access the underlying DataFrame.

**Returns:** pd.DataFrame

---

#### `name`

```python
@property
name -> str
```

Get the display name.

**Returns:** str - Display name

---

#### `description`

```python
@property
description -> str
```

Get the display description.

**Returns:** str - Display description

---

#### `path`

```python
@property
path -> Path
```

Get the base output path.

**Returns:** Path - Base path for display output

---

#### `panel_column`

```python
@property
panel_column -> Optional[str]
```

Get the panel column name.

**Returns:** Optional[str] - Column name containing panel identifiers, or None if not set

---

#### `keysig`

```python
@property
keysig -> str
```

Get the unique key signature for this display.

The key signature is an MD5 hash computed from:
- Display name
- DataFrame shape (rows, columns)
- Column names
- Sample of first and last rows

**Returns:** str - 32-character hex MD5 hash

**Example:**

```python
print(display.keysig)  # '5f4dcc3b5aa765d61d8327deb882cf99'
```

---

### Configuration Methods

#### `set_panel_column()`

```python
set_panel_column(column: str) -> Display
```

Specify which column contains panel identifiers.

**Parameters:**

- `column` (str): Name of the column containing panel IDs

**Returns:** Display (self, for method chaining)

**Raises:**

- `ValueError`: If column is not found in DataFrame

**Example:**

```python
display.set_panel_column('plot_id')
```

---

#### `infer_metas()`

```python
infer_metas(columns: Optional[List[str]] = None) -> Display
```

Automatically infer meta variable types from DataFrame columns.

**Parameters:**

- `columns` (Optional[List[str]]): Specific columns to infer. If None, infers all columns. Default: None

**Returns:** Display (self, for method chaining)

**Inference Rules:**

- `pd.CategoricalDtype` or object → FactorMeta
- Numeric (int, float) → NumberMeta
- `datetime64` without time component → DateMeta
- `datetime64` with time or timezone → TimeMeta
- Boolean → BaseMeta
- Other types → BaseMeta

**Example:**

```python
# Infer all columns
display.infer_metas()

# Infer specific columns
display.infer_metas(columns=['category', 'score'])
```

---

#### `add_meta_def()`

```python
add_meta_def(
    varname: str,
    meta_type: str,
    replace: bool = False,
    **kwargs
) -> Display
```

Add or update a meta variable definition explicitly.

**Parameters:**

- `varname` (str): Column name in DataFrame
- `meta_type` (str): Meta variable type ('factor', 'number', 'currency', 'date', 'time', 'href', 'graph', 'base')
- `replace` (bool): If True, replace existing meta definition. Default: False
- `**kwargs`: Type-specific parameters (see individual meta classes)

**Returns:** Display (self, for method chaining)

**Raises:**

- `ValueError`: If varname not in DataFrame, if meta already exists and replace=False, or if meta_type is invalid

**Example:**

```python
display.add_meta_def('category', 'factor', levels=['A', 'B', 'C'])
display.add_meta_def('price', 'currency', code='USD', digits=2)
display.add_meta_def('measurement', 'number', digits=3, replace=True)
```

---

#### `set_default_layout()`

```python
set_default_layout(
    ncol: int = 4,
    nrow: Optional[int] = None,
    arrangement: str = "row"
) -> Display
```

Configure the default grid layout for panels.

**Parameters:**

- `ncol` (int): Number of columns in the grid. Default: 4
- `nrow` (Optional[int]): Number of rows in the grid. If None, auto-calculated. Default: None
- `arrangement` (str): Panel arrangement order ('row' or 'col'). Default: 'row'

**Returns:** Display (self, for method chaining)

**Example:**

```python
display.set_default_layout(ncol=3, nrow=2, arrangement='row')
```

---

#### `set_panel_options()`

```python
set_panel_options(
    width: Optional[int] = None,
    height: Optional[int] = None
) -> Display
```

Set dimensions for panel rendering.

**Parameters:**

- `width` (Optional[int]): Panel width in pixels
- `height` (Optional[int]): Panel height in pixels

**Returns:** Display (self, for method chaining)

**Example:**

```python
display.set_panel_options(width=800, height=600)
```

---

#### `set_default_labels()`

```python
set_default_labels(labels: List[str]) -> Display
```

Set which metadata columns are visible as labels.

**Parameters:**

- `labels` (List[str]): List of metadata column names to show as labels

**Returns:** Display (self, for method chaining)

**Raises:**

- `ValueError`: If any label not in DataFrame columns

**Example:**

```python
display.set_default_labels(['category', 'score', 'date'])
```

---

### Query Methods

#### `list_meta_variables()`

```python
list_meta_variables() -> List[str]
```

Get list of all metadata variable names.

**Returns:** List[str] - Sorted list of meta variable names

**Example:**

```python
metas = display.list_meta_variables()
print(metas)  # ['category', 'score', 'value']
```

---

#### `get_meta_variable()`

```python
get_meta_variable(name: str) -> BaseMeta
```

Retrieve a specific meta variable by name.

**Parameters:**

- `name` (str): Name of the meta variable

**Returns:** BaseMeta (or subclass) - The meta variable instance

**Raises:**

- `KeyError`: If meta variable not found

**Example:**

```python
score_meta = display.get_meta_variable('score')
print(f"Type: {score_meta.type}, Digits: {score_meta.digits}")
```

---

### Output Methods

#### `write()`

```python
write(
    output_path: Optional[Union[str, Path]] = None,
    force: bool = False
) -> Path
```

Write display to disk as JSON specification.

Creates directory with:
- `displayInfo.json` - Display configuration and metadata definitions
- `metadata.csv` - Cognostics (metadata values) for each panel

**Parameters:**

- `output_path` (Optional[Union[str, Path]]): Output directory path. If None, uses `{path}/{name}`. Default: None
- `force` (bool): If True, overwrite existing directory. If False, raise error if exists. Default: False

**Returns:** Path - Absolute path to created display directory

**Raises:**

- `ValueError`: If panel_column not set, or if directory exists and force=False

**Example:**

```python
# Write to default location
output = display.write()

# Write to specific location
output = display.write(output_path='/path/to/output')

# Overwrite existing
output = display.write(force=True)
```

---

## Meta Variable Classes

All meta variable classes inherit from `BaseMeta` and use the `@attrs.define` decorator.

### FactorMeta

Categorical metadata with defined levels.

```python
@attrs.define
class FactorMeta(BaseMeta):
    type: str = "factor"
    levels: Optional[List[str]] = None
```

**Attributes:**

- `varname` (str): Variable name (inherited from BaseMeta)
- `type` (str): Always "factor"
- `levels` (Optional[List[str]]): Ordered list of factor levels. If None, inferred from data

**Example:**

```python
from trelliscope import FactorMeta

meta = FactorMeta(varname="category", levels=["A", "B", "C", "D"])

# Via Display
display.add_meta_def("category", "factor", levels=["A", "B", "C"])
```

---

### NumberMeta

Numeric continuous metadata.

```python
@attrs.define
class NumberMeta(BaseMeta):
    type: str = "number"
    digits: int = 2
    log: bool = False
```

**Attributes:**

- `varname` (str): Variable name
- `type` (str): Always "number"
- `digits` (int): Number of decimal places to display. Default: 2
- `log` (bool): Whether to use log scale. Default: False

**Example:**

```python
from trelliscope import NumberMeta

meta = NumberMeta(varname="score", digits=3, log=False)

# Via Display
display.add_meta_def("score", "number", digits=3, log=False)
```

---

### CurrencyMeta

Monetary value metadata.

```python
@attrs.define
class CurrencyMeta(BaseMeta):
    type: str = "currency"
    code: str = "USD"
    digits: int = 2
```

**Attributes:**

- `varname` (str): Variable name
- `type` (str): Always "currency"
- `code` (str): ISO 4217 currency code. Default: "USD"
- `digits` (int): Number of decimal places. Default: 2

**Example:**

```python
from trelliscope import CurrencyMeta

meta = CurrencyMeta(varname="price", code="EUR", digits=2)

# Via Display
display.add_meta_def("price", "currency", code="EUR", digits=2)
```

---

### DateMeta

Date metadata (without time component).

```python
@attrs.define
class DateMeta(BaseMeta):
    type: str = "date"
    format: str = "%Y-%m-%d"
```

**Attributes:**

- `varname` (str): Variable name
- `type` (str): Always "date"
- `format` (str): strftime format string. Default: "%Y-%m-%d"

**Example:**

```python
from trelliscope import DateMeta

meta = DateMeta(varname="birth_date", format="%m/%d/%Y")

# Via Display
display.add_meta_def("birth_date", "date", format="%m/%d/%Y")
```

---

### TimeMeta

Datetime metadata with time and optional timezone.

```python
@attrs.define
class TimeMeta(BaseMeta):
    type: str = "time"
    timezone: Optional[str] = None
```

**Attributes:**

- `varname` (str): Variable name
- `type` (str): Always "time"
- `timezone` (Optional[str]): IANA timezone name (e.g., "UTC", "America/New_York"). Default: None

**Example:**

```python
from trelliscope import TimeMeta

meta = TimeMeta(varname="timestamp", timezone="UTC")

# Via Display
display.add_meta_def("timestamp", "time", timezone="America/Chicago")
```

---

### HrefMeta

Hyperlink metadata.

```python
@attrs.define
class HrefMeta(BaseMeta):
    type: str = "href"
    label_col: Optional[str] = None
```

**Attributes:**

- `varname` (str): Variable name (contains URL)
- `type` (str): Always "href"
- `label_col` (Optional[str]): Column name containing link text labels. Default: None

**Example:**

```python
from trelliscope import HrefMeta

meta = HrefMeta(varname="url", label_col="link_text")

# Via Display
display.add_meta_def("url", "href", label_col="link_text")
```

---

### GraphMeta

Sparkline or small visualization metadata.

```python
@attrs.define
class GraphMeta(BaseMeta):
    type: str = "graph"
    idvarname: Optional[str] = None
    direction: str = "x"
```

**Attributes:**

- `varname` (str): Variable name
- `type` (str): Always "graph"
- `idvarname` (Optional[str]): ID variable for graph data. Default: None
- `direction` (str): Graph orientation ('x' or 'y'). Default: 'x'

**Example:**

```python
from trelliscope import GraphMeta

meta = GraphMeta(varname="trend", direction="y", idvarname="month")

# Via Display
display.add_meta_def("trend", "graph", direction="y", idvarname="month")
```

---

### BaseMeta

Generic metadata for types not covered by specific classes.

```python
@attrs.define
class BaseMeta:
    varname: str
    type: str = "base"
```

**Attributes:**

- `varname` (str): Variable name
- `type` (str): Always "base"

**Example:**

```python
from trelliscope import BaseMeta

meta = BaseMeta(varname="flag")

# Via Display
display.add_meta_def("flag", "base")
```

---

## Inference Functions

Functions for automatic type inference from pandas DataFrames.

### `infer_meta_type()`

```python
def infer_meta_type(
    series: pd.Series,
    varname: str
) -> BaseMeta
```

Infer meta variable type from a pandas Series.

**Parameters:**

- `series` (pd.Series): Data column to infer from
- `varname` (str): Variable name

**Returns:** BaseMeta (or subclass) - Inferred meta variable

**Inference Logic:**

```python
if pd.CategoricalDtype:
    return FactorMeta(levels from categories)
elif is_datetime64_dtype:
    if has_time_component or has_timezone:
        return TimeMeta(timezone if present)
    else:
        return DateMeta()
elif is_numeric_dtype:
    return NumberMeta()
else:
    return BaseMeta()
```

**Example:**

```python
from trelliscope.inference import infer_meta_type

meta = infer_meta_type(df['score'], 'score')
print(f"Inferred type: {meta.type}")
```

---

### `infer_metas_from_dataframe()`

```python
def infer_metas_from_dataframe(
    df: pd.DataFrame,
    columns: Optional[List[str]] = None
) -> Dict[str, BaseMeta]
```

Infer meta variables for multiple DataFrame columns.

**Parameters:**

- `df` (pd.DataFrame): DataFrame to infer from
- `columns` (Optional[List[str]]): Specific columns to infer. If None, infers all. Default: None

**Returns:** Dict[str, BaseMeta] - Dictionary mapping column names to meta variables

**Example:**

```python
from trelliscope.inference import infer_metas_from_dataframe

metas = infer_metas_from_dataframe(df, columns=['category', 'score'])
for name, meta in metas.items():
    print(f"{name}: {meta.type}")
```

---

## Serialization Functions

Functions for converting Display objects to JSON.

### `serialize_display_info()`

```python
def serialize_display_info(display: Display) -> Dict[str, Any]
```

Serialize Display to displayInfo.json format.

**Parameters:**

- `display` (Display): Display instance to serialize

**Returns:** Dict[str, Any] - Dictionary in displayInfo.json schema format

**Output Structure:**

```python
{
    "name": str,
    "description": str,
    "keysig": str,
    "metas": List[Dict],
    "state": {
        "layout": Dict,
        "labels": List[str],
        "sort": List,
        "filter": List
    },
    "views": List,
    "panelInterface": {
        "type": "panel_local",
        "panelCol": str,
        "width": int,
        "height": int
    }
}
```

**Example:**

```python
from trelliscope.serialization import serialize_display_info

info = serialize_display_info(display)
print(info['name'])
print(f"Metas: {len(info['metas'])}")
```

---

### `write_display_info()`

```python
def write_display_info(
    display: Display,
    output_path: Path
) -> Path
```

Write displayInfo.json file for Display.

**Parameters:**

- `display` (Display): Display to serialize
- `output_path` (Path): Directory to write displayInfo.json

**Returns:** Path - Path to created displayInfo.json file

**Example:**

```python
from trelliscope.serialization import write_display_info
from pathlib import Path

json_path = write_display_info(display, Path('/path/to/output'))
print(f"Written to: {json_path}")
```

---

### `serialize_to_json_string()`

```python
def serialize_to_json_string(
    display: Display,
    indent: int = 2
) -> str
```

Serialize Display to JSON string.

**Parameters:**

- `display` (Display): Display to serialize
- `indent` (int): JSON indentation level. Default: 2

**Returns:** str - JSON string representation

**Example:**

```python
from trelliscope.serialization import serialize_to_json_string

json_str = serialize_to_json_string(display, indent=4)
print(json_str[:100])  # First 100 characters
```

---

### `validate_display_info()`

```python
def validate_display_info(info: Dict[str, Any]) -> List[str]
```

Validate displayInfo dictionary structure.

**Parameters:**

- `info` (Dict[str, Any]): displayInfo dictionary to validate

**Returns:** List[str] - List of error messages (empty if valid)

**Example:**

```python
from trelliscope.serialization import validate_display_info

errors = validate_display_info(info_dict)
if errors:
    print(f"Validation errors: {errors}")
else:
    print("Valid!")
```

---

## Validation Functions

Functions for validating Display configuration.

### `validate_display_name()`

```python
def validate_display_name(name: str) -> None
```

Validate display name format.

**Parameters:**

- `name` (str): Display name to validate

**Raises:**

- `ValueError`: If name is empty, contains invalid characters, or starts with invalid character

**Rules:**

- Must not be empty
- Must start with letter or underscore
- Can contain letters, numbers, underscores, hyphens
- Cannot contain spaces or special characters

**Example:**

```python
from trelliscope.validation import validate_display_name

validate_display_name("my_display_123")  # OK
validate_display_name("123_display")     # Raises ValueError
```

---

### `validate_panel_column()`

```python
def validate_panel_column(
    df: pd.DataFrame,
    column: str
) -> None
```

Validate that panel column exists in DataFrame.

**Parameters:**

- `df` (pd.DataFrame): DataFrame to check
- `column` (str): Column name to validate

**Raises:**

- `ValueError`: If column not found in DataFrame

**Example:**

```python
from trelliscope.validation import validate_panel_column

validate_panel_column(df, 'panel_id')
```

---

### `validate_meta_type()`

```python
def validate_meta_type(meta_type: str) -> None
```

Validate meta variable type string.

**Parameters:**

- `meta_type` (str): Type to validate

**Raises:**

- `ValueError`: If meta_type not in valid types

**Valid Types:**

- `'factor'`, `'number'`, `'currency'`, `'date'`, `'time'`, `'href'`, `'graph'`, `'base'`

**Example:**

```python
from trelliscope.validation import validate_meta_type

validate_meta_type('number')     # OK
validate_meta_type('invalid')    # Raises ValueError
```

---

## Complete Example

Putting it all together:

```python
import pandas as pd
from pathlib import Path
from trelliscope import Display

# Create data
df = pd.DataFrame({
    'panel_id': [f'plot_{i}' for i in range(1, 101)],
    'category': pd.Categorical(['A', 'B', 'C', 'D'] * 25),
    'score': np.random.uniform(50, 100, 100),
    'date': pd.date_range('2024-01-01', periods=100),
    'sales': np.random.uniform(1000, 50000, 100),
    'url': [f'https://example.com/item/{i}' for i in range(1, 101)]
})

# Create and configure display
display = (
    Display(
        df,
        name="sales_analysis",
        description="Q1 2024 Sales Performance",
        path=Path('./displays')
    )
    .set_panel_column('panel_id')
    .infer_metas(columns=['category', 'score', 'date'])  # Infer some
    .add_meta_def('sales', 'currency', code='USD', digits=2)  # Define others
    .add_meta_def('url', 'href')
    .set_default_layout(ncol=5, nrow=4, arrangement='row')
    .set_panel_options(width=600, height=400)
    .set_default_labels(['category', 'score', 'sales'])
)

# Write to disk
output = display.write()
print(f"Display written to: {output}")
print(f"Metas: {display.list_meta_variables()}")

# Inspect a meta
sales_meta = display.get_meta_variable('sales')
print(f"Sales: {sales_meta.type}, {sales_meta.code}, {sales_meta.digits} digits")
```

---

## Type Hints

py-trelliscope uses type hints throughout. Common types:

```python
from typing import Optional, List, Dict, Any, Union
from pathlib import Path
import pandas as pd

# Common function signatures
def function(
    df: pd.DataFrame,
    columns: Optional[List[str]] = None,
    options: Dict[str, Any] = None
) -> Union[str, Path]:
    pass
```

---

## Error Handling

All functions raise descriptive errors:

- `ValueError` - Invalid parameters or configuration
- `KeyError` - Requested resource not found
- `TypeError` - Wrong parameter type

Always wrap I/O operations in try-except:

```python
try:
    output = display.write()
except ValueError as e:
    print(f"Configuration error: {e}")
except Exception as e:
    print(f"Unexpected error: {e}")
```
