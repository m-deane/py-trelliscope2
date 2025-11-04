# Safari Trelliscope Viewer Debugging Session Summary

## Goal
Fix the Trelliscope viewer to display panel images in Safari browser.

## Initial State
- Viewer loaded successfully in Safari (initialization fixed in previous session)
- Showed "0 of 0" panels instead of expected 20 panels
- No panel images visible

## Key Discoveries

### 1. File Structure Requirements
The R trelliscope package uses this structure:
```
output/
├── config.jsonp          # App config with datatype: "jsonp"
├── id                    # App ID file
├── displays/
│   ├── displayList.jsonp # List of displays
│   └── {display_name}/
│       ├── displayInfo.jsonp  # Display configuration
│       ├── metaData.js        # Panel metadata
│       └── panels/
│           ├── 0.png
│           ├── 1.png
│           └── ...
```

### 2. JSONP vs JSON Mode
- **JSONP Mode**: For local file browsing without server
  - Files: `.jsonp` extensions
  - Uses callbacks: `__loadAppConfig__`, `__loadDisplayList__`, `__loadDisplayInfo__`
  - metaData: `window.metaData = [...]` (NO callback!)
  - Initialize with: `trelliscopeApp('id', './config.jsonp')`

- **JSON Mode**: For server deployment
  - Files: `.json` extensions
  - Uses fetch() to load data
  - Initialize with: `trelliscopeApp('id', './config.json')`

### 3. Safari Local File Restrictions
- Safari blocks `fetch()` for `file://` protocol
- Solution: Run local web server (`python3 -m http.server 8000`)
- Access via: `http://localhost:8000/index.html`

### 4. Configuration File Format

**config.jsonp:**
```javascript
__loadAppConfig__trelliscope_root({
  "name": "Trelliscope App",
  "datatype": "jsonp",
  "id": "trelliscope_root"
})
```

**displayList.jsonp:**
```javascript
__loadDisplayList__trelliscope_root([
  {
    "name": "display_name",
    "description": "...",
    "tags": [],
    "thumbnailurl": "display_name/panels/0.png",
    "order": 0
  }
])
```

**displayInfo.jsonp:**
```javascript
__loadDisplayInfo__trelliscope_root({
  "name": "display_name",
  "description": "...",
  "keysig": "...",
  "n": 3,
  "metas": [
    // Cognostic variables (NOT including panel column)
    {"varname": "id", "label": "ID", "type": "number", ...},
    {"varname": "category", "label": "Category", "type": "factor", "levels": [...]},
    // Panel meta (when included, breaks data loading - TBD why)
    {"varname": "panel", "type": "panel", "paneltype": "img", "aspect": 1, ...}
  ],
  "state": {
    "layout": {"ncol": 3, "nrow": 1, "page": 1, "arrangement": "row"},
    "labels": [],
    "sort": [],
    "filter": []
  },
  "views": [],
  "primarypanel": "panel",
  "thumbnailurl": "panels/0.png",
  "tags": [],
  "keycols": [],
  "inputs": null,
  "order": 0,
  "panelInterface": {
    "type": "file",
    "panelCol": "panel"
  }
})
```

**metaData.js:**
```javascript
window.metaData = [
  {"id": 0, "value": 0, "category": "A", "panel": "panels/0.png"},
  {"id": 1, "value": 10, "category": "B", "panel": "panels/1.png"},
  {"id": 2, "value": 20, "category": "C", "panel": "panels/2.png"}
];
```

### 5. Viewer Initialization
```javascript
// Load metaData.js first (sets window.metaData)
<script src="./displays/display_name/metaData.js"></script>

<script type="module">
    const module = await import('https://esm.sh/trelliscopejs-lib@0.7.16?bundle');
    const initFunc = window.trelliscopeApp || module.trelliscopeApp;

    // Initialize with config.jsonp (NOT .json!)
    initFunc('trelliscope_root', './config.jsonp');
</script>
```

## Current Status

### ✅ Working
- Viewer initialization in Safari
- Data loading: Shows "1 - 3 of 3"
- Callback system: JSONP callbacks fire correctly
- Configuration structure: displayInfo loads with all required fields

### ❌ Not Working
- **Panel rendering**: Shows "No Image" placeholders
- **No img elements created**: Image creation code path never executes
- **Tried solutions that didn't work:**
  - Relative paths: `"panels/0.png"`
  - Full paths: `"displays/minimal_manual/panels/0.png"`
  - Absolute HTTP URLs: `"http://localhost:8000/..."`
  - With/without panel meta in metas array
  - Different panelInterface configurations

## The Mystery

Despite having **perfect configuration** (confirmed via inspection):
- ✓ primarypanel: "panel"
- ✓ Panel meta with type: "panel", paneltype: "img"
- ✓ panelInterface with type: "file", panelCol: "panel"
- ✓ window.metaData with panel column
- ✓ Panel image files exist and are accessible

The viewer:
- Shows "1 - 3 of 3" (knows there are 3 panels)
- Shows "No Image" placeholders (knows to render panels)
- **But creates ZERO `<img>` elements** (image rendering code never runs)

## Hypothesis

There may be an additional undocumented field or condition required for the viewer to trigger image rendering. Possible areas to investigate:

1. **View mode**: Maybe the viewer is in "table" mode instead of "grid" mode?
2. **Missing field**: Some field we haven't discovered that enables image rendering
3. **Library version**: Maybe the 0.7.16 version has different requirements?
4. **Browser compatibility**: Despite fixing Safari init, there may be other Safari-specific issues

## Next Steps

1. **Generate working example from R package**: Use actual R code to create a display, inspect the exact JSON structure
2. **Compare with Python output**: Find differences in structure/fields
3. **Try older viewer versions**: Test with different trelliscopejs-lib versions
4. **Deep dive into viewer source**: Examine trelliscopejs-lib source code to understand image rendering logic
5. **Contact maintainers**: Report issue to trelliscope developers if needed

## Files Created

### Core Structure
- `/examples/output/config.jsonp`
- `/examples/output/config.json`
- `/examples/output/id`
- `/examples/output/displays/displayList.jsonp`
- `/examples/output/displays/minimal_manual/displayInfo.jsonp`
- `/examples/output/displays/minimal_manual/metaData.js`
- `/examples/output/index.html`

### Test Files (18+)
- `test_config_init.html` - Test config-based initialization
- `test_jsonp_mode.html` - Test JSONP mode
- `test_callback_check.html` - Check callback registration
- `test_image_urls_final.html` - Track image URL construction
- `test_inspect_displayinfo.html` - Inspect loaded displayInfo
- `test_absolute_urls.html` - Test with absolute HTTP URLs
- And many more...

## Time Invested
~6 hours of intensive debugging

## Learning Outcomes
- Deep understanding of trelliscope JSONP callback system
- Safari local file restriction workarounds
- Trelliscope file structure and configuration format
- Viewer initialization patterns

---

**Status**: Panel data loading works, but image rendering blocked by unknown factor
**Severity**: High - core functionality not working
**Reproducibility**: 100% - consistent across all configurations tried
