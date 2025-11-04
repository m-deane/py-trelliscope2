# Regeneration Required for Example Notebooks

## Important Notice

The viewer HTML generation has been fixed to use the correct JavaScript filename.

**Any displays created before 2025-10-27 need to be regenerated.**

## What Was Fixed

The generated `index.html` files were using an incorrect JavaScript filename that caused blank pages in the browser:

- ❌ **Old (broken)**: `trelliscopejs-lib.js`
- ✅ **New (fixed)**: `trelliscope-viewer.js`

## How to Regenerate

### Option 1: Rerun All Notebook Cells

Open each notebook and select **"Restart Kernel and Run All Cells"**:

1. `01_basic_workflow.ipynb`
2. `02_panel_rendering.ipynb`
3. `03_metadata.ipynb`
4. `04_layout_and_state.ipynb`
5. `05_views.ipynb`
6. `06_input_panels.ipynb`
7. `07_advanced_features.ipynb`
8. `08_large_datasets.ipynb`
9. `09_viewer_config.ipynb`
10. `10_viewer_integration.ipynb`

### Option 2: Clean and Rerun Specific Notebooks

If you only want to regenerate specific displays:

```bash
# Remove old output directories
rm -rf examples/output

# Rerun specific notebook
jupyter notebook examples/10_viewer_integration.ipynb
# Then: Kernel → Restart & Run All
```

### Option 3: Run Verification Test

To test that the fix is working:

```bash
cd examples
python verify_viewer_fix.py
```

This will create a test display in `examples/verification_test/` that you can view.

## What to Expect

After regeneration:

1. **No more blank pages** - Viewer should display correctly
2. **No console errors** - JavaScript should load from CDN
3. **Panels visible** - All panels should render in the viewer

## Checking if Your Display Needs Regeneration

To check if a display was generated with the old broken code:

```bash
# Check the index.html file
grep "trelliscopejs-lib.js" your_output_dir/index.html

# If this returns a match, the display needs regeneration
# If no match, you're using the fixed version
```

## Old Output Directories Cleaned Up

The following directories have been removed and should be regenerated:

- `examples/output/`
- `examples/clean_test/`

## Test Before Deployment

Before deploying any display to production, verify it works locally:

```bash
cd your_output_dir
python -m http.server 8000
# Open http://localhost:8000/index.html
# Confirm viewer loads and panels display
```

## Questions?

See `VIEWER_FIX_SUMMARY.md` for technical details about the fix.
