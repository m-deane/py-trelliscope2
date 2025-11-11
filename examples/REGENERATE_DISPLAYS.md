# How to Regenerate Displays with Latest Fixes

## Quick Start

The notebook `17_dual_display_demo.ipynb` now has all the fixes built in. Just follow these steps:

### Step 1: Open the Notebook
```bash
cd examples
jupyter notebook 17_dual_display_demo.ipynb
```

### Step 2: Restart Kernel (CRITICAL!)
In Jupyter menu: **Kernel → Restart Kernel**

This clears any cached Python code and ensures you get the latest fixes.

### Step 3: Run These Cells in Order

1. **Cell #1** (NEW!) - Clears cached modules
   - Ensures latest trelliscope code is loaded

2. **Cell #2** - Imports
   - Loads trelliscope with all fixes

3. **Cells #3-8** - Setup and function definitions
   - Defines plot functions (including responsive version)

4. **Cell #9** - Generate display data
   - ✅ Already updated to use `create_plotly_plot_responsive`
   - ✅ Country strings will auto-convert to 1-based indices

5. **Cell #11** - Generate matplotlib display
   - Creates PNG panels with proper factor indexing

6. **Cell #13** - Generate plotly display
   - Creates responsive HTML panels with proper factor indexing

7. **Cell #17** - Start servers
   - Launches on ports 8763 (matplotlib) and 8764 (plotly)

### Step 4: Open Viewers

The servers will open automatically, or manually visit:
- **Matplotlib**: http://localhost:8763/
- **Plotly**: http://localhost:8764/

## What You'll Get

### ✅ Fixed Issues

1. **Country metadata works correctly**
   - Filter shows "Algeria", "Denmark", "Germany", etc.
   - No more "[missing]" values
   - Uses 1-based factor indexing behind the scenes

2. **Plotly plots resize with layout**
   - Change columns from 2 → 3 → 4 in viewer
   - Plots automatically resize to fit
   - Uses `autosize=True` in Plotly layout

3. **Fresh code every time**
   - New Cell #1 clears cached modules
   - Ensures latest serialization fixes are active

## Verification

After regenerating, verify the fixes worked:

### Check Country Metadata
```bash
cd output/refinery_plotly/displays/refinery_plotly
python3 -c "
import json
with open('metaData.json') as f:
    data = json.load(f)
    print(f'Country value: {data[0][\"country\"]}')
    print(f'Type: {type(data[0][\"country\"]).__name__}')
    print('✅ Should be: int with value 1 (not string!)')
"
```

Expected output:
```
Country value: 1
Type: int
✅ Should be: int with value 1 (not string!)
```

### Check Responsive Plots
```bash
cd output/refinery_plotly/displays/refinery_plotly/panels
grep -o '"autosize"[[:space:]]*:[[:space:]]*true' 0.html
```

Expected output: `"autosize": true`

## Troubleshooting

### Country still shows "[missing]"

**Cause**: Jupyter kernel using cached old code

**Fix**:
1. Kernel → Restart Kernel (in Jupyter)
2. Re-run Cell #1 to clear cache
3. Re-run cells 2, 9, 11, 13

### Plots not resizing

**Cause**: Browser cache or old panel files

**Fix**:
1. Hard refresh browser: `Cmd+Shift+R` (Mac) or `Ctrl+Shift+F5` (Win)
2. Try incognito/private window
3. If still broken, regenerate: re-run cells 9, 13

### Import errors after restart

**Cause**: Virtual environment not activated

**Fix**:
```bash
conda activate py-trelliscope
# or
conda activate base  # if installed in base environment
```

## File Locations

**Notebook**: `examples/17_dual_display_demo.ipynb`

**Generated Displays**:
- `examples/output/refinery_by_country/` (matplotlib PNG)
- `examples/output/refinery_plotly/` (plotly HTML)

**Backup of Old Version**:
- `examples/output/refinery_plotly_OLD/` (preserved for comparison)

## Key Code Changes

The fixes are in `trelliscope/serialization.py`:

**Lines 267-278**: String factor → 1-based index conversion (cogData)
**Lines 348-358**: String factor → 1-based index conversion (metaData.json)
**Lines 432-442**: String factor → 1-based index conversion (metaData.js)

**Cell #9 in notebook**: Uses `create_plotly_plot_responsive` instead of `create_plotly_plot`

## Summary

✅ **Kernel restart** → Clears old code
✅ **Cell #1** → Forces module reload
✅ **Cells 9, 11, 13** → Generate displays with fixes
✅ **Cell #17** → Launch servers

Both displays will have working country filters and responsive plots!
