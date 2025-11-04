# Plotly HTML Panel Fix - Final Report

## Problem Identified

**Issue**: Plotly HTML panels showing "No Image" in Trelliscope viewer
**Root Cause**: Hardcoded `paneltype: "img"` in panel meta, even when panels are HTML
**Location**: `/trelliscope/serialization.py`, line 100

## Technical Details

### Current Code Behavior

```python
# Line 164-168: Correctly detects HTML panels for panelInterface
panel_type = "file"  # Default to image files
if hasattr(display, '_panel_format'):
    panel_format = display._panel_format
    panel_type = "iframe" if panel_format == "html" else "file"

# Line 174: Correctly uses panel_type in panelInterface
panel_interface_dict = {
    "type": panel_type,  # ✓ "iframe" for HTML
    "panelCol": display.panel_column,
    "base": "panels",
}

# Line 100: HARDCODED WRONG - doesn't use panel_type
panel_meta = {
    "varname": display.panel_column,
    "type": "panel",
    "paneltype": "img",  # ❌ Always "img", should match panel_type
    ...
}
```

### The Inconsistency

| Field | Current Value | Should Be | Status |
|-------|---------------|-----------|--------|
| `panelInterface.type` | `"iframe"` | `"iframe"` | ✓ Correct |
| `panel_meta.paneltype` | `"img"` | `"iframe"` | ❌ Wrong |

This mismatch confuses the viewer - it doesn't know whether to create `<img>` or `<iframe>` elements.

## The Fix

### Code Change Required

In `/trelliscope/serialization.py`, update lines 95-104:

**BEFORE:**
```python
# Build panel meta variable
panel_meta = {
    "varname": display.panel_column,
    "type": "panel",
    "label": "Panel",
    "paneltype": "img",  # Default to image panels
    "tags": [],
    "filterable": False,
    "sortable": False,
}
```

**AFTER:**
```python
# Determine paneltype based on panel format
# This must match panelInterface.type for viewer consistency
paneltype = "img"  # Default for image panels
if hasattr(display, '_panel_format'):
    paneltype = "iframe" if display._panel_format == "html" else "img"

# Build panel meta variable
panel_meta = {
    "varname": display.panel_column,
    "type": "panel",
    "label": "Panel",
    "paneltype": paneltype,  # Dynamic based on actual panel format
    "tags": [],
    "filterable": False,
    "sortable": False,
}
```

### Alternative: Unified Detection

Better approach - detect once and reuse:

```python
def serialize_display_info(display) -> Dict[str, Any]:
    # ... existing code ...

    # MOVED BEFORE panel meta creation
    # Detect panel type once
    panel_type = "file"  # "file" for images, "iframe" for HTML
    paneltype = "img"    # "img" for <img>, "iframe" for <iframe>

    if display.panel_column is not None:
        if hasattr(display, '_panel_format'):
            if display._panel_format == "html":
                panel_type = "iframe"
                paneltype = "iframe"
            else:
                panel_type = "file"
                paneltype = "img"

    # ... then use paneltype in panel_meta (line ~100) ...
    panel_meta = {
        "varname": display.panel_column,
        "type": "panel",
        "label": "Panel",
        "paneltype": paneltype,  # Use detected value
        ...
    }

    # ... and use panel_type in panelInterface (line ~174) ...
    panel_interface_dict = {
        "type": panel_type,  # Use detected value
        ...
    }
```

## Verification Steps

1. **Apply the fix** to `serialization.py`
2. **Regenerate displays**:
   ```bash
   cd examples
   python 04_plotly_demo.py  # Or whatever creates refinery_plotly
   ```
3. **Check displayInfo.json**:
   ```bash
   cat examples/output/refinery_plotly/displays/refinery_plotly/displayInfo.json
   ```
   Verify:
   - `panelInterface.type === "iframe"` ✓
   - `metas[].paneltype === "iframe"` ✓ (should now match)

4. **Test in browser**:
   ```bash
   cd examples/output/refinery_plotly
   python3 -m http.server 8000
   ```
   Open: `http://localhost:8000/`

5. **Expected result**:
   - Panels load in iframes
   - Plotly charts display correctly
   - Interactive features work (hover, zoom, pan)
   - No "No Image" errors

## Additional Findings

### Panel Path Format
✓ **Correct**: Panel paths in cogData are `"0.html"`, `"1.html"`, etc.
✓ **Correct**: Base path is `"panels"` in panelInterface
✓ **Correct**: Viewer will construct full path as `panels/0.html`

### HTML Panel Structure
✓ **Correct**: Plotly HTML files are self-contained
✓ **Correct**: CDN links for Plotly.js are included
✓ **Correct**: Fixed dimensions (500x400) match display config

### Metadata Files
✓ **Correct**: metaData.json exists
✓ **Correct**: metaData.js exists with window.metaData wrapper
✓ **Correct**: Both contain cogData with panel references

## R vs Python Comparison

### R Implementation (Old Viewer)
- Uses JSONP format with callback wrappers
- Panel type: `htmlwidget` with dependency declarations
- **Not compatible** with modern viewer (v0.7.16)
- Found in: `examples/output/r_example/`

### Python Implementation (Modern Viewer)
- Uses JSON format (no callbacks)
- Panel type: `iframe` for HTML, `file` for images
- **Compatible** with trelliscopejs-lib v0.7.16
- Found in: `examples/output/refinery_plotly/`

**Note**: Don't use R example as reference - it's for the old viewer!

## Testing Checklist

- [ ] Apply code fix to `serialization.py`
- [ ] Regenerate Plotly display
- [ ] Verify `paneltype: "iframe"` in displayInfo.json
- [ ] Test in browser - panels should load
- [ ] Verify Plotly interactivity works
- [ ] Test PNG display still works (no regression)
- [ ] Create mixed display (PNG + HTML) to test dual support

## Confidence Level

**Fix Confidence**: 99%

**Reasoning**:
1. Problem clearly identified via code inspection
2. Root cause is single hardcoded value
3. Fix is straightforward 1-line change
4. All other configuration verified correct
5. Matches specification from research documents

**Risk**: Very Low - only affects panel meta creation, no breaking changes

## Next Steps

1. **Immediate**: Apply the fix described above
2. **Test**: Regenerate and verify in browser
3. **Document**: Update user guide with HTML panel usage
4. **Extend**: Add support for panel type auto-detection from file extensions
5. **Future**: Support mixed displays (some panels PNG, others HTML)

---

**Status**: Ready to implement
**Priority**: HIGH
**Effort**: 5 minutes
**Impact**: Fixes all HTML panel displays
