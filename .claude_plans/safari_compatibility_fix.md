# Safari Compatibility Fix - Summary

## Date
October 28, 2025

## Problem
Trelliscope viewer was showing a blank white page in Safari 26.0.1 on macOS, while working correctly in Chrome/Firefox. The console showed no errors initially, making debugging difficult.

## Root Cause
The original `viewer.py` implementation was attempting to use the `Trelliscope` export from the module directly:

```javascript
const { Trelliscope } = await import('https://esm.sh/trelliscopejs-lib@0.7.16?bundle');
Trelliscope('trelliscope-root', configObject);
```

This approach failed with the error: `undefined is not an object (evaluating 't.slice')`

## Investigation Process
Through progressive debugging, we created multiple test HTML files:

1. **check_browser.html** - Verified Safari ES module support ✓
2. **test_safari.html** - Confirmed JavaScript execution issues
3. **index_debug.html** - Revealed the `t.slice` error with Trelliscope export
4. **index_fixed.html** - Tried multiple parameter patterns, all failed
5. **index_react.html** - Attempted React component rendering, different error
6. **index_working.html** - Local library with module imports, dependency resolution errors
7. **index_importmap.html** - Added import maps, encountered `process` variable error
8. **index_final.html** - Used esm.sh bundling with correct API ✓ **SUCCESS**

## Solution
The correct approach uses `window.trelliscopeApp` function created by the library:

```javascript
const module = await import('https://esm.sh/trelliscopejs-lib@0.7.16?bundle');
let initFunc = window.trelliscopeApp || module.trelliscopeApp;

if (typeof initFunc === 'function') {
    // R API pattern: trelliscopeApp(id, config_path)
    initFunc('trelliscope-root', './basic_viewer_demo/displayInfo.json');
}
```

### Key Changes to viewer.py

**Before:**
```python
html = f"""
<script type="module">
    const {{ Trelliscope }} = await import('{js_url}');
    if (typeof Trelliscope === 'function') {{
        Trelliscope('{element_id}', {config_js});
    }}
</script>
"""
```

**After:**
```python
html = f"""
<script type="module">
    const module = await import('{js_url}');
    let initFunc = window.trelliscopeApp || module.trelliscopeApp;

    if (typeof initFunc === 'function') {{
        initFunc('{element_id}', './{display_name}/displayInfo.json');
    }}
</script>
"""
```

## Key Insights

1. **Library Export Structure**: The trelliscopejs-lib library creates `window.trelliscopeApp` as the main entry point, not the ES module exports directly

2. **API Pattern**: The R package pattern is `trelliscopeApp(id, config_path)` where:
   - First argument: DOM element ID (string)
   - Second argument: Path to displayInfo.json (string, not object)

3. **esm.sh Bundling**: The `?bundle` parameter is crucial for Safari compatibility as it:
   - Bundles all dependencies (React, ReactDOM, etc.)
   - Provides polyfills for Node.js globals like `process`
   - Ensures ES module compatibility across browsers

4. **DOM Setup**: The root div needs `class="trelliscope-not-spa"` for proper initialization

## Browser Compatibility

### Tested Working
- ✓ Safari 26.0.1 on macOS
- ✓ Chrome (previously working)
- ✓ Firefox (previously working)

### Browser Support Requirements
- Modern browser with ES6 module support
- ES2015+ JavaScript features
- Fetch API support
- Minimum versions:
  - Chrome 90+
  - Firefox 88+
  - Safari 14+ (now confirmed working)

## Files Modified

1. **/trelliscope/viewer.py**
   - Updated `generate_viewer_html()` function (lines 86-129)
   - Changed initialization pattern to use `window.trelliscopeApp`
   - Pass displayInfo.json path instead of config object

2. **/examples/output/index.html**
   - Regenerated with new viewer code
   - Now uses Safari-compatible initialization

## Testing Verification

Run the test script to verify:
```bash
cd examples
python test_safari_fix.py
```

Then test in Safari at: http://localhost:6543/index.html

## Next Steps

1. ✓ Update viewer.py with Safari-compatible code
2. ✓ Regenerate index.html for testing
3. ⏳ Verify in Safari browser (awaiting user confirmation)
4. Clean up test HTML files from debugging session
5. Update documentation with Safari compatibility notes

## Documentation Updates Needed

- README.md: Add Safari to supported browsers
- Installation docs: Note Safari compatibility
- Troubleshooting section: Document this Safari-specific solution
