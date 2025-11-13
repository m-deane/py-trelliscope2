# Prompt: Generate Trelliscope Examples Showcasing Phase 4 Features

## Context

You have access to a forecasting workflow template with:
- **Data examples**: Time series datasets with multiple entities
- **Recipes**: Data preprocessing and feature engineering pipelines
- **Workflows**: Model training pipelines
- **Workflowsets**: Multiple model comparisons
- **Tuning**: Hyperparameter optimization results
- **Cross-validation**: Model validation metrics across folds

## Objective

Create a comprehensive suite of Jupyter notebook examples that showcase the new **py-trelliscope2 Dash viewer Phase 4 features** using forecasting workflow outputs.

---

## Phase 4 Features to Showcase

### 1. **Dynamic Layout Controls**
- Interactive ncol/nrow adjustment
- Row vs column arrangement
- Real-time grid updates

### 2. **Label Configuration**
- Selective metadata display
- Type indicators for different cognostics
- Immediate visual updates

### 3. **Performance Optimization**
- Loading states for large datasets
- Efficient filtering/sorting
- Caching demonstrations

### 4. **Keyboard Navigation**
- Quick page navigation (←/→)
- Search shortcuts (/)
- Modal interactions (Esc)

### 5. **Export & Share**
- CSV export of filtered results
- View configuration sharing
- Display metadata export

### 6. **Error Handling & Notifications**
- Toast feedback for user actions
- Empty state handling
- Graceful error recovery

### 7. **Responsive Design**
- Mobile-friendly views
- Tablet optimization
- Touch-friendly controls

### 8. **Help & Documentation**
- In-app feature discovery
- Contextual help
- Keyboard shortcut reference

---

## Example Notebooks to Create

### Example 1: "Multi-Model Forecast Comparison"

**Use Case**: Compare forecasting performance across different models (ARIMA, Prophet, LSTM, XGBoost) for multiple time series.

**Data Structure**:
```python
# Each row = one forecast visualization + metadata
pd.DataFrame({
    'panel': [...],           # Panel column (forecast plots)
    'model': [...],           # Factor: ARIMA, Prophet, LSTM, XGBoost
    'series_id': [...],       # Factor: product_A, product_B, etc.
    'rmse': [...],            # Number: root mean squared error
    'mae': [...],             # Number: mean absolute error
    'mape': [...],            # Number: mean absolute percentage error
    'training_time': [...],   # Number: seconds to train
    'forecast_date': [...],   # Date: when forecast was made
    'data_points': [...],     # Number: training data size
})
```

**Features to Showcase**:
- ✅ **Layout Controls**: Start with 3×2 grid, let users adjust to 4×3 for more models
- ✅ **Labels**: Toggle between showing just model name vs full metrics
- ✅ **Filters**: Filter by RMSE < threshold, model type, series category
- ✅ **Sorts**: Sort by RMSE (best models first), or by training time (fastest first)
- ✅ **Views**: Save "Best Performing Models" view (RMSE < 10, sorted)
- ✅ **Search**: Search for specific series_id or model names
- ✅ **Export**: Export filtered results showing only top-performing models

**Visualization**:
- Each panel shows actual vs predicted time series plot
- Color-coded by model type
- Confidence intervals if available

---

### Example 2: "Hyperparameter Tuning Grid Search Results"

**Use Case**: Visualize results from grid search across different hyperparameter combinations.

**Data Structure**:
```python
pd.DataFrame({
    'panel': [...],           # Learning curves or residual plots
    'model_type': [...],      # Factor: random_forest, xgboost, lightgbm
    'n_estimators': [...],    # Number: 50, 100, 200, 500
    'max_depth': [...],       # Number: 3, 5, 10, 15
    'learning_rate': [...],   # Number: 0.01, 0.1, 0.3 (if applicable)
    'cv_score': [...],        # Number: cross-validation score
    'train_score': [...],     # Number: training score
    'fit_time': [...],        # Number: training time in seconds
    'is_best': [...],         # Factor: yes/no (best params for model)
})
```

**Features to Showcase**:
- ✅ **Performance**: Large dataset (100+ hyperparameter combinations) with loading states
- ✅ **Filters**: Multi-range filtering (cv_score > 0.8, fit_time < 60s)
- ✅ **Sorts**: Multi-column sort (cv_score DESC, then fit_time ASC)
- ✅ **Labels**: Show only critical metrics (cv_score, hyperparameters)
- ✅ **Views**: Save "Production Candidates" (best scoring, reasonable time)
- ✅ **Keyboard**: Quick navigation through parameter combinations
- ✅ **Export**: Export CSV of top 10 configurations for production

**Visualization**:
- Learning curves (train vs validation over iterations)
- Feature importance plots
- Residual distributions

---

### Example 3: "Cross-Validation Fold Analysis"

**Use Case**: Examine model performance across different CV folds and time windows.

**Data Structure**:
```python
pd.DataFrame({
    'panel': [...],           # Fold-specific performance plots
    'fold_id': [...],         # Factor: fold_1, fold_2, ..., fold_10
    'model': [...],           # Factor: model names
    'train_period': [...],    # Date range: "2020-01 to 2021-12"
    'test_period': [...],     # Date range: "2022-01 to 2022-12"
    'rmse': [...],            # Number: fold RMSE
    'r2_score': [...],        # Number: R² score
    'residual_std': [...],    # Number: residual standard deviation
    'prediction_bias': [...], # Number: mean prediction error
})
```

**Features to Showcase**:
- ✅ **Panel Details Modal**: Click fold to see full residual analysis
- ✅ **Modal Navigation**: Navigate through folds using Next/Previous in modal
- ✅ **Search**: Search for specific time periods or fold IDs
- ✅ **Filters**: Find problematic folds (RMSE > threshold, bias != 0)
- ✅ **Views**: Save "Underperforming Folds" view for investigation
- ✅ **Responsive**: View on mobile/tablet for presentations
- ✅ **Help**: In-app help explains CV metrics

**Visualization**:
- Residual plots per fold
- Actual vs predicted scatter plots
- Time series of residuals

---

### Example 4: "Feature Engineering Pipeline Comparison"

**Use Case**: Compare different feature engineering recipes/transformations.

**Data Structure**:
```python
pd.DataFrame({
    'panel': [...],           # Feature importance or correlation plots
    'recipe_id': [...],       # Factor: baseline, engineered_v1, engineered_v2
    'features_used': [...],   # Number: count of features
    'transformation': [...],  # Factor: log, sqrt, polynomial, spline
    'cv_score': [...],        # Number: cross-validation performance
    'feature_set': [...],     # Factor: basic, temporal, lagged, rolling
    'training_time': [...],   # Number: seconds
})
```

**Features to Showcase**:
- ✅ **Layout**: Adjust grid to compare many recipes side-by-side
- ✅ **Labels**: Configure to show recipe_id + cv_score only (minimal)
- ✅ **Filters**: Filter by feature_set and performance threshold
- ✅ **Sorts**: Sort by cv_score to see best recipes first
- ✅ **Export**: Export winning recipes as JSON for reproducibility
- ✅ **Notifications**: Toast when saving successful recipe configurations

**Visualization**:
- Feature importance bar charts
- Correlation heatmaps
- Distribution comparisons (before/after transformation)

---

### Example 5: "Multi-Series Forecasting at Scale"

**Use Case**: Forecast 100+ different time series (e.g., sales by product × region).

**Data Structure**:
```python
pd.DataFrame({
    'panel': [...],           # 100+ forecast visualizations
    'product': [...],         # Factor: 20 products
    'region': [...],          # Factor: 10 regions
    'category': [...],        # Factor: electronics, apparel, food
    'forecast_mape': [...],   # Number: forecast accuracy
    'trend': [...],           # Factor: increasing, decreasing, seasonal
    'last_update': [...],     # Time: timestamp of last forecast
    'alerts': [...],          # Number: count of anomaly alerts
})
```

**Features to Showcase**:
- ✅ **Performance**: 100+ panels with efficient loading
- ✅ **Search**: Global search across product names and regions
- ✅ **Filters**: Complex filtering (category=electronics AND region=west AND mape<10)
- ✅ **Views**: Save multiple views (e.g., "West Region Electronics", "Underperforming Products")
- ✅ **Keyboard**: Rapid navigation with arrow keys
- ✅ **Export**: Export filtered subset for reporting
- ✅ **Empty States**: Show empty state when no series match filters
- ✅ **Responsive**: Mobile view for field reviews

**Visualization**:
- Small multiples of time series + forecasts
- Sparklines in grid view
- Full time series in detail modal

---

### Example 6: "Workflowset Results Dashboard"

**Use Case**: Compare entire ML workflows (data prep + model + postprocessing).

**Data Structure**:
```python
pd.DataFrame({
    'panel': [...],           # ROC curves, confusion matrices, etc.
    'workflow_id': [...],     # Factor: workflow names
    'preprocessing': [...],   # Factor: normalize, standardize, robust
    'model': [...],           # Factor: rf, xgb, lgbm, nn
    'resampling': [...],      # Factor: none, smote, adasyn
    'accuracy': [...],        # Number: classification accuracy
    'f1_score': [...],        # Number: F1 score
    'inference_time': [...],  # Number: prediction time (ms)
    'complexity': [...],      # Number: model parameters count
})
```

**Features to Showcase**:
- ✅ **Layout**: Start compact (3×2), expand to 5×4 for full comparison
- ✅ **Labels**: Show workflow_id + accuracy + f1_score by default
- ✅ **Filters**: Multi-metric filtering (accuracy>0.9 AND inference_time<100)
- ✅ **Sorts**: Sort by F1 score for model selection
- ✅ **Views**: Save "Production Ready" (high accuracy, low latency)
- ✅ **Export**: Export top workflows as CSV for documentation
- ✅ **Help**: In-app help explains workflow components
- ✅ **Notifications**: Success toast when exporting results

**Visualization**:
- ROC curves
- Precision-Recall curves
- Confusion matrices
- Feature importance

---

### Example 7: "Time Series Diagnostics Suite"

**Use Case**: Diagnostic plots for time series analysis (stationarity, autocorrelation, seasonality).

**Data Structure**:
```python
pd.DataFrame({
    'panel': [...],           # Diagnostic plots (ACF, PACF, decomposition)
    'series_id': [...],       # Factor: series identifiers
    'diagnostic_type': [...], # Factor: acf, pacf, decomposition, stationarity
    'is_stationary': [...],   # Factor: yes, no
    'adf_pvalue': [...],      # Number: Augmented Dickey-Fuller p-value
    'seasonality': [...],     # Factor: none, weekly, monthly, yearly
    'trend_strength': [...],  # Number: 0-1 score
})
```

**Features to Showcase**:
- ✅ **Panel Details**: Click diagnostic plot to see full-size version
- ✅ **Filters**: Filter by is_stationary=no to find series needing transformation
- ✅ **Search**: Search for specific series_id
- ✅ **Views**: Save "Non-Stationary Series" view for preprocessing queue
- ✅ **Labels**: Toggle between technical metrics vs simple status
- ✅ **Keyboard**: Quick browsing with arrow keys
- ✅ **Export**: Export list of series needing attention

**Visualization**:
- ACF/PACF plots
- Seasonal decomposition
- Stationarity test results
- Rolling statistics plots

---

### Example 8: "Ensemble Method Comparison"

**Use Case**: Compare different ensemble strategies (bagging, boosting, stacking).

**Data Structure**:
```python
pd.DataFrame({
    'panel': [...],           # Ensemble performance plots
    'ensemble_type': [...],   # Factor: bagging, boosting, stacking, voting
    'base_models': [...],     # Factor: which models are combined
    'n_models': [...],        # Number: how many models in ensemble
    'cv_score': [...],        # Number: cross-validation score
    'improvement': [...],     # Number: % improvement over best base model
    'training_time': [...],   # Number: total training time
    'prediction_time': [...], # Number: inference time
})
```

**Features to Showcase**:
- ✅ **Sorts**: Multi-sort (improvement DESC, then prediction_time ASC)
- ✅ **Filters**: Filter by ensemble_type and improvement threshold
- ✅ **Layout**: Adjust to compare all ensemble types side-by-side
- ✅ **Labels**: Show ensemble_type + improvement prominently
- ✅ **Views**: Save "Best Ensembles" configuration
- ✅ **Export**: Export winning ensemble configurations
- ✅ **Notifications**: Toast feedback on save/load operations

**Visualization**:
- Model contribution plots
- Performance comparison bars
- Diversity metrics
- Error correlation heatmaps

---

## Implementation Guidelines

### For Each Example Notebook:

1. **Setup Section**
   ```python
   import pandas as pd
   import numpy as np
   import matplotlib.pyplot as plt
   from trelliscope import Display

   # Generate synthetic forecasting data
   # Create visualizations
   # Build DataFrame with panels + cognostics
   ```

2. **Trelliscope Creation**
   ```python
   display = (
       Display(df, name="example_name")
       .set_panel_column("panel")
       .infer_metas()
       .set_default_layout(ncol=3, nrow=2)
       .set_default_labels(["key_metric_1", "key_metric_2"])
       .write()
   )
   ```

3. **Feature Showcase Section**
   - Document which Phase 4 features are demonstrated
   - Provide step-by-step instructions for users
   - Include screenshots or descriptions of expected behavior

4. **Testing Instructions**
   - List specific interactions to try
   - Expected outcomes for each interaction
   - Performance expectations (load times, etc.)

---

## Data Generation Strategies

### Synthetic Forecasting Data

```python
def generate_forecast_data(
    n_series: int = 20,
    n_models: int = 4,
    n_periods: int = 100
):
    """Generate synthetic time series forecast data."""

    series_ids = [f"series_{i}" for i in range(n_series)]
    models = ['ARIMA', 'Prophet', 'LSTM', 'XGBoost']

    data = []
    for series_id in series_ids:
        # Generate base time series
        trend = np.linspace(0, 10, n_periods)
        seasonal = 5 * np.sin(np.linspace(0, 4*np.pi, n_periods))
        noise = np.random.normal(0, 1, n_periods)
        actual = trend + seasonal + noise

        for model in models:
            # Generate model-specific forecasts
            forecast = actual + np.random.normal(0, model_variance[model], n_periods)

            # Calculate metrics
            rmse = np.sqrt(np.mean((actual - forecast)**2))
            mae = np.mean(np.abs(actual - forecast))

            # Create visualization
            fig = create_forecast_plot(actual, forecast, series_id, model)

            data.append({
                'panel': fig,
                'series_id': series_id,
                'model': model,
                'rmse': rmse,
                'mae': mae,
                # ... more metrics
            })

    return pd.DataFrame(data)
```

### Panel Visualization Functions

```python
def create_forecast_plot(actual, forecast, series_id, model):
    """Create matplotlib forecast visualization."""
    fig, ax = plt.subplots(figsize=(8, 4))
    ax.plot(actual, label='Actual', color='black', linewidth=2)
    ax.plot(forecast, label='Forecast', color='blue', alpha=0.7)
    ax.fill_between(range(len(actual)),
                     forecast - 1.96*std,
                     forecast + 1.96*std,
                     alpha=0.2, color='blue')
    ax.set_title(f'{series_id} - {model}')
    ax.legend()
    ax.grid(True, alpha=0.3)
    return fig

def create_learning_curve(train_scores, val_scores, params):
    """Create learning curve plot for hyperparameter tuning."""
    fig, ax = plt.subplots(figsize=(8, 4))
    ax.plot(train_scores, label='Train', color='green')
    ax.plot(val_scores, label='Validation', color='red')
    ax.set_xlabel('Iteration')
    ax.set_ylabel('Score')
    ax.set_title(f'Params: {params}')
    ax.legend()
    ax.grid(True, alpha=0.3)
    return fig
```

---

## Success Criteria

Each example notebook should:

- ✅ **Demonstrate at least 3 Phase 4 features** prominently
- ✅ **Use realistic forecasting workflow outputs** (not toy data)
- ✅ **Include clear documentation** of what features are being shown
- ✅ **Provide step-by-step testing instructions** for users
- ✅ **Generate 20-100 panels** (scalable, not trivial)
- ✅ **Use meaningful metadata** (cognostics that enable real insights)
- ✅ **Create publication-quality visualizations** in panels
- ✅ **Include performance benchmarks** where relevant
- ✅ **Work on all devices** (responsive design testing)

---

## Deliverables

1. **8 Jupyter Notebooks** (one per example above)
   - `examples/phase4_showcase/01_multi_model_comparison.ipynb`
   - `examples/phase4_showcase/02_hyperparameter_tuning.ipynb`
   - `examples/phase4_showcase/03_cv_fold_analysis.ipynb`
   - `examples/phase4_showcase/04_feature_engineering.ipynb`
   - `examples/phase4_showcase/05_multi_series_scale.ipynb`
   - `examples/phase4_showcase/06_workflowset_dashboard.ipynb`
   - `examples/phase4_showcase/07_time_series_diagnostics.ipynb`
   - `examples/phase4_showcase/08_ensemble_comparison.ipynb`

2. **README.md** for the showcase directory
   - Overview of all examples
   - Feature mapping (which example shows which feature)
   - Running instructions
   - Expected output descriptions

3. **Testing Script** (`test_phase4_showcase.py`)
   - Automated test that all notebooks run successfully
   - Validates that displays are created
   - Checks that all expected files are generated

---

## Example README.md Structure

```markdown
# Phase 4 Feature Showcase Examples

This directory contains 8 comprehensive examples demonstrating the new
Phase 4 features of the py-trelliscope2 Dash viewer using forecasting
workflows.

## Feature Coverage Matrix

| Example | Layout | Labels | Perf | Keyboard | Export | Errors | Responsive | Help |
|---------|--------|--------|------|----------|--------|--------|------------|------|
| 01_multi_model | ✅ | ✅ | | | ✅ | | | |
| 02_hyperparameter | | | ✅ | ✅ | ✅ | | | |
| 03_cv_fold | | | | | | ✅ | ✅ | ✅ |
| ... | ... | ... | ... | ... | ... | ... | ... | ... |

## Running the Examples

1. Install dependencies:
   ```bash
   pip install -e ".[viz]"
   ```

2. Run any notebook:
   ```bash
   jupyter notebook examples/phase4_showcase/01_multi_model_comparison.ipynb
   ```

3. Or run all examples:
   ```bash
   python examples/phase4_showcase/run_all.py
   ```

## What to Expect

Each example generates:
- A Trelliscope display with 20-100 panels
- Interactive Dash viewer at http://localhost:8053
- Comprehensive metadata enabling rich filtering/sorting
- Step-by-step instructions for feature exploration
```

---

## Prompt Summary

**Task**: Create 8 Jupyter notebook examples using forecasting workflow outputs (model comparisons, hyperparameter tuning, cross-validation, feature engineering, ensembles, diagnostics) to comprehensively showcase all Phase 4 features of the py-trelliscope2 Dash viewer.

**Focus**: Real-world ML/forecasting use cases with meaningful visualizations and metadata that enable users to discover insights through the interactive viewer.

**Outcome**: Production-ready examples that serve as both feature demonstrations and user tutorials for data scientists working with forecasting and ML workflows.
