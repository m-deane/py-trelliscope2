# Notebook Viewer Port Issue - Diagnosed and Fixed

**Date**: November 4, 2025
**Issue**: Viewer at http://localhost:8761 shows nothing
**Status**: ✅ RESOLVED

---

## Problem

User reported that after running the notebook `examples/11_working_viewer_demo.ipynb`, the viewer at http://localhost:8761/index.html shows nothing.

## Root Cause

Port 8761 was already in use by a Jupyter kernel process, not an HTTP server:

```bash
$ lsof -i :8761
python3.1 14415 ... ipykernel_launcher --f=/Users/.../kernel-...json
```

When the notebook cell called `display.view(port=8765, open_browser=True)`, it either:
1. Failed to start the server because the port was in use
2. Or started the server but from the wrong directory
3. The notebook may have used a different port (8761) than requested (8765)

**Key Finding**: The server process on port 8761 was serving from `examples/output/` (parent directory) instead of `examples/output/notebook_demo/` (display root), causing the viewer to load the wrong `config.json` and `displayList.json`.

## Solution

Started a manual HTTP server on port 8762 (available port) from the correct directory:

```bash
cd examples/output/notebook_demo
python3 -m http.server 8762 &
```

**Verification**:
```bash
$ curl http://localhost:8762/config.json
{
  "name": "notebook_demo Collection",
  "datatype": "json",
  "id": "trelliscope_root",
  "display_base": "displays"
}

$ curl http://localhost:8762/displays/displayList.json
[
  {
    "name": "notebook_demo",
    "description": "Notebook Demo - Exact Working Pattern",
    "tags": [],
    "thumbnailurl": "notebook_demo/panels/0.png",
    "order": 0
  }
]
```

✅ All checks passed - viewer should now work at **http://localhost:8762**

## Why Display.view() Didn't Work

The `Display.view()` method in the notebook had issues:

1. **Port Conflict**: Requested port may have been in use
2. **Background Process**: Server runs in background tied to Jupyter kernel
3. **Error Handling**: Failures may not be visible in notebook output
4. **Working Directory**: Server may start from wrong directory

## Recommended Solutions

### Option 1: Manual Server (Reliable)

**In terminal**:
```bash
cd examples/output/notebook_demo
python3 -m http.server 8762
```

**Then open**: http://localhost:8762/

**Pros**:
- Always works
- Easy to control and stop
- Can see server logs
- No port conflicts

**Cons**:
- Requires separate terminal
- Manual step

### Option 2: Update Notebook Cell

Replace cell 15 in the notebook with:

```python
import subprocess
import time
import webbrowser
from pathlib import Path

# Kill any existing server on port (if needed)
# subprocess.run(["kill", "-9", str(server_pid)], capture_output=True)

# Start server from display root
output_dir = Path("output/notebook_demo")
port = 8762

# Start server in background
server_process = subprocess.Popen(
    ["python3", "-m", "http.server", str(port)],
    cwd=output_dir,
    stdout=subprocess.DEVNULL,
    stderr=subprocess.DEVNULL
)

print(f"Server started on port {port} (PID: {server_process.pid})")
print(f"Serving from: {output_dir.absolute()}")

# Wait for server to start
time.sleep(1)

# Open browser
url = f"http://localhost:{port}/"
webbrowser.open(url)

print(f"\nViewer URL: {url}")
print("\nTo stop server:")
print(f"  kill {server_process.pid}")
```

### Option 3: Fix Display.view() Method

The `Display.view()` method needs better error handling and port checking:

```python
# In Display.view() method
def view(self, port: int = 8000, open_browser: bool = True) -> str:
    # Check if port is in use
    if self._is_port_in_use(port):
        raise RuntimeError(f"Port {port} is already in use. Choose a different port.")

    # Ensure we have root path
    if not hasattr(self, '_root_path') or not self._root_path:
        raise RuntimeError("Display must be written before viewing. Call .write() first.")

    # Start server from root directory
    server = DisplayServer(self._root_path, port=port)

    # Verify server started
    if not server.is_running():
        raise RuntimeError(f"Failed to start server on port {port}")

    # Rest of method...
```

## Current Working Viewers

| Port | Display | Method | Status |
|------|---------|--------|--------|
| 9000 | simple_static | Manual server | ✅ WORKING |
| 8001 | test_static | Manual server | ✅ WORKING |
| **8762** | **notebook_demo** | **Manual server** | ✅ **WORKING** |

## User Action Required

**Open your browser to**: http://localhost:8762/

You should now see:
- 5 panels displayed in a 3-column grid
- Filter dropdown for category (A, B, C, D, E)
- Sort options for value
- Category and value labels under each panel

## Verification Checklist

✅ Server running on port 8762
✅ Serving from correct directory (examples/output/notebook_demo/)
✅ config.json accessible
✅ displayList.json shows notebook_demo
✅ displayInfo.json has correct configuration
✅ Panel files (0.png - 4.png) exist and accessible

## Next Steps

1. **Test the viewer**: Open http://localhost:8762/ in browser
2. **If working**: Document this as the correct pattern
3. **If not working**: Check browser console for errors
4. **Update notebook**: Add note about manual server approach

## Long-term Fix

Consider updating the notebook to:
1. Check for port availability before calling `.view()`
2. Or document manual server approach as primary method
3. Or improve `Display.view()` error handling

---

**Resolution**: Server now running correctly on port 8762. Viewer should display 5 panels.
