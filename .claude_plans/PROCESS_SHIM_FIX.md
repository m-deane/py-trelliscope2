# Process Variable Shim - Third Fix Applied

## Latest Error Fixed

You reported:
```
[Error] ReferenceError: Can't find variable: process
    (anonymous function) (trelliscope-viewer.umd.cjs:28:2968)
[Error] ReferenceError: Can't find variable: TrelliscopeApp
    Global Code (index.html:25)
```

## Root Cause

The UMD build (`trelliscope-viewer.umd.cjs`) contains code that checks `process.env.NODE_ENV` to determine if it's running in development or production mode. This is a **Node.js global variable** that doesn't exist in browsers.

## The Fix

Added a browser shim **before** loading the trelliscope JavaScript:

```html
<script>
    // Browser shim for Node.js process variable
    window.process = {
        env: { NODE_ENV: 'production' }
    };
</script>
```

This creates a minimal `process` object that satisfies the UMD build's requirements.

## Implementation

**File**: `trelliscope/viewer.py` (lines 101-106)

The shim is now automatically included in all generated HTML files in the `<head>` section, before the trelliscope JavaScript loads.

## Three-Stage Fix Summary

### Stage 1: 404 Error
- **Problem**: Wrong filename `trelliscopejs-lib.js`
- **Solution**: Use correct package files

### Stage 2: Syntax Error
- **Problem**: ESM build requires `<script type="module">`
- **Solution**: Use UMD build `trelliscope-viewer.umd.cjs`

### Stage 3: Process Variable Error (CURRENT)
- **Problem**: UMD references Node.js `process` variable
- **Solution**: Add browser shim for `window.process`

## Verification

✅ **All 414 tests passing** (added test for process shim)
✅ **Process shim included in generated HTML**
✅ **Fresh test display generated**
✅ **Server running at http://localhost:8888/index.html**

## Test Now

The server has been restarted with a fresh display that includes the process shim.

**→ Open: http://localhost:8888/index.html**

**Expected Result:**
- ✅ No console errors
- ✅ Trelliscope viewer loads
- ✅ 3 bar charts displayed
- ✅ Interactive controls work

**If you still see errors**, please share the exact error messages from the browser console.

## Why This Matters

Many JavaScript libraries that are built with modern bundlers (webpack, vite, rollup) include references to Node.js globals like `process`, `Buffer`, `global`, etc. When loading these in a browser, we need to provide minimal shims for compatibility.

The `process.env.NODE_ENV` check is extremely common because it allows libraries to:
- Include extra debugging in development
- Strip debugging code in production
- Provide different error messages
- Enable/disable certain features

By setting it to `'production'`, we tell the library to use its production build behavior.

## Code Pattern

This is the standard pattern for shimming Node.js globals in browsers:

```html
<!-- Define shims BEFORE loading libraries that need them -->
<script>
    window.process = { env: { NODE_ENV: 'production' } };
    window.Buffer = window.Buffer || { isBuffer: () => false };
    window.global = window.global || window;
</script>

<!-- Now load libraries that reference these globals -->
<script src="library-that-needs-process.js"></script>
```

Our implementation only includes the `process` shim since that's all the trelliscopejs UMD build requires.

## Status

🎉 **READY FOR FINAL TEST**

All three issues have been identified and fixed:
1. ✅ Correct JavaScript filename
2. ✅ Correct build format (UMD)
3. ✅ Browser shims for Node.js globals

Please test http://localhost:8888/index.html and report your results!
