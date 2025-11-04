# HTML Panel Investigation Report

## Executive Summary

**Problem**: Plotly HTML panels showing "No Image" in Trelliscope viewer
**Root Cause**: Missing `paneltype` field in panel meta configuration
**Status**: Configuration appears correct but needs `paneltype: "iframe"` in metas array

## Current Python Implementation

### Our displayInfo.json Structure (refinery_plotly)

```json
{
  "panelInterface": {
    "type": "iframe",      // ✓ Correct for HTML
    "panelCol": "panel",   // ✓ Correct
    "base": "panels"       // ✓ Correct
  },
  "metas": [
    {
      "varname": "panel",
      "type": "panel",
      "label": "Panel",
      "paneltype": "img",    // ❌ WRONG - Should be "iframe" for HTML
      "source": {
        "type": "file",
        "isLocal": true,
        "port": 0
      }
    }
  ]
}
```

### Panel Files Generated
- Location: `panels/0.html`, `panels/1.html`, etc.
- Format: Self-contained Plotly HTML with embedded JavaScript
- Panel references in cogData: `"panel": "0.html"` (correct)

## R Implementation (Reference)

### Old Viewer (JSONP - r_example)
```json
{
  "panelInterface": {
    "type": "htmlwidget",
    "deps": {
      "name": "plotly",
      "assets": [...library files...]
    }
  }
}
```

**Note**: This is the OLD viewer format (v0.3.2) using JSONP. NOT compatible with modern viewer.

## Technical Analysis

### Panel Type Determination Matrix

| File Extension | panelInterface.type | Panel Meta paneltype | Viewer Element |
|---------------|-------------------|---------------------|----------------|
| `.png`, `.jpg` | `"file"` | `"img"` | `<img>` tag |
| `.html`, `.htm` | `"iframe"` | `"iframe"` | `<iframe>` tag |
| URLs | `"REST"` | `"img"` or `"iframe"` | Based on content |

### Critical Fields for HTML Panels

According to `.claude_research/TRELLISCOPEJS_LIB_PANEL_INTERFACE_RESEARCH.json`:

**Top-level panelInterface** (sibling to metas):
```json
{
  "type": "iframe",        // Must be "iframe" for HTML
  "panelCol": "panel",
  "base": "panels"         // Base directory for panel files
}
```

**Panel meta in metas array**:
```json
{
  "varname": "panel",
  "type": "panel",
  "paneltype": "iframe",   // MUST match panelInterface.type
  "source": {
    "type": "file",
    "isLocal": true
  },
  "aspect": 1.0
}
```

## Comparison: Python vs Spec

### What We Have ✓
1. ✓ Top-level `panelInterface` with `type: "iframe"`
2. ✓ Panel files are valid HTML
3. ✓ Panel paths in cogData are correct (`"0.html"`)
4. ✓ Panel meta has `type: "panel"`
5. ✓ Panel source is `type: "file"` with `isLocal: true`

### What's Wrong ❌
1. ❌ Panel meta has `paneltype: "img"` instead of `paneltype: "iframe"`
2. ❌ Inconsistency between panelInterface.type and meta.paneltype

## Expected vs Actual Viewer Behavior

### Expected Flow for HTML Panels
1. Viewer reads `panelInterface.type === "iframe"`
2. Viewer reads panel meta `paneltype === "iframe"`
3. Viewer creates `<iframe>` elements
4. Viewer loads `panels/0.html` into iframe
5. Interactive Plotly chart displays

### Actual Flow (Current Bug)
1. Viewer reads `panelInterface.type === "iframe"` ✓
2. Viewer reads panel meta `paneltype === "img"` ❌
3. **CONFLICT**: Viewer confused about element type
4. Falls back to showing "No Image" placeholder

## File Structure Comparison

### Python Output
```
refinery_plotly/
├── config.json
└── displays/
    └── refinery_plotly/
        ├── displayInfo.json       # Has panelInterface
        ├── metaData.json          # Has cogData
        ├── metaData.js            # JavaScript wrapper
        └── panels/
            ├── 0.html             # Self-contained Plotly
            ├── 1.html
            └── ...
```

### R Output (Old Viewer - JSONP)
```
r_example/appfiles/
├── config.jsonp
└── displays/
    └── common/
        └── refinery_by_country/
            ├── displayObj.jsonp   # JSONP format
            ├── cogData.jsonp
            └── jsonp/
                ├── Algeria.jsonp  # Panel data in JSONP
                └── ...
```

**Note**: R example uses completely different format incompatible with modern viewer.

## Modern Viewer Requirements (v0.7.16)

Based on research:

### Required Top-Level Fields
```json
{
  "name": "...",
  "group": "common",
  "description": "...",
  "keysig": "...",
  "n": 10,
  "height": 500,
  "width": 500,
  "tags": [],
  "keycols": [],
  "metas": [...],            // Must include panel meta
  "inputs": null,
  "cogInterface": {...},
  "cogInfo": {...},
  "cogDistns": {},
  "cogData": [...],
  "state": {...},
  "views": [],
  "primarypanel": "panel",
  "panelInterface": {...},   // REQUIRED - viewer needs this
  "imgSrcLookup": {}
}
```

### Panel Meta Structure for HTML
```json
{
  "varname": "panel",
  "type": "panel",
  "label": "Panel",
  "paneltype": "iframe",     // KEY FIX NEEDED
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
```

## Root Cause Analysis

### Code Location
The bug is in the panel meta generation code where we set:
```python
panel_meta = {
    "varname": panel_col,
    "type": "panel",
    "paneltype": "img",      # ← HARDCODED WRONG
    ...
}
```

### Why It Happens
1. Code likely defaults to `"img"` paneltype
2. Doesn't check actual file extension or panelInterface type
3. No logic to set paneltype based on panel format

### Where to Fix
Need to update code that creates panel meta to:
1. Check file extension (`.html` → `"iframe"`, `.png` → `"img"`)
2. OR check panelInterface.type and match it
3. OR accept paneltype as parameter when creating panel meta

## Solution

### Immediate Fix
Change panel meta generation to set:
```python
panel_meta["paneltype"] = "iframe"  # For HTML panels
```

### Proper Implementation
```python
def infer_paneltype(panel_files, panel_interface_type):
    """Infer paneltype from files or interface config"""
    if panel_interface_type == "iframe":
        return "iframe"

    # Check first file extension
    if panel_files:
        ext = panel_files[0].suffix.lower()
        if ext in ['.html', '.htm']:
            return "iframe"
        elif ext in ['.png', '.jpg', '.jpeg', '.svg']:
            return "img"

    return "img"  # Default fallback
```

### Update Display Class
```python
# In Display.write() or similar:
panel_interface_type = self.panel_interface.get("type", "file")
paneltype = infer_paneltype(panel_files, panel_interface_type)

panel_meta = {
    "varname": self.panel_col,
    "type": "panel",
    "paneltype": paneltype,  # Dynamic based on actual panels
    ...
}
```

## Testing Plan

1. **Update panel meta** to set `paneltype: "iframe"`
2. **Regenerate** displayInfo.json for refinery_plotly
3. **Test in browser** at `http://localhost:8002/`
4. **Verify**:
   - Panels load in iframes
   - Plotly interactivity works
   - No "No Image" errors
5. **Test dual support**: Create display with BOTH PNG and HTML panels

## Additional Considerations

### Dual Panel Type Support
Can we support both PNG and HTML in same display?
- **Answer**: Yes, but each panel must be one type
- **Implementation**: Set paneltype based on actual panel files
- **Use case**: Some panels are static images, others interactive HTML

### Panel Path Format
- ✓ Current format `"0.html"` is correct (no prefix)
- ✓ Base path `"panels"` is correct
- ✓ Viewer will construct: `panels/0.html`

### HTML Panel Best Practices
1. Self-contained HTML (all JS/CSS inline or CDN)
2. Fixed dimensions matching display height/width
3. No external dependencies that might fail in iframe
4. Plotly CDN links work fine

## Conclusion

**Single Fix Required**: Change `paneltype` from `"img"` to `"iframe"` in panel meta for HTML panels.

**Implementation Priority**: HIGH - This is a simple one-line fix that should resolve the issue.

**Testing Status**: Ready to test once fix is applied.

**Confidence**: HIGH - All other configuration is correct, this is the only mismatch.

---

**Next Steps**:
1. Locate panel meta generation code
2. Add logic to set paneltype based on file extension or interface type
3. Regenerate displayInfo.json
4. Test in browser
5. Document proper usage for mixed panel types
