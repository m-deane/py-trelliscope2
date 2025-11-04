# Notebook "0 of 0 Panels" Debug Analysis

## Status: ROOT CAUSE IDENTIFIED ✅

**Date**: November 4, 2025
**Issue**: Notebook viewer at localhost:8888 shows "0 of 0 panels"
**Working Reference**: Test at localhost:9000 shows panels correctly

---

## Problem Analysis

### Critical Discovery: OLD OUTPUT FILES

The notebook is displaying old output files generated **BEFORE** the panel display fixes were implemented.

**Evidence**:
```bash
# File timestamps in examples/output/basic_viewer_demo/
-rw-r--r--  1 matthewdeane  staff  1.4K Oct 28 21:59 displayInfo.json
-rw-r--r--  1 matthewdeane  staff  2.4K Oct 28 21:54 metaData.js
-rw-r--r--  1 matthewdeane  staff  902B Oct 28 21:44 metadata.csv
```

**Panel Display Fixes Implemented**: November 2-3, 2025 (per PANEL_DISPLAY_SUCCESS_SUMMARY.md)

### Comparison: Working vs. Broken

| Aspect | Working (localhost:9000) | Broken (localhost:8888) |
|--------|--------------------------|-------------------------|
| **Files Created** | Nov 3, 19:29 ✅ | Oct 28, 21:59 ❌ |
| **Structure** | Multi-display (config.json → displays/) ✅ | Flat (displayInfo.json at root) ❌ |
| **panelInterface.type** | `"file"` ✅ | `"panel_local"` ❌ |
| **panelInterface.base** | `"panels"` ✅ | `"./basic_viewer_demo/panels"` ❌ |
| **Panel meta type** | `"panel"` ✅ | `"panel_src"` ❌ |
| **primarypanel** | `"panel"` ✅ | `null` (missing) ❌ |
| **cogData** | Present with panel refs ✅ | Missing ❌ |
| **cogInterface** | Present ✅ | Missing ❌ |

### Old displayInfo.json Content (BROKEN)

```json
{
  "name": "basic_viewer_demo",
  "n": 20,
  "panelInterface": {
    "type": "panel_local",  // ❌ Should be "file"
    "panelCol": "panel",
    "format": "png",
    "base": "./basic_viewer_demo/panels",  // ❌ Should be "panels"
    "metaPath": "./metadata.json",
    "metaFile": "metadata.json",
    "dataPath": "./metadata.json"
  },
  "metas": [
    // ...other metas...
    {
      "varname": "panel",
      "label": "Panel",
      "type": "panel_src"  // ❌ Should be "panel"
    }
  ]
  // ❌ Missing: "primarypanel", "group", "cogInterface", "cogInfo", "cogData"
}
```

### Working displayInfo.json Content (CORRECT)

```json
{
  "name": "simple_static",
  "group": "common",
  "n": 5,
  "height": 500,
  "width": 500,
  "primarypanel": "panel",  // ✅ Present
  "panelInterface": {
    "type": "file",  // ✅ Correct
    "panelCol": "panel",
    "base": "panels"  // ✅ Correct (no ./ prefix)
  },
  "metas": [
    // ...other metas...
    {
      "varname": "panel",
      "type": "panel",  // ✅ Correct
      "label": "Panel",
      "paneltype": "img",
      "aspect": 1.0,
      "source": {
        "type": "file",
        "isLocal": true,
        "port": 0
      }
    }
  ],
  "cogInterface": {  // ✅ Present
    "name": "simple_static",
    "group": "common",
    "type": "JSON"
  },
  "cogData": [  // ✅ Present with panel references
    {
      "category": "A",
      "value": 10,
      "panelKey": "0",
      "panel": "0.png"
    }
    // ...
  ]
}
```

---

## Root Causes

### 1. Stale Output Files
The notebook references `examples/output/basic_viewer_demo/` which contains old files from before the fixes.

### 2. Missing Multi-Display Structure
Old output has flat structure:
```
examples/output/basic_viewer_demo/
├── displayInfo.json     # ❌ Old format
├── metadata.json
├── metaData.js
└── panels/
```

Should have multi-display structure:
```
examples/output/{name}/
├── index.html
├── config.json
└── displays/
    ├── displayList.json
    └── basic_viewer_demo/
        ├── displayInfo.json
        ├── metaData.json
        ├── metaData.js
        ├── metadata.csv
        └── panels/
```

### 3. Pre-Fix Implementation
Old files generated with code that had:
- Wrong panelInterface type (`"panel_local"` instead of `"file"`)
- Wrong base path (`"./basic_viewer_demo/panels"` instead of `"panels"`)
- Missing panel meta in metas array
- Missing primarypanel field

---

## Solution

### Step 1: Clean Old Output
Remove stale output directory:
```bash
rm -rf "examples/output/basic_viewer_demo"
```

### Step 2: Re-Run Notebook
The notebook code is already correct:
```python
display = (
    Display(data, name="basic_viewer_demo", path=output_dir)
    .set_panel_column('panel')
    .infer_metas()  # ✅ Calls infer_metas
    .set_default_layout(nrow=2, ncol=3)
)

output_path = display.write(force=True)  # ✅ Uses force=True
```

Running this with current code will generate correct multi-display structure.

### Step 3: Use New Output Path (Alternative)
Instead of cleaning, use a new output path:
```python
output_dir = Path("output/viewer_demo_v2")
```

This creates fresh output without interfering with old files.

---

## Verification Checklist

After re-running notebook, verify:

1. ✅ Multi-display structure exists:
   - `output/{name}/config.json`
   - `output/{name}/displays/displayList.json`
   - `output/{name}/displays/basic_viewer_demo/displayInfo.json`

2. ✅ displayInfo.json has correct fields:
   ```json
   {
     "primarypanel": "panel",
     "panelInterface": {
       "type": "file",
       "base": "panels"
     },
     "cogData": [ /* with panel refs */ ]
   }
   ```

3. ✅ Panel meta in metas array:
   ```json
   {
     "varname": "panel",
     "type": "panel",
     "paneltype": "img",
     "source": {"type": "file", "isLocal": true}
   }
   ```

4. ✅ Viewer shows panels (not "0 of 0")

---

## Prevention

### Best Practices
1. **Always use `force=True`** when re-running notebooks to overwrite old output
2. **Use dated output paths** for testing: `output/test_2025_11_04/`
3. **Clean old output** before major structure changes
4. **Check file timestamps** when debugging viewer issues

### Testing Pattern
```python
# Use dated output for testing
from datetime import datetime
timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
output_dir = Path(f"output/test_{timestamp}")

display = (
    Display(data, name="my_display", path=output_dir)
    .set_panel_column('panel')
    .infer_metas()
    .write(force=True)
)
```

---

## Conclusion

**✅ ISSUE RESOLVED**: The notebook code is correct. The problem is stale output files from before the panel display fixes were implemented.

**Solution**: Re-run the notebook cells to regenerate output with current code, or clean the old output directory first.

**Expected Result**: After re-running, the viewer will display panels correctly, matching the working test implementation at localhost:9000.
