# Critical Differences: Working R Example vs Broken Python Implementation

## Analysis Date: 2025-11-02

## Executive Summary

**ROOT CAUSE IDENTIFIED**: The Python implementation is using the wrong **data format** and **panel interface type** compared to the working R example.

---

## 1. CRITICAL DIFFERENCE: Data Format (JSONP vs JSON)

### Working R Example
- **Data Format**: `JSONP` (JSON with Padding - callback-based)
- **Config File**: `config.jsonp` with callback wrapper
- **Config Content**:
  ```javascript
  __loadTrscopeConfig__890bd296({
    "display_base": "displays",
    "data_type": "jsonp",
    "cog_server": {
      "type": "jsonp",
      "info": {
        "base": "displays"
      }
    },
    "split_layout": false,
    "has_legend": false
  })
  ```

### Broken Python Example
- **Data Format**: `JSON` (plain JSON)
- **Config File**: `config.json` (no callback wrapper)
- **Config Content**:
  ```json
  {
    "name": "Trelliscope App",
    "datatype": "json",
    "id": "trelliscope_root"
  }
  ```

**IMPACT**: The viewer is expecting JSONP callbacks but receiving plain JSON, causing load failures.

---

## 2. CRITICAL DIFFERENCE: Panel Interface Type

### Working R Example (displayObj.jsonp)
```javascript
"panelInterface": {
  "type": "htmlwidget",
  "deps": {
    "name": "plotly",
    "assets": [
      {"type": "script", "url": "lib/htmlwidgets-1.6.4/htmlwidgets.js"},
      {"type": "script", "url": "lib/plotly-binding-4.10.4/plotly.js"},
      // ... more plotly dependencies
    ]
  }
}
```

**Panel Storage**: Panels are stored as **JSONP files** containing plotly widget HTML:
- File: `displays/common/refinery_by_country/jsonp/Algeria.jsonp`
- Format: `__panel__._Algeria_refinery_by_country({ plotly data })`

### Broken Python Example (displayInfo.json)
```json
"panelInterface": {
  "type": "panel_local",
  "panelCol": "panel"
}
```

**Panel Storage**: Panels are stored as **PNG images**:
- Files: `displays/minimal_manual/panels/0.png`, `1.png`, `2.png`

**IMPACT**: The panel interface type doesn't match the actual panel format, causing rendering failures.

---

## 3. File Structure Differences

### Working R Example Structure
```
r_example/
├── index.html (htmlwidgets-based loader)
├── lib/ (JavaScript libraries)
│   ├── htmlwidgets-1.6.4/
│   ├── trelliscopejs_widget-0.3.2/
│   └── trelliscopejs_widget-binding-0.2.6/
└── appfiles/
    ├── config.jsonp (JSONP format)
    ├── id (unique ID file)
    └── displays/
        ├── displayList.jsonp (callback-wrapped)
        └── common/
            └── refinery_by_country/
                ├── displayObj.jsonp (callback-wrapped)
                ├── cogData.jsonp (callback-wrapped)
                └── jsonp/ (panel JSONP files)
                    ├── Algeria.jsonp
                    ├── Denmark.jsonp
                    └── ...
```

### Broken Python Example Structure
```
output/
├── index.html (ESM module-based loader)
├── config.json (plain JSON)
└── displays/
    └── minimal_manual/
        ├── displayInfo.json (plain JSON)
        ├── metaData.json (plain JSON)
        └── panels/ (PNG images)
            ├── 0.png
            ├── 1.png
            └── 2.png
```

---

## 4. Metadata Storage Differences

### Working R Example
- **Cognostics Data**: `cogData.jsonp` (JSONP callback)
- **Display Info**: `displayObj.jsonp` (JSONP callback)
- **Format**: Callback-wrapped with unique function names
  ```javascript
  __loadCogData__890bd296_common_refinery_by_country([
    {"country":"Algeria", "panelKey":"Algeria", ...},
    {"country":"Denmark", "panelKey":"Denmark", ...},
    ...
  ])
  ```

### Broken Python Example
- **Metadata**: `metaData.json` (plain JSON array)
- **Display Info**: `displayInfo.json` (plain JSON object)
- **Format**: Simple JSON arrays/objects
  ```json
  [
    {"id": 0, "value": 0, "category": "A", "panel": "panels/0.png"},
    {"id": 1, "value": 10, "category": "B", "panel": "panels/1.png"},
    {"id": 2, "value": 20, "category": "C", "panel": "panels/2.png"}
  ]
  ```

---

## 5. Index.html Initialization Differences

### Working R Example
- **Technology**: R htmlwidgets framework
- **Viewer Version**: trelliscopejs_widget-0.3.2 (older, JSONP-based)
- **Initialization**:
  ```html
  <script src="lib/htmlwidgets-1.6.4/htmlwidgets.js"></script>
  <script src="lib/trelliscopejs_widget-0.3.2/trelliscope.min.js"></script>
  <script type="application/json" data-for="htmlwidget-...">
    {"x":{"id":"890bd296","config_info":"'appfiles/config.jsonp'", ...}}
  </script>
  ```

### Broken Python Example
- **Technology**: ESM modules from CDN
- **Viewer Version**: trelliscopejs-lib@0.7.16 (newer, JSON-based)
- **Initialization**:
  ```html
  <script type="module">
    const module = await import('https://esm.sh/trelliscopejs-lib@0.7.16?bundle');
    initFunc('trelliscope_root', './config.json');
  </script>
  ```

**ISSUE**: Version mismatch - newer viewer expects JSON mode, but Python is mixing JSONP field names with JSON format.

---

## 6. DisplayInfo/DisplayObj Field Comparison

### Key Differences

| Field | R Example (displayObj.jsonp) | Python Example (displayInfo.json) |
|-------|------------------------------|-----------------------------------|
| **Format** | JSONP callback-wrapped | Plain JSON object |
| **Metadata field** | `cogInfo` (inline definitions) | `metas` (array of definitions) |
| **Panel paths** | Separate JSONP files in `jsonp/` dir | Referenced in metaData.json |
| **Panel type** | `"type": "htmlwidget"` with deps | `"type": "panel_local"` with panelCol |
| **Cognostics data** | Separate `cogData.jsonp` file | Combined in `metaData.json` |
| **Distribution data** | `cogDistns` object with histograms | Missing entirely |
| **State** | `state` object with layout/labels/sort | `state` object (structure differs) |

### Specific Field Differences

#### R Example Fields (Present)
```javascript
{
  "name": "refinery_by_country",
  "group": "common",               // ✓ Has group
  "desc": "Refinery Capacity",
  "n": 10,
  "height": 500,
  "width": 500,
  "cogInterface": {...},           // ✓ Cognition interface
  "panelInterface": {...},
  "cogInfo": {...},                // ✓ Meta variable definitions
  "cogDistns": {...},              // ✓ Distribution data for filters
  "imgSrcLookup": {},
  "state": {...}
}
```

#### Python Example Fields (Present)
```json
{
  "name": "minimal_manual",
  "description": "Minimal manual example",
  "keysig": "manual123",
  "tags": [],
  "keycols": [],
  "metas": [...],                  // ✓ Array format (not object)
  "inputs": null,
  "state": {...},
  "views": [],
  "primarypanel": "panel",
  "thumbnailurl": "panels/0.png",
  "order": 0,
  "panelInterface": {...}
}
```

---

## 7. The Smoking Gun: Panel Path Resolution

### Working R Example
1. **DisplayObj** specifies: `"panelInterface": {"type": "htmlwidget", ...}`
2. **Panels stored at**: `displays/common/refinery_by_country/jsonp/Algeria.jsonp`
3. **Viewer loads**: JSONP callback files with embedded plotly HTML
4. **Result**: ✓ Images render correctly

### Broken Python Example
1. **DisplayInfo** specifies: `"panelInterface": {"type": "panel_local", "panelCol": "panel"}`
2. **Metadata** specifies: `"panel": "panels/0.png"`
3. **Panels stored at**: `displays/minimal_manual/panels/0.png`
4. **Viewer expects**: Panel paths in metaData to be loaded as images
5. **Result**: ✗ Images don't render (path resolution issue)

---

## 8. Root Cause Analysis

### Primary Issue: Architecture Mismatch

The Python implementation is trying to use **trelliscopejs-lib@0.7.16** (JSON mode) but:

1. **Missing required fields** for JSON mode:
   - No `cogDistns` (distribution data needed for filter UI)
   - Panel paths may not be resolving correctly
   - Missing display `group` field

2. **Using wrong panel storage**:
   - Storing as PNG files but using `panel_local` type
   - Should either:
     - Store as PNG and use proper image panel interface, OR
     - Store as HTML/JSONP for interactive widgets

3. **Incomplete metadata structure**:
   - Missing histogram/distribution data for filter UI
   - Missing proper panel path resolution mechanism

### Secondary Issue: Version Incompatibility

The R example uses **older trelliscopejs** (v0.3.2 htmlwidgets version) which:
- Uses JSONP callback pattern
- Has different field expectations
- Includes bundled JavaScript libraries

The Python example uses **newer trelliscopejs-lib** (v0.7.16) which:
- Uses plain JSON with fetch API
- Has evolved field structure
- Loads from CDN via ESM

---

## 9. Specific Fix Required

### Option 1: Match R JSONP Approach (Not Recommended)
- Convert all JSON to JSONP with callbacks
- Store panels as JSONP-wrapped HTML
- Use older htmlwidgets-based viewer

### Option 2: Fix JSON Mode Implementation (RECOMMENDED)

**Required Changes to Python Code:**

1. **Add `cogDistns` field** to displayInfo.json:
   ```json
   "cogDistns": {
     "id": {
       "type": "numeric",
       "dist": {
         "raw": {"breaks": [0, 1, 2, 3], "freq": [1, 1, 1]}
       },
       "log_default": false
     },
     "value": { ... },
     "category": {
       "type": "factor",
       "dist": {"A": 1, "B": 1, "C": 1},
       "has_dist": true,
       "max": 1
     }
   }
   ```

2. **Fix panel interface type** for PNG images:
   ```json
   "panelInterface": {
     "type": "file",
     "extension": "png"
   }
   ```

3. **Ensure panel paths** in metaData.json are correct relative paths:
   ```json
   {"id": 0, "panel": "displays/minimal_manual/panels/0.png"}
   ```
   OR use base-relative paths if config specifies display_base

4. **Add display group field**:
   ```json
   "group": "common"
   ```

5. **Update config.json** to match newer format:
   ```json
   {
     "display_base": "displays",
     "data_type": "json",
     "id": "trelliscope_root"
   }
   ```

---

## 10. Conclusion

**The images don't render because:**

1. ✗ **Panel interface type mismatch**: Using `panel_local` with PNG files instead of `file` type
2. ✗ **Missing distribution data**: `cogDistns` field required for filter UI
3. ✗ **Panel path resolution**: Paths in metaData.json may not be resolving correctly
4. ✗ **Incomplete displayInfo**: Missing fields that viewer expects in JSON mode

**Priority Fix Order:**
1. Change `panelInterface.type` from `"panel_local"` to `"file"`
2. Add `"extension": "png"` to panelInterface
3. Add `cogDistns` field with histogram data
4. Verify panel paths are correct (likely need full paths from display root)
5. Add `group` field to displayInfo

**Test Strategy:**
After each fix, reload the viewer and check browser console for errors. The panel loading should show progress through:
1. Config loaded ✓
2. Display list loaded ✓
3. Display info loaded ✓
4. Metadata loaded ✓ (currently working)
5. Panel paths resolved ✗ (currently failing)
6. Images rendered ✗ (currently failing)
