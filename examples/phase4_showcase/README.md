# Phase 4 Feature Showcase Examples

This directory contains comprehensive Jupyter notebook examples demonstrating all **Phase 4 features** of the py-trelliscope2 Dash interactive viewer using realistic forecasting and machine learning workflows.

## 🎯 Overview

Each example uses synthetic but realistic forecasting data to showcase specific Phase 4 enhancements:

| # | Example | Panels | Primary Focus |
|---|---------|--------|---------------|
| 1 | [Multi-Model Forecast Comparison](01_multi_model_comparison.ipynb) | 80 | Layout controls, Label config, Views |
| 2 | [Hyperparameter Tuning Grid Search](02_hyperparameter_tuning.ipynb) | 216 | Performance optimization, Large datasets |
| 3 | [Cross-Validation Fold Analysis](03_cv_fold_analysis.ipynb) | 30 | Panel details modal, Responsive design |
| 5 | [Multi-Series Forecasting at Scale](05_multi_series_scale.ipynb) | 120 | Search, Complex filtering, Scale |

**Total**: 4 comprehensive examples covering 8 Phase 4 features

---

## ✅ Phase 4 Feature Coverage Matrix

| Feature | Example 1 | Example 2 | Example 3 | Example 5 | Coverage |
|---------|:---------:|:---------:|:---------:|:---------:|:--------:|
| **1. Dynamic Layout Controls** | ✅ | | | | ⭐⭐⭐ |
| **2. Label Configuration** | ✅ | ✅ | | | ⭐⭐⭐ |
| **3. Performance Optimization** | | ✅ | | ✅ | ⭐⭐⭐⭐ |
| **4. Keyboard Navigation** | ✅ | ✅ | ✅ | ✅ | ⭐⭐⭐⭐⭐ |
| **5. Export & Share** | ✅ | ✅ | | ✅ | ⭐⭐⭐⭐ |
| **6. Error Handling & Notifications** | | | ✅ | ✅ | ⭐⭐⭐ |
| **7. Responsive Design** | | | ✅ | | ⭐⭐⭐ |
| **8. Help & Documentation** | ✅ | | ✅ | | ⭐⭐⭐ |

**Legend**: ✅ = Feature demonstrated | ⭐ = Coverage level (more stars = more examples)

---

## 📖 Example Details

### Example 1: Multi-Model Forecast Comparison

**File**: `01_multi_model_comparison.ipynb`

**Scenario**: Compare 4 forecasting models (ARIMA, Prophet, ETS, XGBoost) across 20 products

**Panels**: 80 (20 products × 4 models)

**Features Showcased**:
- ✅ **Dynamic Layout Controls**: Adjust ncol/nrow from 3×2 to 5×4
- ✅ **Label Configuration**: Toggle between minimal vs comprehensive labels
- ✅ **Filters**: Multi-criteria filtering (category, model, performance)
- ✅ **Sorts**: Multi-column sorting (RMSE then training time)
- ✅ **Views**: Save "Best Models", "Fast Models" configurations
- ✅ **Search**: Find specific products or models
- ✅ **Export**: Download top-performing model configurations
- ✅ **Keyboard**: Navigate with arrow keys, /for search

**Key Insights**:
- Which model performs best overall?
- Which model offers best speed/accuracy trade-off?
- Are certain products harder to forecast?

**Recommended For**: First-time users, General workflow overview

---

### Example 2: Hyperparameter Tuning Grid Search

**File**: `02_hyperparameter_tuning.ipynb`

**Scenario**: Grid search across 216 hyperparameter combinations for 3 models

**Panels**: 216 (Random Forest + XGBoost + LightGBM combinations)

**Features Showcased**:
- ✅ **Performance Optimization**: Large dataset (200+ panels) with loading states
- ✅ **Multi-Range Filtering**: cv_score > 0.85 AND fit_time < 60s
- ✅ **Multi-Column Sorting**: Best score first, then fastest time
- ✅ **Label Configuration**: Show only critical metrics
- ✅ **Views**: Save "Production Candidates" with complex filters
- ✅ **Keyboard Navigation**: Rapid browsing through 18 pages
- ✅ **Export**: Export top 10 configurations as CSV

**Key Insights**:
- Best overall hyperparameter configuration?
- Speed vs accuracy trade-offs?
- Which models overfit most?
- Production-ready configurations?

**Recommended For**: Performance testing, Large dataset handling

---

### Example 3: Cross-Validation Fold Analysis

**File**: `03_cv_fold_analysis.ipynb`

**Scenario**: Examine residuals across 10 CV folds for 3 models

**Panels**: 30 (10 folds × 3 models)

**Features Showcased**:
- ✅ **Panel Details Modal**: Click panels for full-size residual analysis
- ✅ **Modal Navigation**: Next/Previous buttons to step through folds
- ✅ **Responsive Design**: Mobile/tablet testing with DevTools
- ✅ **Search**: Find specific folds or time periods
- ✅ **Help & Documentation**: In-app help for CV metrics
- ✅ **Error Handling**: Empty states for impossible filters
- ✅ **Keyboard in Modal**: Arrow keys navigate, Esc closes

**Key Insights**:
- Which folds have highest errors?
- Are there temporal patterns in residuals?
- Which model handles different periods best?
- Signs of non-random errors?

**Recommended For**: Modal features, Responsive design testing

---

### Example 5: Multi-Series Forecasting at Scale

**File**: `05_multi_series_scale.ipynb`

**Scenario**: Forecast 120 time series (20 products × 6 regions)

**Panels**: 120 (Large-scale demo)

**Features Showcased**:
- ✅ **Performance at Scale**: 100+ panels efficiently
- ✅ **Global Search**: Fast search across products, regions, categories
- ✅ **Complex Filtering**: Multi-dimensional (category AND region AND performance)
- ✅ **Multiple Views**: Save analysis states for different stakeholders
- ✅ **Keyboard Navigation**: Rapid page navigation (10 pages)
- ✅ **Export**: Filtered subsets for reporting
- ✅ **Empty States**: Graceful handling when no matches

**Key Insights**:
- Which regions perform best for each category?
- Which products need attention across all regions?
- Regional forecasting patterns?
- Category-specific accuracy?

**Recommended For**: Scalability testing, Search features, Real-world workflows

---

## 🚀 Running the Examples

### Prerequisites

```bash
# Install py-trelliscope2 with visualization extras
pip install -e ".[viz]"

# Or install required packages
pip install pandas numpy matplotlib scipy trelliscope
```

### Run Individual Example

```bash
# Option 1: Jupyter Notebook
jupyter notebook examples/phase4_showcase/01_multi_model_comparison.ipynb

# Option 2: Jupyter Lab
jupyter lab examples/phase4_showcase/

# Option 3: VS Code
# Open notebook in VS Code with Jupyter extension
```

### Expected Workflow

1. **Open notebook** in Jupyter
2. **Run all cells** (Cell → Run All)
3. **Wait for viewer to launch** (last cell)
4. **Browser opens automatically** at http://localhost:8053
5. **Explore features** using the testing guide in each notebook
6. **Stop server** with Ctrl+C when done

---

## 📊 What to Expect

### Generated Files

Each example creates:

```
/tmp/tmp{random}/
└── {display_name}/
    ├── config.json
    ├── displays/
    │   ├── displayList.json
    │   └── {display_name}/
    │       ├── displayInfo.json
    │       ├── metaData.json
    │       ├── metaData.js
    │       └── panels/
    │           ├── 0.png
    │           ├── 1.png
    │           └── ...
    └── index.html
```

### Browser Experience

- **Interactive grid** with configurable layout
- **Sidebar** with filters, sorts, views, search, labels, export
- **Header** with help and keyboard shortcuts buttons
- **Modals** for panel details and help
- **Toast notifications** for user feedback
- **Responsive design** adapts to screen size

---

## 🧪 Testing Checklist

Use these examples to systematically test Phase 4 features:

### Feature 1: Dynamic Layout Controls

- [ ] **Example 1** - Adjust ncol from 3 to 5
- [ ] **Example 1** - Change arrangement from row to column
- [ ] **Example 1** - Reset to default layout

### Feature 2: Label Configuration

- [ ] **Example 1** - Toggle individual labels on/off
- [ ] **Example 2** - Use "Select All" / "Clear All"
- [ ] **Example 1** - Observe immediate grid updates

### Feature 3: Performance Optimization

- [ ] **Example 2** - Load 216 panels, check timing (< 3s)
- [ ] **Example 5** - Load 120 panels, check responsiveness
- [ ] **Example 2** - Apply filters, observe loading states
- [ ] **Example 5** - Sort large dataset, check performance (< 500ms)

### Feature 4: Keyboard Navigation

- [ ] **All Examples** - Press → for next page
- [ ] **All Examples** - Press ← for previous page
- [ ] **All Examples** - Press / to focus search
- [ ] **All Examples** - Press Esc to clear search
- [ ] **Example 3** - Use arrows in panel modal

### Feature 5: Export & Share

- [ ] **Example 1** - Export CSV with filters applied
- [ ] **Example 2** - Export view configuration as JSON
- [ ] **Example 5** - Export filtered subset for reporting
- [ ] **All Examples** - Verify timestamped filenames

### Feature 6: Error Handling & Notifications

- [ ] **Example 3** - Apply impossible filter, see empty state
- [ ] **Example 5** - Click "Reset Filters" from empty state
- [ ] **Example 1** - Save view, see success toast
- [ ] **All Examples** - Toast auto-dismisses after 3s

### Feature 7: Responsive Design

- [ ] **Example 3** - Open DevTools, test tablet view (768px)
- [ ] **Example 3** - Test mobile view (375px)
- [ ] **Example 3** - Verify sidebar collapses
- [ ] **Example 3** - Verify touch-friendly buttons (44px)
- [ ] **Example 3** - Test modal on mobile

### Feature 8: Help & Documentation

- [ ] **Example 1** - Click "?" help button
- [ ] **Example 3** - Review all 9 help sections
- [ ] **All Examples** - Click "⌨️" for keyboard shortcuts
- [ ] **All Examples** - Verify help is comprehensive

---

## 📈 Performance Benchmarks

**Expected Performance** (by example):

| Example | Panels | Initial Load | Filter | Sort | Search | Page Nav |
|---------|--------|--------------|--------|------|--------|----------|
| Example 1 | 80 | < 2s | < 400ms | < 400ms | < 200ms | < 300ms |
| Example 2 | 216 | < 3s | < 500ms | < 500ms | < 200ms | < 300ms |
| Example 3 | 30 | < 1.5s | < 300ms | < 300ms | < 150ms | < 200ms |
| Example 5 | 120 | < 2.5s | < 400ms | < 400ms | < 200ms | < 300ms |

**How to Measure**:
1. Open browser DevTools (F12)
2. Go to Performance tab
3. Record operation
4. Check duration in timeline

---

## 🎓 Learning Path

**For New Users**:
1. Start with **Example 1** (Multi-Model Comparison) - covers basics
2. Try **Example 3** (CV Fold Analysis) - learn modal features
3. Move to **Example 5** (Multi-Series Scale) - see scale capabilities
4. Finish with **Example 2** (Hyperparameter Tuning) - advanced workflows

**For Performance Testing**:
1. **Example 2** - Large dataset (216 panels)
2. **Example 5** - Medium dataset (120 panels) with complex filters

**For Mobile Testing**:
1. **Example 3** - Best responsive design demo
2. Use browser DevTools device emulation

---

## 💡 Tips for Exploration

### Discover Insights

Each example is designed to answer specific questions:

**Example 1**:
- "Which model should I use for production?"
- "What's the speed/accuracy trade-off?"

**Example 2**:
- "Which hyperparameters optimize performance?"
- "Where are the overfitting risks?"

**Example 3**:
- "Are my CV folds representative?"
- "Do residuals show concerning patterns?"

**Example 5**:
- "Which markets underperform?"
- "Are there geographic patterns?"

### Save Your Work

- Create **Views** for different stakeholder needs:
  - "Executive Summary" - top performers only
  - "Deep Dive" - problematic cases needing investigation
  - "Production Ready" - validated configurations

- **Export** results:
  - CSV for Excel analysis
  - View JSON for reproducing analysis
  - Share configurations with team

---

## 🔧 Troubleshooting

### Notebook Won't Run

```bash
# Reinstall with extras
pip install -e ".[viz]"

# Or install missing packages
pip install matplotlib scipy pandas
```

### Browser Doesn't Open

- Manually open: http://localhost:8053
- Check if port is in use: `lsof -i :8053`
- Change port in last cell: `app.run(port=8054)`

### Slow Performance

- Close other applications
- Check browser has enough memory
- Try smaller example first (Example 3 has only 30 panels)

### Visualizations Don't Appear

- Verify matplotlib backend: `import matplotlib; matplotlib.use('Agg')`
- Check panel column contains figures: `df['panel'].head()`

---

## 📚 Additional Resources

### Documentation

- [PHASE_4_COMPLETE.md](../../.claude_plans/PHASE_4_COMPLETE.md) - Full feature implementation
- [PHASE_4_VALIDATION.md](../../.claude_plans/PHASE_4_VALIDATION.md) - Comprehensive testing checklist
- [PROJECT_COMPLETE.md](../../.claude_plans/PROJECT_COMPLETE.md) - Overall project summary
- [FINAL_STATUS.md](../../.claude_plans/FINAL_STATUS.md) - Current implementation status

### Main Documentation

- [CLAUDE.md](../../CLAUDE.md) - Project overview and technical details
- [README.md](../../README.md) - User-facing documentation

---

## 🎉 Summary

These Phase 4 showcase examples demonstrate:

✅ **All 8 Phase 4 features** comprehensively covered
✅ **Realistic workflows** using forecasting and ML scenarios
✅ **Performance at scale** (up to 216 panels)
✅ **Step-by-step testing guides** in each notebook
✅ **Real insights** discoverable through exploration

**Result**: Production-ready interactive viewer with full feature parity + enhancements!

---

*Created: 2025-11-13*
*py-trelliscope2 Phase 4 Complete*
*Total Examples: 4 | Total Panels: 446 | Total Features: 8*
