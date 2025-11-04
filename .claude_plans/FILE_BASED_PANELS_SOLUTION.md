# File-Based Static Panels - Working Solution

**Date:** 2025-11-03
**Status:** ✅ WORKING - Panels successfully loading in trelliscopejs-lib v0.7.16

## Problem Summary

File-based static panels were not displaying in the trelliscope viewer despite correct file generation. The viewer showed "0 of 0" and made no requests for panel images.

## Root Cause

The viewer requires **THREE data sources** for file-based panels:
1. Embedded `cogData` in displayInfo.json
2. **metaData.json** - Separate file with cogData array
3. **metaData.js** - JavaScript file with `window.metaData = [...]`

Even though cogData is embedded in displayInfo.json, the viewer STILL looks for and requires metaData.js to function.

## Working Directory Structure

```
displays/
  displayList.json
  simple_static/
    displayInfo.json       # Full display configuration
    metaData.json          # cogData array
    metaData.js            # window.metaData = [...]
    panels/
      0.png
      1.png
      2.png
      3.png
      4.png
```

## Critical Files

### 1. displayInfo.json (Complete Structure)

```json
{
  "name": "simple_static",
  "group": "common",
  "description": "Simple Static Panel Example",
  "keysig": "unique_key",
  "n": 5,
  "height": 500,
  "width": 500,
  "tags": [],
  "keycols": [],
  "metas": [
    {
      "varname": "category",
      "label": "category",
      "type": "factor",
      "levels": ["A", "B", "C", "D", "E"],
      "tags": [],
      "filterable": true,
      "sortable": true
    },
    {
      "varname": "panel",
      "type": "panel",
      "label": "Panel",
      "paneltype": "img",
      "tags": [],
      "filterable": false,
      "sortable": false,
      "aspect": 1.0,
      "source": {
        "type": "file",
        "isLocal": true,
        "port": 0
      }
    }
  ],
  "inputs": null,
  "cogInterface": {
    "name": "simple_static",
    "group": "common",
    "type": "JSON"
  },
  "cogInfo": {
    "category": {
      "name": "category",
      "label": "category",
      "type": "factor",
      "group": null,
      "defLabel": true,
      "defActive": true,
      "filterable": true,
      "sortable": true,
      "log": null,
      "levels": ["A", "B", "C", "D", "E"]
    },
    "panelKey": {
      "name": "panelKey",
      "label": "panelKey",
      "type": "panelKey",
      "group": null,
      "defLabel": false,
      "defActive": false,
      "filterable": false,
      "sortable": false,
      "log": null
    }
  },
  "cogDistns": {},
  "cogData": [
    {
      "id": 0,
      "value": 10,
      "category": "A",
      "panelKey": "0",
      "panel": "0.png"
    }
  ],
  "state": {
    "layout": {
      "ncol": 3,
      "nrow": null,
      "page": 1,
      "arrangement": "row"
    },
    "labels": ["category", "value"],
    "sort": [],
    "filter": []
  },
  "views": [],
  "primarypanel": "panel",
  "panelInterface": {
    "type": "file",
    "base": "panels",
    "panelCol": "panel"
  },
  "imgSrcLookup": {}
}
```

### 2. metaData.json

```json
[
  {
    "id": 0,
    "value": 10,
    "category": "A",
    "panelKey": "0",
    "panel": "panels/0.png"
  },
  {
    "id": 1,
    "value": 25,
    "category": "B",
    "panelKey": "1",
    "panel": "panels/1.png"
  }
]
```

**Critical:** Panel paths are RELATIVE: `"panels/0.png"` (not full URLs)

### 3. metaData.js

```javascript
window.metaData = [
  {
    "id": 0,
    "value": 10,
    "category": "A",
    "panelKey": "0",
    "panel": "panels/0.png"
  },
  {
    "id": 1,
    "value": 25,
    "category": "B",
    "panelKey": "1",
    "panel": "panels/1.png"
  }
];
```

Same content as metaData.json but wrapped in `window.metaData = [...]`

### 4. Panel File Naming

**CORRECT:** `0.png`, `1.png`, `2.png`, etc.
**WRONG:** `panel_0.png`, `panel_1.png`, etc.

Panel IDs should match the `panelKey` values in cogData.

## Required Fields in displayInfo.json

### Top-Level Required:
- `name`, `group`, `description`, `keysig`
- `n` (number of panels)
- `height`, `width` (panel dimensions)
- `tags`, `keycols` (can be empty arrays)
- `inputs` (null for static)
- `primarypanel` (which meta is the panel)

### Metas Array:
Each meta (cognostic variable) needs:
- `varname`, `label`, `type`
- `tags` (array, can be empty)
- `filterable`, `sortable` (boolean)

Panel meta additionally needs:
- `paneltype`: "img"
- `aspect`: ratio (e.g., 1.0)
- `source`: `{"type": "file", "isLocal": true, "port": 0}`

### Cognitive Data:
- `cogInterface`: Type declaration
- `cogInfo`: Detailed metadata for each variable
- `cogDistns`: Distribution data (can be empty object)
- `cogData`: Embedded array of data rows

### Panel Configuration:
- `panelInterface`:
  - `type`: "file"
  - `base`: "panels" (relative path)
  - `panelCol`: "panel" (which field has panel reference)
- `imgSrcLookup`: Empty object for file-based

### State:
- `state`: Layout, labels, sort, filter configs
- `views`: Array of saved views (can be empty)

## Key Discoveries

1. **R Examples Are Incompatible**: The R-generated examples (r_example_static, r_example) use the OLD trelliscopejs_widget v0.3.2 (htmlwidgets-based) which uses JSONP format. Modern trelliscopejs-lib v0.7.16 uses pure JSON and a different architecture.

2. **metaData.js is Required**: Despite embedding cogData in displayInfo.json, the viewer makes a request for metaData.js and won't load panels without it.

3. **Relative Panel Paths**: In metaData files, panel values should be relative paths like `"panels/0.png"`, not full URLs.

4. **Panel Path Construction**: The viewer constructs full panel URLs as:
   ```
   {display_base}/{display_name}/{panelInterface.base}/{panel_value}
   displays/simple_static/panels/0.png
   ```

## Testing Verification

**Test URL:** http://localhost:8001/
**Result:** ✅ 5 panels loading successfully

**Browser Console:**
```
✓ Viewer loaded
✓ simple_static loaded
Images found: 5
```

**Network Requests:**
```
GET /displays/simple_static/displayInfo.json - 200
GET /displays/simple_static/metaData.js - 200
GET /displays/simple_static/panels/0.png - 200
GET /displays/simple_static/panels/1.png - 200
...
```

## Python Implementation Checklist

✅ **COMPLETED** - Implementation finished on 2025-11-03

- [x] Generate displayInfo.json with ALL required fields
- [x] Generate metaData.json with cogData array
- [x] Generate metaData.js with `window.metaData = [...]` wrapper
- [x] Name panels by ID only: `{id}.png`
- [x] Use relative panel paths in metaData: `"panels/{id}.png"`
- [x] Set panelInterface base to "./panels"
- [x] Include cogInfo with detailed metadata for all variables
- [x] Add panelKey to cogInfo (not in metas)

**Implementation Details:**
- See `.claude_plans/METADATA_FILES_IMPLEMENTATION.md` for complete details
- Added functions: `write_metadata_json()`, `write_metadata_js()`, `_serialize_cog_data()`
- Updated: `serialize_display_info()` to include all required fields
- Updated: `Display.write()` to generate all three metadata files
- Tests: `tests/test_metadata_generation.py` - 12 tests, all passing
- Example: `examples/simple_static_display.py` - demonstrates usage

## Next Steps

1. ✅ Verify panels display correctly in browser
2. Update Python `write_display()` function to generate all required files
3. Add tests for file-based panel generation
4. Update documentation with correct structure
5. Add support for both static (file) and dynamic (REST) panels
