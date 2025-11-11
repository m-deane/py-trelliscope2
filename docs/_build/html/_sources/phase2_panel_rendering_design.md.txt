# Phase 2: Panel Rendering Architecture Design

## Overview

Phase 2 adds the ability to render actual visualizations (panels) from various sources and save them to disk for viewing.

## Current State (Phase 1)

Phase 1 provides:
- Display class with configuration
- Meta variable system
- JSON serialization (displayInfo.json, metadata.csv)
- `Display.write()` method that writes metadata

**What's Missing**: Actual panel file generation

## Phase 2 Goals

Add support for:
1. Multiple visualization libraries (matplotlib, plotly, altair)
2. Different panel types (images, HTML, URLs)
3. Lazy evaluation (callables for expensive plots)
4. Performance optimization (parallel rendering, caching)

## Architecture

### 1. Adapter Pattern for Panel Types

```
┌─────────────────────────────────────────┐
│          PanelRenderer (ABC)            │
│  - detect(obj) -> bool                  │
│  - save(obj, path, **kwargs) -> Path    │
│  - get_interface_type() -> str          │
└─────────────────────────────────────────┘
                    △
                    │
        ┌───────────┼───────────┬──────────────┐
        │           │           │              │
┌───────────┐ ┌──────────┐ ┌─────────┐ ┌────────────┐
│Matplotlib │ │ Plotly   │ │ Altair  │ │   Image    │
│ Adapter   │ │ Adapter  │ │ Adapter │ │  Adapter   │
│ (PNG)     │ │ (HTML)   │ │ (HTML)  │ │ (copy)     │
└───────────┘ └──────────┘ └─────────┘ └────────────┘
```

### 2. Panel Sources

Panels can come from various sources:

| Source Type | Example | Handler |
|-------------|---------|---------|
| matplotlib Figure | `fig` | MatplotlibAdapter |
| plotly Figure | `go.Figure()` | PlotlyAdapter |
| altair Chart | `alt.Chart()` | AltairAdapter |
| File path | `"/path/to/img.png"` | FilePathHandler |
| URL | `"https://..."` | URLHandler |
| Callable | `lambda: create_plot()` | LazyPanelHandler |
| HTML string | `"<html>...</html>"` | HTMLHandler |

### 3. Panel Types in panelInterface

```json
{
  "panelInterface": {
    "type": "panel_local",  // or "panel_url", "iframe"
    "panelCol": "panel",
    "format": "png",        // or "html", "svg"
    "width": 800,
    "height": 600
  }
}
```

## Implementation Plan

### Step 1: Create Base Classes

**File**: `trelliscope/panels/__init__.py`

```python
from abc import ABC, abstractmethod
from pathlib import Path
from typing import Any, Dict, Optional

class PanelRenderer(ABC):
    """Base class for panel rendering adapters."""

    @abstractmethod
    def detect(self, obj: Any) -> bool:
        """Return True if this adapter can handle the object."""
        pass

    @abstractmethod
    def save(self, obj: Any, path: Path, **kwargs) -> Path:
        """Save the object to file and return the path."""
        pass

    @abstractmethod
    def get_interface_type(self) -> str:
        """Return the panelInterface type for this adapter."""
        pass

    @abstractmethod
    def get_format(self) -> str:
        """Return the file format/extension."""
        pass
```

### Step 2: Implement MatplotlibAdapter

**File**: `trelliscope/panels/matplotlib_adapter.py`

```python
from pathlib import Path
from typing import Any
from trelliscope.panels import PanelRenderer

class MatplotlibAdapter(PanelRenderer):
    """Adapter for matplotlib figures."""

    def __init__(self, format: str = "png", dpi: int = 100):
        self.format = format
        self.dpi = dpi

    def detect(self, obj: Any) -> bool:
        """Detect matplotlib Figure objects."""
        try:
            import matplotlib.figure
            return isinstance(obj, matplotlib.figure.Figure)
        except ImportError:
            return False

    def save(self, obj: Any, path: Path, **kwargs) -> Path:
        """Save matplotlib figure to file."""
        dpi = kwargs.get('dpi', self.dpi)
        format = kwargs.get('format', self.format)

        output_path = path.with_suffix(f'.{format}')
        obj.savefig(output_path, dpi=dpi, bbox_inches='tight')
        return output_path

    def get_interface_type(self) -> str:
        return "panel_local"

    def get_format(self) -> str:
        return self.format
```

### Step 3: Implement PlotlyAdapter

**File**: `trelliscope/panels/plotly_adapter.py`

```python
from pathlib import Path
from typing import Any
from trelliscope.panels import PanelRenderer

class PlotlyAdapter(PanelRenderer):
    """Adapter for plotly figures."""

    def __init__(self, format: str = "html"):
        self.format = format

    def detect(self, obj: Any) -> bool:
        """Detect plotly Figure objects."""
        try:
            import plotly.graph_objects as go
            return isinstance(obj, (go.Figure, dict))
        except ImportError:
            return False

    def save(self, obj: Any, path: Path, **kwargs) -> Path:
        """Save plotly figure to HTML."""
        import plotly.io as pio

        output_path = path.with_suffix('.html')
        pio.write_html(obj, output_path, include_plotlyjs='cdn')
        return output_path

    def get_interface_type(self) -> str:
        return "iframe"

    def get_format(self) -> str:
        return "html"
```

### Step 4: Create PanelManager

**File**: `trelliscope/panels/manager.py`

```python
from pathlib import Path
from typing import List, Any, Optional
from trelliscope.panels import PanelRenderer
from trelliscope.panels.matplotlib_adapter import MatplotlibAdapter
from trelliscope.panels.plotly_adapter import PlotlyAdapter

class PanelManager:
    """Manages panel rendering with multiple adapters."""

    def __init__(self):
        self.adapters: List[PanelRenderer] = [
            MatplotlibAdapter(),
            PlotlyAdapter(),
        ]

    def register_adapter(self, adapter: PanelRenderer):
        """Register a new adapter."""
        self.adapters.insert(0, adapter)

    def detect_adapter(self, obj: Any) -> Optional[PanelRenderer]:
        """Find adapter that can handle this object."""
        for adapter in self.adapters:
            if adapter.detect(obj):
                return adapter
        return None

    def save_panel(
        self,
        obj: Any,
        output_path: Path,
        panel_id: str,
        **kwargs
    ) -> Path:
        """Save panel using appropriate adapter."""
        # Handle callables (lazy evaluation)
        if callable(obj):
            obj = obj()

        # Find adapter
        adapter = self.detect_adapter(obj)
        if adapter is None:
            raise ValueError(
                f"No adapter found for panel type: {type(obj)}. "
                f"Supported types: matplotlib Figure, plotly Figure"
            )

        # Create panel path
        format = adapter.get_format()
        panel_path = output_path / f"{panel_id}.{format}"

        # Save panel
        return adapter.save(obj, panel_path, **kwargs)
```

### Step 5: Integrate with Display.write()

**Modifications to**: `trelliscope/display.py`

```python
def write(
    self,
    output_path: Optional[Union[str, Path]] = None,
    force: bool = False,
    render_panels: bool = True  # NEW
) -> Path:
    """Write display to disk."""

    # ... existing validation and setup ...

    # Write panel files if requested
    if render_panels and self.panel_column is not None:
        self._render_panels(output_path)

    # Write displayInfo.json
    write_display_info(self, output_path)

    # Write metadata.csv
    self._write_metadata_csv(output_path)

    return output_path

def _render_panels(self, output_path: Path) -> None:
    """Render all panels to files."""
    from trelliscope.panels.manager import PanelManager

    # Create panels directory
    panels_dir = output_path / "panels"
    panels_dir.mkdir(exist_ok=True)

    # Get panel manager
    manager = PanelManager()

    # Render each panel
    panel_col = self.panel_column
    for idx, row in self.data.iterrows():
        panel_obj = row[panel_col]
        panel_id = str(row[panel_col] if isinstance(row[panel_col], str) else idx)

        try:
            panel_path = manager.save_panel(
                panel_obj,
                panels_dir,
                panel_id
            )
            print(f"Rendered panel: {panel_path.name}")
        except Exception as e:
            print(f"Error rendering panel {panel_id}: {e}")
```

## Data Flow

```
DataFrame with panel column
         │
         ▼
Display.write(render_panels=True)
         │
         ▼
_render_panels()
         │
         ├──► For each row:
         │    ├──► Get panel object
         │    ├──► Check if callable → execute
         │    ├──► PanelManager.detect_adapter()
         │    ├──► adapter.save(obj, path)
         │    └──► Record panel filename
         │
         ▼
panels/ directory with saved files
```

## Phase 2 Prioritization

### MVP (Minimum Viable Product)
1. ✅ PanelRenderer base class
2. ✅ MatplotlibAdapter (PNG export)
3. ✅ PlotlyAdapter (HTML export)
4. ✅ PanelManager for adapter selection
5. ✅ Integration with Display.write()
6. ✅ Basic tests
7. ✅ Example notebook

### Nice-to-Have (Later)
- AltairAdapter
- Lazy evaluation (callables)
- Parallel rendering
- Panel caching
- Progress bars
- Error recovery

## Testing Strategy

### Unit Tests
```python
# tests/unit/test_matplotlib_adapter.py
def test_matplotlib_adapter_detect():
    """Test matplotlib figure detection."""
    fig, ax = plt.subplots()
    adapter = MatplotlibAdapter()
    assert adapter.detect(fig) is True

def test_matplotlib_adapter_save():
    """Test saving matplotlib figure."""
    fig, ax = plt.subplots()
    adapter = MatplotlibAdapter()
    path = adapter.save(fig, Path('/tmp/test'))
    assert path.exists()
```

### Integration Tests
```python
# tests/integration/test_panel_rendering.py
def test_render_matplotlib_panels():
    """Test full workflow with matplotlib."""
    df = pd.DataFrame({
        'panel': [create_fig() for _ in range(5)],
        'value': range(5)
    })

    display = (
        Display(df, name="test")
        .set_panel_column('panel')
        .write()
    )

    # Verify panels/ directory
    panels_dir = display / "panels"
    assert len(list(panels_dir.glob('*.png'))) == 5
```

## Migration from Phase 1

Phase 1 displays work without changes:
- If `render_panels=False`, behavior is identical to Phase 1
- Existing displays continue to work
- New functionality is opt-in

## Next Steps

1. Create `trelliscope/panels/` package structure
2. Implement base classes and adapters
3. Update Display.write() with panel rendering
4. Write comprehensive tests
5. Create example notebooks
6. Update documentation
