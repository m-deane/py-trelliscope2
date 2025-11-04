# Browser Testing Guide - REST Panel Integration

## Date: 2025-11-02
## Status: Ready for Manual Browser Testing
## Test Page: `examples/output/test_rest_integration.html`

---

## Overview

This guide provides step-by-step instructions for manually testing the REST panel integration in a web browser. The test validates that:

1. Forked viewer loads correctly
2. REST panel metadata is properly configured
3. Panels load via HTTP API
4. Viewer UI interactions work (filter, sort, labels)
5. No console errors occur

---

## Prerequisites

### 1. Panel Server Running

```bash
# Verify server is running on port 5001
$ curl http://localhost:5001/api/health
{
  "status": "ok",
  "output_dir": "/path/to/output",
  "displays_dir_exists": true
}
```

**If not running:**
```bash
$ cd examples
$ python panel_server.py
# Server starts on http://localhost:5001
```

### 2. Test Display Created

```bash
# Verify rest_demo display exists
$ ls examples/output/rest_demo/
displayInfo.json  metadata.csv

# Check displayInfo.json has REST panel metadata
$ cat examples/output/rest_demo/displayInfo.json | jq '.metas[] | select(.type == "panel")'
{
  "varname": "panel",
  "type": "panel",
  "source": {
    "type": "REST",
    "url": "http://localhost:5001/api/panels/minimal_manual"
  }
}
```

### 3. Viewer Files in Place

```bash
# Check viewer assets
$ ls examples/output/
assets/       # Forked viewer assets
index.html    # Viewer entry point
rest_demo/    # Test display
```

---

## Test Procedure

### Step 1: Open Test Page

```bash
# Open browser test page
$ open examples/output/test_rest_integration.html

# Or navigate to:
http://localhost:5001/test_rest_integration.html
```

**Expected Result:**
- Page loads with header "REST Panel Integration - Browser Test"
- Pre-flight checks run automatically
- Status indicators show green checkmarks
- Log console shows successful tests
- Viewer iframe loads display

### Step 2: Verify Pre-Flight Checks

The test page automatically runs these checks:

**✅ Panel Server**
- Connects to http://localhost:5001/api/health
- Verifies server is responding
- Status: "Connected ✓"

**✅ Display Metadata**
- Loads displayInfo.json
- Finds panel metadata
- Verifies source.type === "REST"
- Status: "REST config valid ✓"

**✅ Panel Endpoints**
- Tests /api/panels/minimal_manual/0, /1, /2
- Verifies all return 200 OK
- Checks Content-Type: image/png
- Status: "3/3 endpoints OK ✓"

**✅ Viewer Assets**
- Checks for /assets/index.js
- Verifies viewer files loaded
- Status: "Assets loaded ✓"

**Expected Log Output:**
```
============================================================
STARTING REST PANEL INTEGRATION TESTS
============================================================
[timestamp] Checking panel server health...
[timestamp] ✓ Panel server is running
[timestamp] Loading displayInfo.json...
[timestamp] ✓ displayInfo.json loaded
[timestamp] ✓ REST panel source configured correctly!
[timestamp] Testing panel endpoints...
[timestamp] ✓ Panel 0: 200 OK (image/png, 6967 bytes)
[timestamp] ✓ Panel 1: 200 OK (image/png, 6854 bytes)
[timestamp] ✓ Panel 2: 200 OK (image/png, 7012 bytes)
[timestamp] ✓ All 3 panel endpoints responding!
[timestamp] Checking viewer assets...
[timestamp] ✓ Viewer assets found
============================================================
[timestamp] ✓ ALL TESTS PASSED!
============================================================
```

### Step 3: Open Browser DevTools

**Chrome/Edge:**
- Press F12 or Cmd+Option+I (Mac)
- Go to "Network" tab
- Click "Filter" icon and type "panels"

**Firefox:**
- Press F12 or Cmd+Option+I (Mac)
- Go to "Network" tab
- Type "panels" in filter box

**Safari:**
- Enable Developer menu: Preferences → Advanced → Show Develop menu
- Press Cmd+Option+I
- Go to "Network" tab
- Type "panels" in filter

### Step 4: Verify REST Panel Requests

**What to Look For:**

1. **Panel Requests Appear**
   ```
   GET /api/panels/minimal_manual/0   200 OK   image/png   6.9 KB
   GET /api/panels/minimal_manual/1   200 OK   image/png   6.8 KB
   GET /api/panels/minimal_manual/2   200 OK   image/png   7.0 KB
   ```

2. **Request Headers**
   - Method: GET
   - Status: 200
   - Type: image/png
   - Size: ~7KB per panel

3. **Response Headers**
   ```
   HTTP/1.1 200 OK
   Content-Type: image/png
   Content-Length: 6967
   Access-Control-Allow-Origin: *
   ```

4. **Timing**
   - Initial load: 100-500ms per panel
   - Cached loads: <50ms

**Success Criteria:**
- ✅ All panel requests return 200 OK
- ✅ Content-Type is image/png
- ✅ No 404 or 500 errors
- ✅ Panels load within reasonable time

### Step 5: Visual Inspection

**Check the Viewer Display:**

1. **Panel Grid Visible**
   - 3 panel cards displayed
   - Arranged in 3 columns (as configured)
   - Each panel shows an image (not "No Image")

2. **Panel Images Rendered**
   - Images are visible and not broken
   - Correct aspect ratio (1:1)
   - Clear, not pixelated

3. **Metadata Labels**
   - Category labels visible (A, B, C)
   - Value labels visible (0, 10, 20)
   - Labels positioned correctly below panels

**Expected Visual:**
```
┌─────────────┬─────────────┬─────────────┐
│   Panel 0   │   Panel 1   │   Panel 2   │
│  [IMAGE]    │  [IMAGE]    │  [IMAGE]    │
│  Category: A│  Category: B│  Category: C│
│  Value: 0   │  Value: 10  │  Value: 20  │
└─────────────┴─────────────┴─────────────┘
```

### Step 6: Test Viewer Interactions

**Test 1: Filter by Category**
1. Click "Filters" button in sidebar
2. Select "Category" filter
3. Check "A" and "B" (uncheck "C")
4. Click "Apply"
5. Verify: Only panels 0 and 1 visible

**Test 2: Sort by Value**
1. Click "Sort" button in sidebar
2. Add sort: "Value", descending
3. Click "Apply"
4. Verify: Panels reorder (2, 1, 0)

**Test 3: Change Labels**
1. Click "Labels" button in sidebar
2. Deselect "Value"
3. Click "Apply"
4. Verify: Only Category labels shown

**Test 4: Layout Changes**
1. Change columns to 2 (dropdown or input)
2. Verify: Panels rearrange to 2-column grid
3. Change back to 3 columns

**Success Criteria:**
- ✅ Filters work correctly
- ✅ Sorting works correctly
- ✅ Labels update correctly
- ✅ Layout changes work
- ✅ No errors in console

### Step 7: Console Error Check

**Open Console Tab:**
- Look for any JavaScript errors (red text)
- Check for warnings (yellow text)
- Verify no "Failed to load" messages

**Expected: Clean Console**
```javascript
// Should see messages like:
Viewer initialized
Loading display: rest_demo
Fetching displayInfo.json
Display loaded successfully
Rendering 3 panels

// Should NOT see:
❌ Error loading panel
❌ Failed to fetch
❌ TypeError: Cannot read property...
❌ CORS error
```

**Common Errors and Solutions:**

1. **CORS Error**
   ```
   Access to fetch at 'http://localhost:5001' from origin 'http://localhost:8000'
   has been blocked by CORS policy
   ```
   **Solution:** Panel server already has CORS enabled. Check server logs.

2. **404 Not Found**
   ```
   GET /api/panels/minimal_manual/0 404 (Not Found)
   ```
   **Solution:** Check panel_server.py is running and display exists.

3. **Network Error**
   ```
   Failed to fetch
   ```
   **Solution:** Verify panel server is running on port 5001.

---

## Automated Test Page Features

### Test Console

The test page includes an interactive console with these buttons:

**Run All Tests**
- Executes all pre-flight checks
- Shows pass/fail status
- Logs detailed results

**Clear Logs**
- Clears test console
- Resets log history

**Test Panel Load**
- Loads a single panel
- Shows response details
- Useful for debugging

### Status Indicators

Four status boxes show real-time check results:

1. **Panel Server** - Server connectivity
2. **Display Metadata** - JSON configuration
3. **Panel Endpoints** - REST API responses
4. **Viewer Assets** - File availability

**Colors:**
- 🟢 Green: Success
- 🟡 Yellow: Pending/In Progress
- 🔴 Red: Error/Failed

---

## Expected Results Summary

### ✅ Success Indicators

**Visual:**
- ✅ 3 panels displayed in grid
- ✅ Images loaded and visible
- ✅ Labels showing correct data
- ✅ Layout responsive

**Network:**
- ✅ 3 successful panel API requests
- ✅ All return 200 OK
- ✅ Content-Type: image/png
- ✅ Reasonable load times

**Console:**
- ✅ No errors
- ✅ Display loads successfully
- ✅ Panels render without issues

**Interactions:**
- ✅ Filtering works
- ✅ Sorting works
- ✅ Labels toggle works
- ✅ Layout changes work

### ❌ Failure Indicators

**Visual:**
- ❌ "No Image" placeholders
- ❌ Broken image icons
- ❌ Missing panels
- ❌ Layout issues

**Network:**
- ❌ 404 errors on panel requests
- ❌ 500 server errors
- ❌ CORS errors
- ❌ Timeouts

**Console:**
- ❌ JavaScript errors
- ❌ Failed to load messages
- ❌ TypeError exceptions
- ❌ Network errors

---

## Troubleshooting

### Issue 1: Panel Server Not Running

**Symptoms:**
- Connection refused errors
- 404 on /api/health
- No panel requests in Network tab

**Solution:**
```bash
$ cd examples
$ python panel_server.py
# Server should start on http://localhost:5001
```

### Issue 2: Wrong Panel URLs

**Symptoms:**
- 404 on panel requests
- Correct URL format but wrong display name

**Solution:**
Check displayInfo.json panel source URL matches panel_server.py routes:
```json
{
  "source": {
    "url": "http://localhost:5001/api/panels/minimal_manual"
  }
}
```

### Issue 3: Viewer Not Loading

**Symptoms:**
- Blank iframe
- No viewer UI
- Missing assets errors

**Solution:**
```bash
# Verify viewer files exist
$ ls examples/output/assets/
# Should see index.js, index.css, etc.

# Re-copy from fork if needed
$ cp -r viewer_fork/trelliscopejs-lib/dist/* examples/output/
```

### Issue 4: Panels Not Rendering

**Symptoms:**
- "No Image" placeholders
- Broken images
- Requests succeed but images don't show

**Solution:**
1. Check panel server logs for errors
2. Verify Content-Type: image/png in responses
3. Test panel URL directly in browser
4. Check image file exists in panels directory

---

## Performance Benchmarks

### Expected Load Times

**Initial Page Load:**
- Test page: < 1 second
- Viewer initialization: 1-2 seconds
- displayInfo.json: < 100ms
- All 3 panels: 300-1500ms total

**Panel Loading:**
- Single panel: 100-500ms (uncached)
- Single panel: < 50ms (cached)
- Parallel loading: 6 panels concurrently

**Interactions:**
- Filter application: < 200ms
- Sort application: < 200ms
- Label toggle: < 100ms
- Layout change: < 300ms

### Performance Tips

1. **Browser caching** dramatically improves repeat loads
2. **Parallel loading** - browser loads up to 6 panels simultaneously
3. **Panel size** affects load time - optimize images for web
4. **Network latency** - localhost is fast, remote slower

---

## Advanced Testing

### Testing with Different Displays

Create new test displays:

```python
import pandas as pd
from trelliscope import Display, RESTPanelInterface

# Larger display
data = pd.DataFrame({
    'panel': [str(i) for i in range(100)],
    'value': range(100)
})

display = (Display(data, name="large_test")
    .set_panel_column("panel")
    .set_panel_interface("rest",
        base="http://localhost:5001/api/panels/large_test")
    .write(render_panels=False))
```

Then test:
```bash
$ open http://localhost:5001/large_test
```

### Testing with Remote API

Configure remote REST endpoint:

```python
display.set_panel_interface("rest",
    base="https://api.example.com/panels/my_display",
    api_key="secret_key")
```

Verify in Network tab:
- Requests go to remote URL
- Authorization header includes API key
- CORS headers present

---

## Test Checklist

Use this checklist for complete browser testing:

### Pre-Flight
- [ ] Panel server running on port 5001
- [ ] rest_demo display created
- [ ] Viewer files in place
- [ ] Test page accessible

### Automated Tests
- [ ] All pre-flight checks pass (green)
- [ ] Panel server connected
- [ ] displayInfo.json valid
- [ ] Panel endpoints responding
- [ ] Viewer assets loaded

### Network Tab
- [ ] 3 panel requests visible
- [ ] All return 200 OK
- [ ] Content-Type: image/png
- [ ] Reasonable response times
- [ ] No errors or warnings

### Visual
- [ ] 3 panels displayed
- [ ] Images loaded correctly
- [ ] Labels showing data
- [ ] Layout correct (3 columns)
- [ ] No broken images

### Console
- [ ] No JavaScript errors
- [ ] No failed requests
- [ ] No TypeErrors
- [ ] No CORS errors

### Interactions
- [ ] Filtering works
- [ ] Sorting works
- [ ] Labels toggle works
- [ ] Layout changes work
- [ ] No errors during interaction

### Performance
- [ ] Page loads in < 5 seconds
- [ ] Panels load in < 2 seconds total
- [ ] Interactions feel responsive
- [ ] No lag or freezing

---

## Success Criteria

**Minimum Success:**
- ✅ Viewer loads
- ✅ 3 panels visible
- ✅ REST API calls successful
- ✅ No console errors

**Complete Success:**
- ✅ All above
- ✅ All interactions work
- ✅ Performance acceptable
- ✅ Test page checks pass

**Exceptional Success:**
- ✅ All above
- ✅ Tested with multiple displays
- ✅ Tested with 100+ panels
- ✅ Tested on multiple browsers
- ✅ Documented any issues found

---

## Browser Compatibility

### Recommended Browsers

**Chrome/Edge (Chromium):**
- ✅ Full support
- ✅ Best DevTools
- ✅ Fast rendering

**Firefox:**
- ✅ Full support
- ✅ Good DevTools
- ✅ Standards compliant

**Safari:**
- ✅ Full support
- ⚠️  DevTools less detailed
- ✅ Good performance

### Known Issues

**Safari:**
- May require enabling Developer menu
- DevTools filter less intuitive
- CORS handling stricter

**Firefox:**
- Network tab timing slightly different
- Cache behavior may differ

**All Browsers:**
- Requires JavaScript enabled
- Requires network access to localhost
- May need CORS for remote APIs

---

## Next Steps After Testing

### If All Tests Pass ✅

1. **Document Results**
   - Screenshot of successful test
   - Save Network tab HAR file
   - Note load times

2. **Create GitHub Fork**
   - Fork trelliscopejs-lib on GitHub
   - Push feature branch
   - Create PR (optional)

3. **Production Deployment**
   - Deploy panel server
   - Configure remote URLs
   - Test with production data

### If Tests Fail ❌

1. **Debug Issues**
   - Check console errors
   - Review Network tab
   - Examine server logs

2. **Fix Problems**
   - Update code as needed
   - Re-test until passing
   - Document fixes

3. **Report Issues**
   - Create GitHub issue
   - Include error messages
   - Provide reproduction steps

---

## Conclusion

This browser testing guide provides comprehensive instructions for validating the REST panel integration. Following these steps ensures the forked viewer correctly loads panels from the Python-generated REST API configuration.

**Test Page:** `examples/output/test_rest_integration.html`
**Status:** Ready for manual browser testing
**Expected Duration:** 10-15 minutes for complete testing

---

**Last Updated:** 2025-11-02
**Status:** ✅ Ready for Testing
