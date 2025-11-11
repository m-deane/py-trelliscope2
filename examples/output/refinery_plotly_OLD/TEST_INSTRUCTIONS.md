# Categorical Filter Fix - Testing Instructions

## Status
- **Data**: ✅ Confirmed numeric (country: 0, 1, 2...) in displayInfo.json
- **Viewer**: ✅ Patched and built (Nov 5 22:20:31)
- **Fix Applied**: ✅ Two bugs fixed in getLabelFromFactor
- **Integration**: ✅ Patched viewer bundled with py-trelliscope2

## The Two Bugs That Were Fixed

### Bug 1: Falsy Check Treating 0 as Invalid
```typescript
// BEFORE (BUGGY):
if (!factor || factor === -Infinity) {
    return MISSING_TEXT;
}
// Problem: !0 is true in JavaScript, so index 0 was treated as invalid!

// AFTER (FIXED):
if (factor === null || factor === undefined || factor === -Infinity) {
    return MISSING_TEXT;
}
// Solution: Explicit checks that allow 0 as a valid index
```

### Bug 2: Off-by-One Error (R-style indexing)
```typescript
// BEFORE (BUGGY):
return levels[factor - 1];  // R uses 1-indexed factors

// AFTER (FIXED):
return levels[factor];  // JavaScript uses 0-indexed arrays
```

## Testing URLs

### Test 1: No-Cache Diagnostic (Most Reliable)
**URL**: http://localhost:8764/test_no_cache.html

This test:
- Forces fresh load with `cache: 'no-store'`
- Shows response headers (cache status)
- Validates data format (numeric vs string)
- Tests the getLabelFromFactor logic
- Shows raw cogData entries

**Expected Results**:
- ✅ "First country value: 0 (type: number)"
- ✅ All cogData entries show numeric indices
- ✅ Manual lookup test shows correct labels
- ✅ "Final Verdict: All country values are numeric indices (CORRECT)"

### Test 2: Cache-Busting Test
**URL**: http://localhost:8764/test_cache_bust.html

This test:
- Uses timestamp query parameters `?v=${timestamp}`
- Shows diagnostic info about data loading
- Tests factor-to-label conversion

**Expected Results**:
- ✅ "First country value: 0 (number)"
- ✅ Lookup shows: `0 → "Algeria"`
- ✅ Buggy logic: "[missing]" (for index 0)
- ✅ Fixed logic: "Algeria"

### Test 3: Main Viewer
**URL**: http://localhost:8764/

The production viewer using patched assets.

**How to Test**:
1. Open http://localhost:8764/ in a fresh incognito window
2. Press Cmd+Shift+R (hard refresh) to clear cache
3. Click the filter panel icon (left sidebar with funnel icon)
4. Locate the "Country" filter
5. Check the histogram bars

**Expected Results**:
- ✅ Histogram shows country names: Algeria, Denmark, Germany, Italy, Netherlands, Norway, Romania, Russian Federation, Turkey, United Kingdom
- ✅ NOT "[missing]"
- ✅ Can click on bars to filter by country
- ✅ Count numbers appear next to each country

### Test 4: Patched Viewer Test
**URL**: http://localhost:8764/index_PATCHED.html

Uses the viewer from `viewer-patched/` directory.

**Expected Results**: Same as Test 3

## If Still Showing [missing]

### Step 1: Verify Browser Cache is Clear
1. Open DevTools (Cmd+Option+I)
2. Go to Network tab
3. Check "Disable cache" checkbox
4. Hard refresh (Cmd+Shift+R)

### Step 2: Check What's Being Loaded
1. In Network tab, look for:
   - `displayInfo.json` request
   - Check Status: Should be 200 (not 304)
   - Check Response tab
   - Look for `cogData[0].country`
   - Should be: `0` (number)
   - Should NOT be: `"Algeria"` (string)

2. Also check for:
   - `viewer/assets/index.js` request
   - Check Status: Should be 200
   - Check Size: Should be ~1.6 MB

### Step 3: Check Console for Errors
1. Open Console tab in DevTools
2. Look for any errors in red
3. Common issues:
   - "Failed to fetch" → Server not running
   - "404" → Files missing
   - "Unexpected token" → JSON parse error

### Step 4: Verify Server is Running
```bash
# Check if server is running on port 8764
lsof -i :8764

# If not, restart:
cd "/Users/matthewdeane/Documents/Data Science/python/_projects/py-trelliscope2/examples/output/refinery_plotly"
python3 -m http.server 8764
```

## Data Format Verification

The JSON files have been converted to use numeric indices:

```json
{
  "country": 0,          // ✅ Numeric (correct)
  "avg_capacity": 497.7,
  "panelKey": "0"
}
```

NOT:
```json
{
  "country": "Algeria",  // ❌ String (incorrect)
  "avg_capacity": 497.7,
  "panelKey": "0"
}
```

To verify manually:
```bash
cd "/Users/matthewdeane/Documents/Data Science/python/_projects/py-trelliscope2/examples/output/refinery_plotly/displays/refinery_plotly"
python3 -c "import json; print(json.load(open('displayInfo.json'))['cogData'][0]['country'])"
# Should output: 0
```

## Viewer Build Information

- **Source**: `trelliscopejs-lib-patched/src/utils.ts`
- **Built**: Nov 5, 2025 22:20:31
- **Size**: 1.6 MB (index.js) + 68 KB (index.css)
- **Location**: `viewer/assets/index.js`

Viewer was built AFTER the fix was applied to source.

## Technical Details

### Factor Data Flow
1. Python generates display with factor strings
2. `serialization.py` converts strings to 0-based indices during cogData generation
3. JSON files store numeric indices (0, 1, 2...)
4. Viewer loads JSON and uses numeric index to look up label
5. Fixed `getLabelFromFactor` allows 0 as valid index and uses direct array access

### Browser Caching Issues
The Python `http.server` doesn't set proper cache headers, so browsers aggressively cache:
- JSON files (displayInfo.json)
- JavaScript files (index.js)
- CSS files (index.css)

**Solution**: Use no-cache test page or incognito mode with hard refresh.

## Success Criteria

✅ Diagnostic shows: "All country values are numeric indices (CORRECT)"
✅ Main viewer shows country names in filter histogram
✅ Can click country names to filter data
✅ No "[missing]" labels anywhere

## Next Steps if Issues Persist

1. **Check if JSON was actually updated**: Run `examples/fix_refinery_json.py` again
2. **Verify viewer has fix**: Check source at `trelliscopejs-lib-patched/src/utils.ts` line 30
3. **Rebuild viewer**: `cd trelliscopejs-lib-patched && npm run build`
4. **Re-copy assets**: Copy `dist/assets/*` to `examples/output/refinery_plotly/viewer/assets/`
5. **Test in different browser**: Try Firefox, Chrome, Safari to rule out browser-specific caching

## Contact

If issues persist after following all steps, provide:
1. Screenshot of test_no_cache.html output
2. Network tab screenshot showing displayInfo.json response
3. Console tab screenshot showing any errors
4. Output of: `python3 -c "import json; print(json.load(open('displays/refinery_plotly/displayInfo.json'))['cogData'][0])"`
