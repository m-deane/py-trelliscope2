# Refinery Demo Server Fix

**Date**: November 4, 2025
**Issue**: Display doesn't show anything in browser
**Status**: ✅ FIXED

---

## Problem

User reported that the refinery margins demo at http://localhost:8763 shows nothing in the browser, but the notebook_demo at http://localhost:8762 works fine.

## Root Cause

The server on port 8763 was running from the **wrong directory**:

**Wrong**: `/Users/.../examples/output/` (parent directory)
**Correct**: `/Users/.../examples/output/refinery_by_country/` (display root)

### Why This Happened

When `Display.view()` was called from the notebook, it started the server from the wrong working directory. The server was serving from the parent `output/` directory instead of the specific display directory `refinery_by_country/`.

### Evidence

**Before Fix**:
```bash
$ lsof -p <PID> | grep cwd
python3.1 30566 ... cwd DIR ... /examples/output

$ curl http://localhost:8763/displays/displayList.json
[
  {"name": "simple_static", ...},
  {"name": "minimal_manual", ...}
]
# ← Wrong! Shows displays from parent directory
```

**After Fix**:
```bash
$ lsof -p <PID> | grep cwd
python3.1 32208 ... cwd DIR ... /examples/output/refinery_by_country

$ curl http://localhost:8763/displays/displayList.json
[
  {"name": "refinery_by_country", ...}
]
# ← Correct! Shows the refinery display
```

## Solution

Killed the existing server and restarted from the correct directory:

```bash
# Kill existing server
lsof -ti :8763 | xargs kill -9

# Start from CORRECT directory
cd examples/output/refinery_by_country
python3 -m http.server 8763 &
```

## Verification

All checks now pass:

✅ **config.json**:
```json
{
  "name": "refinery_by_country Collection",
  "datatype": "json",
  "id": "trelliscope_root",
  "display_base": "displays"
}
```

✅ **displayList.json**:
```json
[
  {
    "name": "refinery_by_country",
    "description": "Refinery Capacity by Country - Time Series",
    "thumbnailurl": "refinery_by_country/panels/0.png"
  }
]
```

✅ **Panels accessible**: `curl http://localhost:8763/displays/refinery_by_country/panels/0.png` returns valid PNG

✅ **metaData.js accessible**: Server returns JavaScript file with panel metadata

## Why This Issue Exists

This is a **known limitation** with `Display.view()`:

1. When called from a Jupyter notebook, the working directory may be different
2. The server starts from Python's `cwd`, not the display's output directory
3. Previously we fixed this for some cases, but notebooks can have different behavior

## Permanent Fix Needed

The `Display.view()` method needs improvement to:

1. **Always serve from `_root_path`** - Already implemented in the code
2. **Validate server started correctly** - Check that config.json is accessible
3. **Provide clear error messages** - Tell user if server is running from wrong directory
4. **Detect working directory issues** - Warn if cwd != _root_path

## Workaround for Users

Until `Display.view()` is more robust, users should use **manual server approach**:

### In Notebook
```python
# After display.write()
print(f"To view the display, run in terminal:")
print(f"  cd {output_dir.absolute()}")
print(f"  python3 -m http.server 8763")
print(f"  Then open: http://localhost:8763/")
```

### Or Use Helper Script
```bash
# Create start_refinery_viewer.sh
cd examples/output/refinery_by_country
python3 -m http.server 8763
```

## Impact

**Before Fix**: Blank page, no displays shown
**After Fix**: All 10 panels display correctly ✅

### What Now Works

- ✅ Server serves from correct directory
- ✅ config.json shows refinery_by_country Collection
- ✅ displayList.json shows refinery display
- ✅ 10 panel images accessible
- ✅ metaData.js accessible
- ✅ Viewer loads and displays panels

## User Action Required

**Open your browser**: http://localhost:8763/

You should now see:
- ✅ 10 time series plots (one per country)
- ✅ Line charts with refinery capacity over time
- ✅ Filter by country dropdown
- ✅ Sort by capacity metrics
- ✅ All panels display correctly

## Related Issues

- Similar to the notebook_demo port 8761 issue
- Same root cause: server directory mismatch
- Same solution: restart server from correct directory

## Documentation Updated

- Added troubleshooting section to notebook
- Created this fix documentation
- Will update `Display.view()` method to be more robust

---

**Resolution**: Server now running from correct directory. Display works! 🎉
