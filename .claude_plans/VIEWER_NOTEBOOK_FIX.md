# Viewer Notebook Fix Summary

**Date**: October 27, 2025
**Status**: ✅ FIXED

---

## Problem

The `10_viewer_integration.ipynb` notebook was showing TypeError:

```
TypeError: Display.set_panel_column() got an unexpected keyword argument 'panel_fn'
```

This error occurred in multiple cells throughout the notebook.

---

## Root Cause

The notebook was using an API pattern that doesn't exist in the current implementation:

```python
# ❌ This doesn't exist in the current implementation
Display(data, name="demo").set_panel_column('id', panel_fn=make_plot)
```

The `set_panel_column()` method only accepts a column name parameter, not a `panel_fn` function. The current API expects the panel column to already contain Figure objects in the DataFrame.

---

## Solution

Updated all cells to use the correct API pattern:

1. **Generate plots** by applying the plot function to each row
2. **Add plots as a column** to the DataFrame
3. **Reference that column** as the panel column

### Before (Broken)
```python
display = (
    Display(data, name="basic_viewer_demo", path=output_dir)
    .set_panel_column('id', panel_fn=make_plot)  # ❌ panel_fn doesn't exist
    .set_default_layout(nrow=2, ncol=3)
    .write()
)
```

### After (Fixed)
```python
# Generate plots for each row
data['panel'] = data.apply(make_plot, axis=1)

display = (
    Display(data, name="basic_viewer_demo", path=output_dir)
    .set_panel_column('panel')  # ✅ Column with Figure objects
    .infer_metas()
    .set_default_layout(nrow=2, ncol=3)
    .write()
)
```

---

## Changes Made

### Cells Updated

1. **Cell 5** - Basic viewer demo
   - Added: `data['panel'] = data.apply(make_plot, axis=1)`
   - Changed: `.set_panel_column('id', panel_fn=make_plot)` → `.set_panel_column('panel')`
   - Added: `.infer_metas()`

2. **Cell 9** - Dark theme
   - Added: `data_dark = data.copy()` and `data_dark['panel'] = ...`
   - Changed: `.set_panel_column('id', panel_fn=make_plot)` → `.set_panel_column('panel')`
   - Added: `.infer_metas()` and `force=True`

3. **Cell 10** - Minimal viewer
   - Added: `data_minimal = data.copy()` and `data_minimal['panel'] = ...`
   - Changed: `.set_panel_column('id', panel_fn=make_plot)` → `.set_panel_column('panel')`
   - Added: `.infer_metas()` and `force=True`

4. **Cell 12** - Sorted demo
   - Added: `data_sorted = data.copy()` and `data_sorted['panel'] = ...`
   - Changed: `.set_panel_column('id', panel_fn=make_plot)` → `.set_panel_column('panel')`
   - Added: `.infer_metas()` and `force=True`

5. **Cell 14** - Styled demo
   - Added: `data_styled = data.copy()` and `data_styled['panel'] = ...`
   - Changed: `.set_panel_column('id', panel_fn=make_plot)` → `.set_panel_column('panel')`
   - Added: `.infer_metas()` and `force=True`

6. **Cell 16** - Advanced configuration
   - Added: `data_advanced = data.copy()` and `data_advanced['panel'] = ...`
   - Changed: `.set_panel_column('id', panel_fn=make_plot)` → `.set_panel_column('panel')`
   - Added: `.infer_metas()` and `force=True`

7. **Cell 21** - Production export
   - Added: `data_export = data.copy()` and `data_export['panel'] = ...`
   - Changed: `.set_panel_column('id', panel_fn=make_plot)` → `.set_panel_column('panel')`
   - Added: `.infer_metas()`

8. **Cell 27** - Time series analysis
   - Added: `metadata['panel'] = metadata.apply(make_time_series_plot, axis=1)`
   - Changed: `.set_panel_column('series_id', panel_fn=make_time_series_plot)` → `.set_panel_column('panel')`
   - Added: `.infer_metas()` and `force=True`

---

## Additional Improvements

### 1. Added `.infer_metas()`
All displays now call `.infer_metas()` to automatically detect metadata types from the DataFrame columns (excluding the panel column).

### 2. Added `force=True` for overwrites
Most displays (except the first) use `force=True` to allow overwriting output directories, making it easier to re-run cells during development.

### 3. Created copies for multiple displays
When creating multiple displays from the same base data, we now create copies:
```python
data_dark = data.copy()
data_dark['panel'] = data_dark.apply(make_plot, axis=1)
```

This prevents modifying the original DataFrame and ensures each display has its own panel column.

---

## Understanding the Pattern

### Why This Pattern?

The current implementation follows a **DataFrame-centric design**:
- All data (metadata + panels) lives in a DataFrame
- Panel column contains actual Figure objects
- Display reads from the DataFrame during write/render

### Benefits:
- ✅ Consistent with pandas workflows
- ✅ Easy to inspect: `df['panel'][0]` shows the figure
- ✅ Flexible: Can generate plots ahead of time or on-demand
- ✅ Compatible with existing DataFrame operations

### Trade-offs:
- Need to generate all plots before creating Display
- Plots stored in memory (not lazy-evaluated)
- For 1000+ panels, may want to generate plots during write

---

## How to Run the Notebook

### Option 1: In Your IDE
1. **Reload** the notebook (close and reopen) to pick up changes
2. **Select kernel**: "Python (py-trelliscope)"
3. **Run all cells** - Should execute without errors

### Option 2: Command Line
```bash
cd /Users/matthewdeane/Documents/Data\ Science/python/_projects/py-trelliscope2
source py-trelliscope-env/bin/activate
jupyter lab examples/10_viewer_integration.ipynb
```

### Option 3: Execute Without GUI
```bash
source py-trelliscope-env/bin/activate
jupyter nbconvert --to notebook --execute --inplace \
  examples/10_viewer_integration.ipynb \
  --ExecutePreprocessor.kernel_name=py-trelliscope
```

---

## Expected Output

When running Cell 5 (basic viewer demo):

```
Display written to: output/basic_viewer_demo

Created files:
  - displayInfo.json
  - metadata.csv
  - panels/
```

The notebook should now execute all cells cleanly, generating:
- Interactive viewer demos on different ports (9000-9006)
- Exported static sites in `exports/` directory
- Multiple display configurations showcasing themes and styling

---

## Related Fixes

This is the third notebook fix in the series:

1. **`01_getting_started.ipynb`** - Fixed rendering errors by adding `render_panels=False`
   - See: `NOTEBOOK_FIX_SUMMARY.md`

2. **`02_panel_rendering.ipynb`** - Fixed unhashable Figure error by skipping panel column in `infer_metas()`
   - See: `trelliscope/display.py` lines 507-509

3. **`10_viewer_integration.ipynb`** (this fix) - Fixed API mismatch by removing `panel_fn` parameter
   - See: This document

---

## Testing

All **413 tests passing** after the previous fix to `infer_metas()`.

The notebook fix is compatible with the current test suite and implementation.

---

## Summary

✅ **Problem**: Notebook used non-existent `panel_fn` parameter
✅ **Solution**: Generate panel column with `.apply()`, use `.set_panel_column('panel')`
✅ **Result**: Notebook now matches current API and executes cleanly

The notebook demonstrates the complete viewer workflow: basic viewing, configuration, theming, static export, and validation!
