# Viewer Blank Page Diagnostic Steps

**Issue**: Viewer shows blank white page
**Location**: `http://localhost:8972/index.html`

---

## Step 1: Check Browser Console (MOST IMPORTANT)

1. Open the blank page in your browser
2. Open Developer Tools:
   - **Chrome/Edge**: Press `F12` or `Cmd+Option+I` (Mac)
   - **Firefox**: Press `F12` or `Cmd+Option+K` (Mac)
   - **Safari**: Press `Cmd+Option+C`

3. Look at the **Console** tab for errors (red text)

### Common Errors and Fixes:

| Error | Cause | Fix |
|-------|-------|-----|
| `Failed to fetch ./basic_viewer_demo/displayInfo.json` | displayInfo.json not found | Display not written or wrong path |
| `TrelliscopeApp is not defined` | CDN JavaScript didn't load | Check internet, try different CDN |
| `Unexpected token < in JSON` | Server returned HTML instead of JSON | CORS issue or wrong server directory |
| `Cannot read property 'panels' of undefined` | Missing fields in displayInfo.json | Need `format` and `base` fields |

---

## Step 2: Check Network Tab

1. Stay in Developer Tools
2. Go to **Network** tab
3. Refresh the page (`Cmd+R` or `F5`)
4. Look for these requests:

### Should Load Successfully (Status 200):
- ✅ `index.html`
- ✅ `trelliscopejs-lib.js` (from unpkg.com)
- ✅ `index.css` (from unpkg.com)
- ✅ `displayInfo.json`
- ✅ `metadata.csv`
- ✅ Panel images like `0.png`, `1.png`, etc.

### If Any Show Red (Failed):
- **CDN files fail**: No internet or CDN blocked → Need local viewer files
- **displayInfo.json 404**: Display not in expected location → Check paths
- **displayInfo.json 403**: Permission issue → Check file permissions
- **Panel images 404**: Panels not rendered → Need to run with `render_panels=True`

---

## Step 3: Verify File Structure

Run this in your terminal:

```bash
cd /Users/matthewdeane/Documents/Data\ Science/python/_projects/py-trelliscope2/examples
tree -L 3 output/  # or use: find output/ -type f | head -20
```

###Expected Structure:
```
output/
├── index.html                      # ← Viewer page
└── basic_viewer_demo/              # ← Display directory
    ├── displayInfo.json            # ← Config (needs format + base)
    ├── metadata.csv                # ← Metadata
    └── panels/                     # ← Panel images
        ├── 0.png
        ├── 1.png
        └── ...
```

---

## Step 4: Check displayInfo.json Content

```bash
cd examples/output/basic_viewer_demo
cat displayInfo.json | python -m json.tool | grep -A 5 panelInterface
```

### Must Have These Fields:
```json
"panelInterface": {
    "type": "panel_local",
    "panelCol": "panel",
    "format": "png",          # ← REQUIRED
    "base": "./panels"        # ← REQUIRED
}
```

### If Missing `format` or `base`:
The display was created with old code. **Rerun the notebook cell** with `force=True`:

```python
output_path = display.write(force=True)  # Regenerate with fix
```

---

## Step 5: Test with Minimal Example

Run this Python code to create a guaranteed-working display:

```python
import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
from pathlib import Path
import sys
sys.path.insert(0, '/Users/matthewdeane/Documents/Data Science/python/_projects/py-trelliscope2')

from trelliscope import Display

# Minimal test
df = pd.DataFrame({'id': [1, 2, 3], 'value': [10, 20, 30]})

def plot_fn(row):
    fig, ax = plt.subplots(figsize=(4, 3))
    ax.bar(['V'], [row['value']])
    ax.set_title(f"ID {row['id']}")
    plt.tight_layout()
    return fig

df['panel'] = df.apply(plot_fn, axis=1)

display = Display(df, name='minimal_test', path='test_output')
display.set_panel_column('panel').infer_metas()
output = display.write(force=True)

print(f"Created: {output}")
print("Now run: cd test_output && python -m http.server 8888")
print("Then open: http://localhost:8888/index.html")
```

---

## Step 6: Check Internet Connectivity

The viewer loads JavaScript from CDN. Test if it's accessible:

```bash
curl -I https://unpkg.com/trelliscopejs-lib/dist/trelliscopejs-lib.js
```

**Should see**: `HTTP/2 200` or `HTTP/2 302`

**If fails**: No internet or CDN blocked → Need offline viewer setup

---

## Step 7: Browser-Specific Issues

### Safari
- May block CDN resources for security
- **Fix**: Enable "Develop" menu → "Disable Cross-Origin Restrictions"

### Chrome/Edge
- Usually works fine
- Check console for CORS errors

### Firefox
- May have strict CORS policies
- **Fix**: Try Chrome as a test

---

## Quick Diagnostic Script

Run this to check everything:

```bash
cd /Users/matthewdeane/Documents/Data\ Science/python/_projects/py-trelliscope2/examples

echo "=== Checking file structure ==="
ls -la output/
ls -la output/basic_viewer_demo/

echo "\n=== Checking displayInfo.json ==="
cat output/basic_viewer_demo/displayInfo.json | python -m json.tool | grep -A 10 panelInterface

echo "\n=== Checking panel files ==="
ls -1 output/basic_viewer_demo/panels/ | head -5

echo "\n=== Checking CDN accessibility ==="
curl -I https://unpkg.com/trelliscopejs-lib/dist/trelliscopejs-lib.js | head -3

echo "\n=== Testing local server ==="
cd output && python -m http.server 8888 &
SERVER_PID=$!
sleep 2
curl -I http://localhost:8888/index.html | head -3
curl -I http://localhost:8888/basic_viewer_demo/displayInfo.json | head -3
kill $SERVER_PID
```

---

## Most Likely Causes (Based on "Blank Page"):

1. **JavaScript not loading** → Check Console for `TrelliscopeApp is not defined`
2. **displayInfo.json 404** → Wrong path or display not written
3. **Missing format/base fields** → Need to regenerate display
4. **CORS error** → Server configuration or browser security
5. **No internet** → CDN can't load

---

## What to Report

Please provide:

1. **Browser console errors** (copy the red text)
2. **Network tab failures** (which files show red/404)
3. **displayInfo.json content** (especially `panelInterface` section)
4. **File structure** (output of `ls -la output/`)

With this information, we can pinpoint the exact issue!
