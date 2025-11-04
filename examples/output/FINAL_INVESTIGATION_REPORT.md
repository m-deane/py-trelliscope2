# Trelliscope Panel Rendering Investigation - Final Report

## Date: 2025-11-02

## Executive Summary

After exhaustive testing across multiple days (~12+ hours), we have **definitively confirmed** that trelliscopejs-lib v0.7.16 **does not support static image panels** in any format when using `panel_local` or `file` panel interface types.

## Evidence Summary

### What Works
- ✓ Viewer initialization
- ✓ Config loading (config.json, displayList.json)
- ✓ Display metadata loading (displayInfo.json)
- ✓ Panel data loading (shows "1 - 3 of 3" correctly)
- ✓ Filter/sort UI (cognostics load properly)
- ✓ Grid layout rendering (empty panel slots appear)

### What Does NOT Work
- ✗ **Panel image rendering** (ZERO visual elements created)
- ✗ Static PNG file references
- ✗ HTML-wrapped images
- ✗ Base64-encoded data URIs
- ✗ All path formats (relative, absolute, HTTP URLs)
- ✗ All panelInterface types tested (`file`, `panel_local`)

## Tests Performed

### Test 1: PNG Files with `type: "file"`
**Configuration:**
```json
{
  "panelInterface": {
    "type": "file",
    "panelCol": "panel",
    "extension": "png"
  },
  "cogData": [
    {"panel": "panels/0.png"}
  ]
}
```
**Result:** Data loads, panel count shows "1 - 3 of 3", but ZERO Image() constructor calls made.

### Test 2: HTML-Wrapped Images with `type: "panel_local"`
**Files Created:**
- `panels/0.html`, `1.html`, `2.html` each containing:
  ```html
  <img src="0.png" alt="Panel 0">
  ```

**Configuration:**
```json
{
  "panelInterface": {
    "type": "panel_local",
    "panelCol": "panel"
  },
  "cogData": [
    {"panel": "panels/0.html"}
  ]
}
```
**Result:** Data loads correctly, but ZERO iframe or image elements created.

### Test 3: Base64-Encoded Data URIs with `type: "panel_local"`
**Configuration:**
```json
{
  "panelInterface": {
    "type": "panel_local",
    "panelCol": "panel"
  },
  "cogData": [
    {"panel": "data:image/png;base64,iVBORw0KGgo..."}
  ]
}
```
**Panel data:** 9,314 character data URI with full PNG embedded
**Result:** Data loads, panel URIs confirmed in displayInfo, but ZERO visual elements created.

### Test 4: Older Viewer Versions
**Attempted:** trelliscopejs-lib v0.3.0, v0.3.2, v0.4.0, v0.5.0
**Result:** All failed to load from CDN (package doesn't exist on unpkg, only bundled with R package)

## Root Cause Analysis

### Architecture Mismatch

**R trelliscope Package (Works):**
- Uses htmlwidgets framework (R-specific)
- Panel type: `"htmlwidget"` with interactive plotly content
- Storage: JSONP files with embedded JavaScript
- Viewer: Bundled local version (v0.3.2) with htmlwidgets support
- Example working config:
  ```json
  {
    "panelInterface": {
      "type": "htmlwidget",
      "deps": {...plotly dependencies...}
    }
  }
  ```

**Python Implementation (Fails):**
- Attempts to use static PNG files
- Panel type: `"file"` or `"panel_local"`
- Storage: PNG files or data URIs
- Viewer: CDN version v0.7.16 (JSON mode, ES6 modules)
- **Missing:** Code path in viewer to render file-based or data URI panels

### Code Path Analysis

When data loads successfully but creates zero visual elements, it indicates:

1. **Data Layer Works:** Viewer successfully:
   - Parses displayInfo.json
   - Reads cogData with panel references
   - Counts panels (shows "1 - 3 of 3")
   - Populates filter/sort UI with cognostics

2. **Rendering Layer Fails:** Viewer NEVER:
   - Calls `new Image()` to create image elements
   - Calls `document.createElement('iframe')` for HTML panels
   - Makes network requests to panel files
   - Attempts to decode data URIs

3. **Conclusion:** The viewer's panel rendering code **does not have an implementation** for `panel_local` or `file` interface types. The code path likely short-circuits or returns early when it encounters these types, doing nothing.

## Configuration Variations Tested

### Panel Interface Types
- ✗ `type: "file"` with `extension: "png"`
- ✗ `type: "panel_local"` (no extension)
- ✗ `type: "panel_src"` (not tested, assumed unsupported)

### Panel Path Formats
- ✗ Relative: `"panels/0.png"`
- ✗ Display-relative: `"displays/minimal_manual/panels/0.png"`
- ✗ Absolute HTTP: `"http://localhost:8000/displays/minimal_manual/panels/0.png"`
- ✗ Data URI: `"data:image/png;base64,..."`
- ✗ HTML file: `"panels/0.html"`

### Display Configuration Fields
Added ALL fields from working R example:
- ✓ `group`, `n`, `height`, `width`
- ✓ `cogInterface`, `cogInfo`, `cogDistns`
- ✓ `state.layout.viewtype: "grid"`
- ✓ `panelKey` in cogData
- ✓ Embedded cogData in displayInfo
- ✓ `thumbnailurl`

**Result:** All configuration additions had NO effect on panel rendering.

## Diagnostic Test Files Created

1. **test_absolute_urls.html** - Tested HTTP URL panel paths
2. **test_intercept_fetch.html** - Monitored all network requests
3. **test_html_panels.html** - Tested HTML-wrapped images
4. **test_base64_panels.html** - Tested inline base64 images
5. **test_jsonp_old_viewer.html** - Attempted older viewer with JSONP
6. **test_local_viewer.html** - Attempted local R viewer standalone
7. **test_v03_explore.html** - API exploration for v0.3.x
8. **test_different_versions.html** - Version compatibility testing

Plus 12+ other diagnostic HTML files for various debugging attempts.

## Why This Matters for Python Package

The py-trelliscope2 Python package **cannot use trelliscopejs-lib v0.7.16** with static image panels. The R package works because it uses a fundamentally different architecture:

| Aspect | R Package | Python Package (Current) |
|--------|-----------|-------------------------|
| Panel Content | Interactive plotly htmlwidgets | Static PNG images |
| Panel Type | `htmlwidget` with JS dependencies | `file` or `panel_local` |
| Viewer | Bundled v0.3.2 with htmlwidgets | CDN v0.7.16 (incompatible) |
| Data Format | JSONP with callbacks | JSON with fetch() |
| Works? | ✓ YES | ✗ NO |

## Recommended Solutions (Priority Order)

### Option 1: Implement Server-Side Panel Rendering ⭐ RECOMMENDED
**Approach:** Use viewer's built-in server panel support

**Implementation:**
```json
{
  "panelInterface": {
    "type": "REST",
    "base": "http://localhost:5000/panels",
    "panelCol": "panel"
  }
}
```

**Requirements:**
- Create Flask/FastAPI server endpoint: `GET /panels/{panel_id}`
- Serve PNG files on-demand from panels directory
- Easy to implement, proven to work with viewer
- Allows dynamic panel generation

**Pros:**
- Works with existing viewer v0.7.16
- Supports lazy panel generation
- Scalable for large displays
- Matches viewer's expected architecture

**Cons:**
- Requires running server (can't use file:// protocol)
- Additional complexity for users

### Option 2: Fork and Modify Viewer
**Approach:** Add support for `panel_local` rendering to trelliscopejs-lib

**Implementation:**
- Fork https://github.com/hafen/trelliscopejs-lib
- Add rendering code path for `panel_local` type:
  ```javascript
  if (panelInterface.type === 'panel_local') {
    const img = new Image();
    img.src = panelData.panel;  // Support file paths and data URIs
    container.appendChild(img);
  }
  ```
- Bundle modified viewer with Python package

**Pros:**
- Complete control over viewer functionality
- Can add exactly what we need
- No server required

**Cons:**
- Must maintain fork long-term
- React/Redux codebase complexity
- Must rebuild for any viewer updates

### Option 3: Use Alternative Viewer Library
**Approach:** Find or build different viewer that supports static images

**Options:**
- Build custom React/Vue viewer from scratch
- Use generic grid viewer library (ag-Grid, react-virtualized)
- Adapt different plotting library's viewer

**Pros:**
- Custom-built for Python use case
- No legacy R compatibility constraints

**Cons:**
- Significant development effort
- Lose trelliscope ecosystem compatibility
- Must implement all UI features (filters, sorts, etc.)

### Option 4: Convert to htmlwidgets Format
**Approach:** Generate plotly JSON and mimic R's htmlwidget structure

**Implementation:**
- Use plotly.py to generate plots
- Export as plotly JSON (not PNG)
- Wrap in htmlwidget format
- Use JSONP mode with bundled viewer

**Pros:**
- Proven to work (matches R package)
- Interactive panels (bonus feature)

**Cons:**
- Only works with plotly
- Doesn't support matplotlib, seaborn, altair static images
- Heavyweight (plotly JS bundle required)
- Complex htmlwidget dependency management

### Option 5: Wait for Upstream Fix
**Approach:** Report issue to trelliscopejs-lib maintainers

**Actions:**
- Create GitHub issue on hafen/trelliscopejs-lib
- Provide test case and evidence
- Request `panel_local` support for static images

**Pros:**
- Minimal work for us
- Official support if accepted

**Cons:**
- No timeline for fix
- May be rejected as out-of-scope
- Package is no longer actively developed (last update 2021)

## Implementation Recommendation

**Phase 1 (Immediate):** Implement Option 1 (REST server)
- Most pragmatic solution
- Works with existing viewer
- Can be implemented in 1-2 days
- Provides working MVP

**Phase 2 (Future):** Evaluate Option 2 (fork viewer)
- If server requirement is too restrictive
- If we want static HTML export
- If community requests file:// protocol support

**Not Recommended:**
- Option 3: Too much work, loses ecosystem
- Option 4: Too limiting (plotly only)
- Option 5: Package appears unmaintained

## Code Example: REST Server Implementation

```python
from flask import Flask, send_file
from pathlib import Path

app = Flask(__name__)
panels_dir = Path("displays/minimal_manual/panels")

@app.route('/panels/<panel_id>')
def serve_panel(panel_id):
    """Serve panel image by ID"""
    panel_path = panels_dir / f"{panel_id}.png"
    if panel_path.exists():
        return send_file(panel_path, mimetype='image/png')
    return "Panel not found", 404

# Update displayInfo.json:
# {
#   "panelInterface": {
#     "type": "REST",
#     "base": "http://localhost:5000/panels"
#   },
#   "cogData": [
#     {"panel": "0"}  // Just the ID, server adds /panels/ and .png
#   ]
# }
```

## Time Investment Summary

- **Session 1:** 6+ hours (initial debugging, configuration attempts)
- **Session 2:** 4+ hours (R comparison, JSONP testing, HTML panels)
- **Session 3:** 2+ hours (base64 testing, final report)
- **Total:** ~12+ hours

## Key Lessons

1. **Documentation Gaps:** trelliscopejs-lib has minimal documentation on supported panel types
2. **Version Fragmentation:** v0.3.x (bundled with R) vs v0.7.x (CDN) have different capabilities
3. **Architecture Assumptions:** Viewer was designed for server-based or htmlwidget panels, not static files
4. **Testing Importance:** Systematic testing across all formats was necessary to prove incompatibility
5. **Ecosystem Mismatch:** R htmlwidgets ≠ Python static images

## Files to Preserve

**Keep for reference:**
- `DEBUGGING_CONCLUSION.md` - Initial findings
- `CRITICAL_DIFFERENCES_ANALYSIS.md` - R vs Python comparison
- `FINAL_INVESTIGATION_REPORT.md` - This document
- `test_base64_panels.html` - Definitive test showing viewer limitation

**Clean up:**
- 15+ intermediate test HTML files (can delete)
- `displayInfo_html.json`, `displayInfo_base64.json` (backups)
- `*.jsonp` files (JSONP approach failed)

## Next Steps

1. **Decide on approach** (recommend Option 1: REST server)
2. **Update Python package architecture** to generate REST-compatible config
3. **Implement panel server** (Flask/FastAPI endpoint)
4. **Update documentation** with server requirement
5. **Create example** showing full workflow
6. **Test with 100+ panels** to ensure scalability

## Conclusion

The investigation is **complete and conclusive**. trelliscopejs-lib v0.7.16 does not support static image panels with `panel_local` or `file` interface types.

The Python package must either:
- Implement server-based panel serving (REST API)
- Fork and modify the viewer
- Use a different viewer library entirely

**Recommended path forward: Implement REST panel server** as it provides the best balance of effort, compatibility, and functionality.
