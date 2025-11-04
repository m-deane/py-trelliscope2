# Working Viewer Demo Notebook - Created ✅

**File**: `examples/11_working_viewer_demo.ipynb`
**Date**: November 4, 2025
**Purpose**: Demonstrate the fully working viewer at http://localhost:9000

---

## What's in the Notebook

This notebook provides a **complete walkthrough** of the working trelliscope viewer with all panels displaying correctly.

### Section Overview

1. **Quick Start** - Direct link to working viewer at localhost:9000
2. **Inspect Working Display** - Examine the file structure
3. **Configuration Files** - Deep dive into config.json and displayList.json
4. **Panel Interface** - The CRITICAL configuration that makes panels work
5. **Panel Meta** - How panel metadata must be structured
6. **Panel References** - Correct format for cogData entries
7. **Create New Display** - Build your own working display from scratch
8. **Verify Configuration** - Checklist to ensure everything is correct
9. **Launch Viewer** - Start the interactive viewer
10. **Compare URLs** - Links to all working viewers
11. **Key Takeaways** - Critical requirements and best practices

---

## How to Use

### Option 1: Just View the Working Example

1. Open http://localhost:9000 in your browser
2. You should see **5 panels** with bar charts displaying correctly
3. This is the reference working implementation

### Option 2: Run the Notebook

1. Open `examples/11_working_viewer_demo.ipynb` in Jupyter
2. Run cells 1-5 to inspect the working display structure
3. Run cells 6-8 to create your own new display
4. Run cell 9 to launch the viewer for your new display
5. Your new display will be at http://localhost:8765

### Option 3: Quick Reference

Just read through the notebook to understand:
- What files are required
- How they must be structured
- Critical configuration values
- Common pitfalls to avoid

---

## Key Highlights

### Critical Configuration Values

The notebook clearly shows these MUST be correct:

```json
// panelInterface
{
  "type": "file",        // NOT "panel_local"
  "base": "panels",      // NOT "./panels"
  "panelCol": "panel"
}

// Panel meta in metas array
{
  "varname": "panel",
  "type": "panel",       // NOT "panel_src"
  "paneltype": "img"
}

// Panel references in cogData
{
  "panel": "0.png"       // NOT "panels/0.png"
}
```

### Multi-Display Structure

```
output/
├── index.html          ← Server serves from here
├── config.json         ← Points to displays/
└── displays/
    ├── displayList.json
    └── {name}/
        ├── displayInfo.json
        └── panels/
            ├── 0.png
            └── ...
```

---

## Working Viewers Available

After running the notebook, you'll have access to:

| URL | Description | Panels | Status |
|-----|-------------|--------|--------|
| http://localhost:9000 | Original working example | 5 | ✅ Running |
| http://localhost:8001 | Reference implementation | 5 | ✅ Running |
| http://localhost:8765 | Your new demo (from notebook) | 15 | ✅ After running cell 9 |

---

## What Makes This Notebook Special

1. **Live Comparison**: You can see the working version while creating your own
2. **Verification Built-In**: Checklist cells verify correct configuration
3. **Step-by-Step**: Each critical component explained individually
4. **Complete Example**: Full working code from data → display → viewer
5. **Troubleshooting**: Clear explanation of what goes wrong when config is incorrect

---

## Code Pattern to Follow

The notebook demonstrates this proven pattern:

```python
# 1. Create data with panels
data = pd.DataFrame({
    'panel': [fig1, fig2, fig3],  # Matplotlib/Plotly figures
    'category': ['A', 'B', 'C'],
    'value': [10, 20, 30]
})

# 2. Create display with correct configuration
display = (
    Display(data, name="my_display", path=output_dir)
    .set_panel_column('panel')    # REQUIRED
    .infer_metas()                 # REQUIRED
    .set_default_layout(ncol=3)
)

# 3. Write with force=True
output_path = display.write(force=True)

# 4. Launch viewer (uses fixed Display.view())
url = display.view(port=8765, open_browser=True)
```

---

## Verification Checklist

The notebook includes this automated checklist:

- ✅ panelInterface.type == "file"
- ✅ panelInterface.base == "panels"
- ✅ primarypanel field set
- ✅ Panel meta in metas array
- ✅ Panel meta type == "panel"
- ✅ cogData has panel references
- ✅ Panel reference format: "0.png"

All must pass for panels to display correctly.

---

## Differences from Other Notebooks

### vs. 01_getting_started.ipynb
- **01**: Basic introduction, may use old patterns
- **11**: Current best practices with all fixes applied ✅

### vs. 02_panel_rendering.ipynb
- **02**: Focuses on rendering panels to files
- **11**: Focuses on viewer integration and display ✅

### vs. 10_viewer_integration.ipynb
- **10**: General viewer integration (may need updates)
- **11**: Working example with verified configuration ✅

---

## Common Issues Prevented

The notebook explicitly shows how to avoid:

1. ❌ Using "panel_local" instead of "file"
2. ❌ Using "./panels" instead of "panels"
3. ❌ Missing panel meta in metas array
4. ❌ Wrong panel reference format
5. ❌ Server running from wrong directory

All these are **automatically correct** when following the notebook pattern.

---

## Next Steps

### To Use This as a Template

1. Copy cells 6-9 from the notebook
2. Replace the `create_demo_plot()` function with your own
3. Update data creation to match your use case
4. Run the cells
5. View at the URL printed

### To Understand the Working Version

1. Run cells 1-5 to inspect localhost:9000
2. Read the explanations of each configuration file
3. Compare with your own displays if they're not working
4. Use the verification checklist

### To Create More Examples

The notebook pattern can be extended to:
- Time series data (like in 10_viewer_integration.ipynb)
- Statistical models (different plot types per category)
- Geographic data (maps as panels)
- Any visualization that fits the panel model

---

## Files Created

1. **examples/11_working_viewer_demo.ipynb** - The demo notebook ✅
2. **.claude_plans/WORKING_VIEWER_DEMO_SUMMARY.md** - This summary ✅

---

## Conclusion

**✅ READY TO USE**: Open `examples/11_working_viewer_demo.ipynb` and start exploring!

The notebook provides:
- ✅ Working reference at localhost:9000
- ✅ Complete explanation of all configuration
- ✅ Step-by-step guide to create your own
- ✅ Verification checklist
- ✅ Troubleshooting guidance

**All panels display correctly when following this pattern!** 🎉
