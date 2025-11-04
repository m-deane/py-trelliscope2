# React Dependencies Fix - Fourth Fix Applied

## Latest Error Fixed

You reported:
```
[Error] TypeError: undefined is not an object (evaluating 'e.__SECRET_INTERNALS_DO_NOT_USE_OR_YOU_WILL_BE_FIRED')
    nV (trelliscope-viewer.umd.cjs:10:153)
[Error] ReferenceError: Can't find variable: TrelliscopeApp
    Global Code (index.html:31)
```

## Root Cause

The error `__SECRET_INTERNALS_DO_NOT_USE_OR_YOU_WILL_BE_FIRED` is React's internal API object. The UMD build expects **React and ReactDOM to be loaded as global variables**, but we weren't loading them.

The trelliscopejs library is built with React 18.2.0 and expects it to be available before the library loads.

## The Fix

Added React and ReactDOM to the HTML, **loading before the trelliscope script**:

```html
<!-- Load React and ReactDOM before trelliscope (required for UMD build) -->
<script crossorigin src="https://unpkg.com/react@18.2.0/umd/react.production.min.js"></script>
<script crossorigin src="https://unpkg.com/react-dom@18.2.0/umd/react-dom.production.min.js"></script>
<!-- Load trelliscope viewer -->
<script src="https://unpkg.com/trelliscopejs-lib@0.7.16/dist/trelliscope-viewer.umd.cjs"></script>
```

## Implementation

**File**: `trelliscope/viewer.py` (lines 60-61, 115-116)

The React dependencies are now automatically included in all generated HTML files, loaded in the correct order:

1. **Process shim** (in `<head>`)
2. **React** (React core library)
3. **ReactDOM** (React DOM rendering)
4. **Trelliscope** (the actual viewer)

## Four-Stage Fix Summary

### Stage 1: 404 Error ✅
- **Problem**: Wrong filename `trelliscopejs-lib.js`
- **Solution**: Use correct package files

### Stage 2: Syntax Error ✅
- **Problem**: ESM build requires `<script type="module">`
- **Solution**: Use UMD build `trelliscope-viewer.umd.cjs`

### Stage 3: Process Variable Error ✅
- **Problem**: UMD references Node.js `process` variable
- **Solution**: Add browser shim for `window.process`

### Stage 4: React Dependencies Error (CURRENT) ✅
- **Problem**: UMD expects React/ReactDOM globals
- **Solution**: Load React and ReactDOM from CDN

## Verification

✅ **All 415 tests passing** (added test for React dependencies)
✅ **React and ReactDOM included in generated HTML**
✅ **Correct loading order verified**
✅ **Fresh test display generated**
✅ **Server running at http://localhost:8888/index.html**

## Test Now

The server has been restarted with a fresh display that includes all four fixes.

**→ Open: http://localhost:8888/index.html**

**Expected Result:**
- ✅ No console errors at all
- ✅ Trelliscope viewer loads completely
- ✅ 3 bar charts displayed
- ✅ Interactive controls work (sorting, filtering, layout)

**If you still see errors**, please share the complete console output.

## Why UMD Requires React

UMD (Universal Module Definition) builds can work in three modes:

1. **AMD (RequireJS)**: For module loaders
2. **CommonJS (Node.js)**: For server-side JavaScript
3. **Global (Browser)**: Creates/uses global variables

When used in a browser, the trelliscope UMD build:
- Expects `React` to exist as `window.React`
- Expects `ReactDOM` to exist as `window.ReactDOM`
- Creates `TrelliscopeApp` as `window.TrelliscopeApp`

Since React is a peer dependency (not bundled), we must load it separately.

## Complete Dependency Chain

```
Browser loads HTML
    ↓
Process shim creates window.process
    ↓
React script creates window.React
    ↓
ReactDOM script creates window.ReactDOM
    ↓
Trelliscope script uses React/ReactDOM to create window.TrelliscopeApp
    ↓
Our initialization code calls TrelliscopeApp.createApp()
    ↓
Viewer renders!
```

## Alternative Approach (Not Used)

We could have used the ESM build with `<script type="module">` instead:

```html
<script type="module">
  import { createApp } from 'https://unpkg.com/trelliscopejs-lib@0.7.16/dist/trelliscope-viewer.js';
  createApp({...});
</script>
```

However, this has downsides:
- Module scripts are deferred by default
- Harder to debug in browser console
- More complex initialization
- Compatibility concerns with older browsers

The UMD approach with global variables is simpler and more universally compatible.

## Status

🎉 **READY FOR FINAL TEST**

All four issues have been identified and fixed:
1. ✅ Correct JavaScript filename (UMD build)
2. ✅ Correct build format (UMD not ESM)
3. ✅ Browser shims for Node.js globals (process)
4. ✅ React dependencies loaded from CDN

Please test http://localhost:8888/index.html and report your results!
