# Phase 3: Viewer Integration Architecture Design

## Overview

Phase 3 adds the ability to view trelliscope displays interactively in a web browser using the trelliscopejs viewer.

## Current State (Phase 2)

Phase 2 provides:
- Display creation and configuration
- Panel rendering (matplotlib, plotly)
- JSON specification output (displayInfo.json, metadata.csv)
- Panel files in panels/ directory

**What's Missing**: Interactive viewing interface

## Phase 3 Goals

Add support for:
1. Development server for local viewing
2. `Display.view()` method to launch viewer
3. Static HTML export for deployment
4. Integration with trelliscopejs viewer

## Architecture Options

### Option 1: Serve trelliscopejs from CDN (Chosen)

**Approach**: Generate HTML page that loads trelliscopejs-lib from CDN

**Pros**:
- No need to bundle JavaScript
- Always uses latest viewer version
- Minimal Python code
- Fast to implement

**Cons**:
- Requires internet connection
- Less control over viewer version

### Option 2: Bundle trelliscopejs Locally

**Approach**: Include trelliscopejs-lib in package, serve locally

**Pros**:
- Works offline
- Version control
- Full customization

**Cons**:
- Large package size
- Need to maintain JS build
- More complex deployment

**Decision**: Start with Option 1 (CDN) for MVP, Option 2 as future enhancement

## Implementation Plan

### Component 1: Development Server

**File**: `trelliscope/server.py`

```python
import http.server
import socketserver
import threading
from pathlib import Path

class DisplayServer:
    """Simple HTTP server for viewing displays locally."""

    def __init__(self, display_dir: Path, port: int = 8000):
        self.display_dir = display_dir
        self.port = port
        self.httpd = None
        self.thread = None

    def start(self, blocking: bool = False):
        """Start server."""
        os.chdir(self.display_dir.parent)
        handler = http.server.SimpleHTTPRequestHandler
        self.httpd = socketserver.TCPServer(("", self.port), handler)

        if blocking:
            self.httpd.serve_forever()
        else:
            self.thread = threading.Thread(target=self.httpd.serve_forever)
            self.thread.daemon = True
            self.thread.start()

    def stop(self):
        """Stop server."""
        if self.httpd:
            self.httpd.shutdown()
```

### Component 2: Viewer HTML Generator

**File**: `trelliscope/viewer.py`

```python
def generate_viewer_html(display_name: str, config: dict = None) -> str:
    """Generate HTML page that loads trelliscopejs viewer."""

    html = f'''<!DOCTYPE html>
<html>
<head>
    <meta charset="utf-8">
    <title>Trelliscope - {display_name}</title>
    <meta name="viewport" content="width=device-width, initial-scale=1">
    <link rel="stylesheet" href="https://unpkg.com/trelliscopejs-lib/dist/assets/index.css">
</head>
<body>
    <div id="trelliscope-root"></div>
    <script src="https://unpkg.com/trelliscopejs-lib/dist/trelliscopejs-lib.js"></script>
    <script>
        TrelliscopeApp.createApp({{
            id: "trelliscope-root",
            displayListPath: "./{display_name}/displayInfo.json",
            spa: false
        }});
    </script>
</body>
</html>
'''
    return html
```

### Component 3: Display.view() Method

**Enhancement to**: `trelliscope/display.py`

```python
def view(
    self,
    port: int = 8000,
    open_browser: bool = True,
    blocking: bool = False
) -> str:
    """Launch viewer for this display.

    Starts a local server and opens the display in a browser.

    Parameters
    ----------
    port : int
        Port for development server. Default: 8000
    open_browser : bool
        Whether to open browser automatically. Default: True
    blocking : bool
        If True, blocks until server stopped. Default: False

    Returns
    -------
    str
        URL where display is being served

    Example
    -------
    >>> display.write()
    >>> display.view()  # Opens in browser
    >>> # Server runs in background

    >>> # Or blocking mode:
    >>> display.view(blocking=True)  # Ctrl+C to stop
    """
    from trelliscope.server import DisplayServer
    from trelliscope.viewer import generate_viewer_html, write_index_html
    import webbrowser

    # Ensure display is written
    if not self._output_path:
        self.write()

    # Generate viewer HTML
    html = generate_viewer_html(self.name)
    index_path = self._output_path.parent / "index.html"
    write_index_html(index_path, html)

    # Start server
    server = DisplayServer(self._output_path, port=port)
    server.start(blocking=False)

    # Open browser
    url = f"http://localhost:{port}/index.html"
    if open_browser:
        webbrowser.open(url)

    if blocking:
        print(f"Serving display at {url}")
        print("Press Ctrl+C to stop")
        server.httpd.serve_forever()
    else:
        print(f"Display available at: {url}")
        print("Server running in background")

    return url
```

### Component 4: Static Export

**File**: `trelliscope/export.py`

```python
def export_static(
    display_path: Path,
    output_path: Path,
    viewer_version: str = "latest"
) -> Path:
    """Export display as standalone HTML site.

    Creates self-contained directory with all assets.

    Parameters
    ----------
    display_path : Path
        Path to display directory
    output_path : Path
        Where to export static site
    viewer_version : str
        trelliscopejs-lib version to use

    Returns
    -------
    Path
        Path to exported site
    """
    import shutil

    # Create output directory
    output_path.mkdir(parents=True, exist_ok=True)

    # Copy display directory
    display_name = display_path.name
    shutil.copytree(display_path, output_path / display_name)

    # Generate and write index.html
    html = generate_viewer_html(display_name)
    (output_path / "index.html").write_text(html)

    # Generate README
    readme = generate_deployment_readme(display_name)
    (output_path / "README.md").write_text(readme)

    return output_path
```

## Data Flow

### Viewing a Display

```
User calls display.view()
         │
         ▼
Check if display written
         │ (if not)
         ├──► display.write()
         │
         ▼
Generate index.html with viewer
         │
         ▼
Start HTTP server (port 8000)
         │
         ▼
Open browser → http://localhost:8000/index.html
         │
         ▼
Browser loads trelliscopejs-lib from CDN
         │
         ▼
Viewer fetches displayInfo.json
         │
         ▼
Viewer renders interactive display
```

### Static Export

```
User calls export_static(display_path, output_path)
         │
         ▼
Create output directory
         │
         ▼
Copy display directory
         │
         ▼
Generate index.html
         │
         ▼
Generate README.md
         │
         ▼
Output ready for deployment
```

## File Structure

### Local Development

```
trelliscope_output/
├── index.html              # Generated viewer page
└── my_display/
    ├── displayInfo.json
    ├── metadata.csv
    └── panels/
        ├── 0.png
        └── ...
```

### Static Export

```
export_output/
├── index.html              # Viewer page
├── README.md              # Deployment instructions
└── my_display/
    ├── displayInfo.json
    ├── metadata.csv
    └── panels/
        ├── 0.png
        └── ...
```

## Integration with trelliscopejs-lib

### CDN Links

**Production**:
- CSS: `https://unpkg.com/trelliscopejs-lib/dist/assets/index.css`
- JS: `https://unpkg.com/trelliscopejs-lib/dist/trelliscopejs-lib.js`

**Specific Version**:
- `https://unpkg.com/trelliscopejs-lib@2.0.0/dist/...`

### JavaScript API

```javascript
// Initialize viewer
TrelliscopeApp.createApp({
    id: "trelliscope-root",           // DOM element ID
    displayListPath: "./display/",     // Path to display
    spa: false,                        // Single-page app mode
    config: {}                         // Additional config
});
```

## Phase 3 MVP Components

### Must-Have (MVP)
1. ✅ Simple HTTP server (http.server based)
2. ✅ HTML generation with CDN viewer
3. ✅ Display.view() method
4. ✅ Automatic browser opening
5. ✅ Basic tests

### Nice-to-Have (Later)
- Static export utility
- Custom viewer configuration
- Multiple display list support
- Viewer theme customization
- HTTPS support
- Authentication

## Testing Strategy

### Unit Tests
```python
def test_server_initialization():
    """Test server can be created."""
    server = DisplayServer(Path("/tmp/test"), port=8001)
    assert server.port == 8001

def test_html_generation():
    """Test HTML generation."""
    html = generate_viewer_html("my_display")
    assert "trelliscopejs-lib" in html
    assert "my_display" in html
```

### Integration Tests
```python
def test_view_workflow():
    """Test complete view workflow."""
    # Create and write display
    display = Display(df, name="test").set_panel_column("plot")
    display.write()

    # View (non-blocking)
    url = display.view(open_browser=False, blocking=False)

    # Verify server is running
    import requests
    response = requests.get(url)
    assert response.status_code == 200
```

### Manual Testing
- Open multiple displays simultaneously
- Test with different browsers
- Test with large displays (1000+ panels)
- Test panel navigation and filtering

## Browser Compatibility

**Supported Browsers**:
- Chrome/Edge 90+
- Firefox 88+
- Safari 14+

**Not Supported**:
- Internet Explorer

## Security Considerations

**Development Server**:
- Binds to localhost only (not 0.0.0.0)
- No authentication (local use only)
- CORS headers as needed

**Production Deployment**:
- Use proper web server (nginx, Apache)
- HTTPS recommended
- Consider authentication if needed

## Performance Considerations

**Server Performance**:
- http.server sufficient for local dev
- For production, use proper web server

**Viewer Performance**:
- Lazy loading of panels (handled by viewer)
- Efficient metadata filtering
- Virtual scrolling for large displays

## Migration from Phase 2

Phase 2 displays work without changes:
- Existing `write()` calls continue to work
- `view()` is optional, can still deploy manually
- No breaking changes to existing API

## Next Steps

1. Implement simple HTTP server
2. Create HTML generation utilities
3. Add Display.view() method
4. Write tests
5. Create example notebook
6. Document deployment options

## Future Enhancements

**Phase 3.5+**:
- Offline viewer bundle
- Custom viewer themes
- Display lists (multiple displays)
- Authentication support
- Cloud deployment utilities (S3, GitHub Pages)
- Docker containers
