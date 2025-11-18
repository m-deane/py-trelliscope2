# JSONP Mode Test with Older Viewer

## Date: 2025-11-02

## Goal

Test whether older viewer versions (v0.3.x) with JSONP mode can render static PNG panel files.

## Hypothesis

The newer viewer (v0.7.16) in JSON mode doesn't support `panelInterface.type = "file"` for static PNG panels, but older versions using JSONP mode might support this use case since they were developed around the same time as the R package.

## Test Setup

### Files Created

1. **config.jsonp** - App configuration with `__loadDisplayList__()` callback
   - Sets `datatype: "jsonp"`
   - Includes displays array with minimal_manual display info
   - Uses `display_base: "displays"`

2. **displayInfo.jsonp** - Display configuration with `__loadDisplayObj__()` callback
   - Complete display configuration matching JSON version
   - Added: `group`, `n`, `height`, `width`
   - Added: `cogInterface`, `cogDistns`
   - Added: `panelInterface` with `type: "file"`, `extension: "png"`

3. **cogData.jsonp** - Panel metadata with `__loadCogData__()` callback
   - 3 rows of panel data
   - Panel paths as relative: `"panels/0.png"`, `"panels/1.png"`, `"panels/2.png"`
   - Includes `panelKey` field

4. **test_jsonp_old_viewer.html** - Test harness using trelliscopejs-lib@0.3.2
   - Intercepts all JSONP callbacks to confirm they fire
   - Intercepts Image() constructor to detect image creation
   - Logs all src assignments
   - 5-second diagnostic check

## Key Differences from JSON Mode

| Aspect | JSON Mode (v0.7.16) | JSONP Mode (v0.3.2) |
|--------|---------------------|---------------------|
| Data loading | fetch() API | JSONP callbacks via script tags |
| Callback names | N/A | `__loadDisplayList__`, `__loadDisplayObj__`, `__loadCogData__` |
| File protocol | Requires HTTP server | Works on file:// protocol |
| Panel paths | Absolute HTTP URLs tested | Relative paths (panels/0.png) |

## Expected Results

### Success Indicators
- ✓ JSONP callbacks fire successfully
- ✓ `Image()` constructor called 3 times
- ✓ Image src set to panel PNG paths
- ✓ Network requests made to panel images
- ✓ Images visible in viewer grid

### Failure Indicators
- ✗ JSONP callbacks fire but no Image() calls
- ✗ Same behavior as v0.7.16 (data loads, no images)
- ✗ Errors in console about panel interface

## Next Steps Based on Results

### If Test SUCCEEDS
- Older viewer DOES support file-based PNG panels
- **Solution**: Use v0.3.x with JSONP mode in Python package
- Update Python writer to generate JSONP files instead of JSON
- Bundle older viewer version or allow configuration

### If Test FAILS
- File-based PNG panels not supported in ANY viewer version
- **Next Option**: Try Option 2 (HTML-wrapped images)
  - Create HTML files with `<img>` tags pointing to PNGs
  - Use `panelInterface.type = "html"`
  - Store HTML files in panels/ directory

### Alternative Path
- Option 3: Base64 encode images directly in cogData
- Option 4: Implement REST panel source with custom API
- Option 5: Contact trelliscopejs maintainers

## Test Execution

1. Start HTTP server: `cd examples/output && python3 -m http.server 8000`
2. Open browser to: `http://localhost:8000/test_jsonp_old_viewer.html`
3. Observe console log for:
   - JSONP callback execution
   - Image() constructor calls
   - Image src assignments
4. Check viewer at 5-second mark:
   - Panel count display
   - Actual image visibility
   - Network tab for PNG requests

## Reference

- Previous debugging: DEBUGGING_CONCLUSION.md
- Working R example: r_example/index.html (uses htmlwidgets, not static PNGs)
- Critical differences: CRITICAL_DIFFERENCES_ANALYSIS.md
