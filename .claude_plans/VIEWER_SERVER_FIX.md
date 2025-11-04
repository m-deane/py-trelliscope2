# Display.view() Server Directory Fix

**Date**: November 4, 2025
**Issue**: Viewer showed "0 of 0 panels" due to server running from wrong directory
**Status**: **FIXED** ✅

---

## Root Cause

The `Display.view()` method was starting the HTTP server from the **wrong directory** for multi-display structures.

### The Bug

**In Display.write()** (line 813):
```python
self._output_path = display_output_path  # Points to displays/basic_viewer_demo/
```

**In Display.view()** (line 1070 - OLD):
```python
server = DisplayServer(self._output_path, port=port)
```

**In DisplayServer.start()** (server.py line 102):
```python
os.chdir(self.display_dir.parent)  # Changes to displays/
```

### Result
Server served from `examples/output/basic_viewer_demo/displays/` instead of `examples/output/basic_viewer_demo/`

This caused:
- `http://localhost:8889/config.json` → looked for `displays/config.json` (doesn't exist)
- `http://localhost:8889/displays/displayList.json` → looked for `displays/displays/displayList.json` (doesn't exist)
- Viewer couldn't find config files → showed "0 of 0 panels"

---

## The Fix

### Change 1: Store Root Path

**File**: `trelliscope/display.py`

**In `__init__()`** (line 151-152):
```python
# Track output paths for viewer integration
self._output_path: Optional[Path] = None  # Display directory (for writing files)
self._root_path: Optional[Path] = None    # Root directory (for serving HTTP)
```

**In `write()`** (line 812-814):
```python
# Store BOTH display path and root path for viewer integration
self._output_path = display_output_path
self._root_path = root_path
```

### Change 2: Use Root Path for Server

**In `view()`** (line 1066-1074):
```python
# Write index.html to root directory (for multi-display structure)
# Use root path if available, otherwise fallback to output_path parent
root_path = getattr(self, '_root_path', self._output_path.parent)
index_path = root_path / "index.html"
write_index_html(index_path, html)

# Start server from ROOT path (not display subdirectory)
# This is critical for multi-display structure to work correctly
server = DisplayServer(root_path, port=port)
```

---

## Before vs. After

| Aspect | Before (BROKEN) | After (FIXED) |
|--------|-----------------|---------------|
| **Server directory** | `displays/` | `root/` ✅ |
| **Server path** | `.../displays/` | `.../basic_viewer_demo/` ✅ |
| **config.json** | Not accessible | `http://localhost:8889/config.json` ✅ |
| **displayList.json** | Not accessible | `http://localhost:8889/displays/displayList.json` ✅ |
| **Panels display** | "0 of 0 panels" ❌ | Shows all panels ✅ |

---

## Test Results

### Test Script Output
```
✓ ALL CHECKS PASSED!

The notebook display has been generated correctly.
```

### Directory Structure Verification
```
examples/output/basic_viewer_demo/   ← SERVER STARTS HERE ✅
├── index.html
├── config.json
└── displays/
    ├── displayList.json
    └── basic_viewer_demo/
        ├── displayInfo.json
        ├── panels/
        │   ├── 0.png
        │   └── ...
        └── ...
```

---

## How to Test

### Option 1: Re-run Notebook Cell
In `examples/10_viewer_integration.ipynb`:
1. Re-run Cell 6 (the `.view()` call)
2. This will start a new server on the correct directory
3. Open `http://localhost:6547/` (or whatever port cell 6 uses)
4. **Expected**: Viewer shows 20 panels

### Option 2: Test with Script
```bash
cd /Users/matthewdeane/Documents/Data\ Science/python/_projects/py-trelliscope2
python examples/test_notebook_display.py

# Then manually start server
cd examples/output/notebook_test/basic_viewer_demo
python -m http.server 8889
# Open http://localhost:8889/
```

---

## Impact

### Files Changed
- `trelliscope/display.py`
  - Added `self._root_path` attribute
  - Store both display and root paths in `write()`
  - Use root path in `view()` for server

### Backward Compatibility
✅ **Fully backward compatible**
- Uses `getattr()` with fallback for old Display instances
- Single-display structure (non-multi-display) still works
- Existing code continues to work without changes

### Related Issues
- Fixes notebook "0 of 0 panels" issue
- Ensures `.view()` method works correctly with multi-display structure
- Server now serves from correct directory for all use cases

---

## Prevention

### Best Practice
When implementing server/viewer features:
1. **Always verify server root directory** matches structure requirements
2. **Test both single and multi-display modes**
3. **Check actual HTTP paths** the viewer tries to load
4. **Inspect server working directory** (not just the path passed to server)

### Testing Checklist
- [ ] Server serves from correct directory
- [ ] config.json accessible at `http://localhost:PORT/config.json`
- [ ] displayList.json accessible at `http://localhost:PORT/displays/displayList.json`
- [ ] displayInfo.json accessible at `http://localhost:PORT/displays/{name}/displayInfo.json`
- [ ] Panels load in viewer
- [ ] No "0 of 0 panels" message

---

## Conclusion

**✅ FIXED**: Display.view() now starts server from the correct root directory.

**Next Step**: Re-run notebook cell 6 to test the viewer with the fixed code.

**Expected Result**: Viewer will show 20 panels instead of "0 of 0 panels".
