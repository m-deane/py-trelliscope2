==================
Examples
==================

Complete working examples demonstrating py-trelliscope features.

Time Series Analysis
====================

Visualizing multiple time series with filtering and sorting:

.. code-block:: python

   import pandas as pd
   import matplotlib.pyplot as plt
   from trelliscope import Display, FactorMeta, NumberMeta

   # Load time series data
   df = pd.read_csv("stock_prices.csv")
   df['date'] = pd.to_datetime(df['date'])

   # Create plot for each stock
   def create_time_series_plot(data, symbol):
       fig, ax = plt.subplots(figsize=(8, 5))
       ax.plot(data['date'], data['price'], linewidth=2)
       ax.set_title(f"{symbol} Stock Price")
       ax.set_xlabel("Date")
       ax.set_ylabel("Price (USD)")
       ax.grid(True, alpha=0.3)
       plt.tight_layout()
       return fig

   # Aggregate by stock
   results = []
   for symbol, group in df.groupby('symbol'):
       results.append({
           'symbol': symbol,
           'plot': create_time_series_plot(group, symbol),
           'avg_price': group['price'].mean(),
           'volatility': group['price'].std(),
           'max_price': group['price'].max(),
           'min_price': group['price'].min()
       })

   display_df = pd.DataFrame(results)

   # Create display
   display = (
       Display(display_df, name="stock_analysis",
               description="Stock price analysis with volatility metrics")
       .set_panel_column("plot")
       .add_meta_def(FactorMeta("symbol", label="Stock Symbol"))
       .add_meta_def(NumberMeta("avg_price", label="Avg Price (USD)", digits=2))
       .add_meta_def(NumberMeta("volatility", label="Volatility", digits=2))
       .add_meta_def(NumberMeta("max_price", label="Max Price (USD)", digits=2))
       .add_meta_def(NumberMeta("min_price", label="Min Price (USD)", digits=2))
       .set_default_layout(ncol=3, nrow=2)
       .set_default_labels(["symbol", "avg_price"])
       .set_default_sorts([{"varname": "volatility", "dir": "desc"}])
       .add_view(
           name="high_volatility",
           filter_list=[{"type": "range", "varname": "volatility", "min": 10}],
           sort_list=[{"varname": "volatility", "dir": "desc"}]
       )
       .write()
   )

   # Clean up matplotlib figures
   for fig in display_df['plot']:
       plt.close(fig)

Geographic Analysis
===================

Country-level analysis with interactive Plotly maps:

.. code-block:: python

   import pandas as pd
   import plotly.graph_objects as go
   from trelliscope import Display, FactorMeta, NumberMeta

   # Load country data
   df = pd.read_csv("country_metrics.csv")

   # Create choropleth for each metric
   def create_country_map(metric_name, metric_data):
       fig = go.Figure(data=go.Choropleth(
           locations=df['country_code'],
           z=df[metric_data],
           text=df['country'],
           colorscale='Viridis',
           autocolorscale=False,
           marker_line_color='darkgray',
           marker_line_width=0.5,
           colorbar_title=metric_name,
       ))

       fig.update_layout(
           title=f"{metric_name} by Country",
           geo=dict(
               showframe=False,
               showcoastlines=False,
               projection_type='equirectangular'
           ),
           width=600,
           height=400
       )
       return fig

   # Create one display per metric
   metrics = {
       'GDP': 'gdp',
       'Population': 'population',
       'Life Expectancy': 'life_expectancy'
   }

   results = []
   for metric_name, metric_col in metrics.items():
       results.append({
           'metric': metric_name,
           'plot': create_country_map(metric_name, metric_col),
           'avg_value': df[metric_col].mean(),
           'max_value': df[metric_col].max()
       })

   display_df = pd.DataFrame(results)

   display = (
       Display(display_df, name="country_metrics",
               description="Global country metrics visualization")
       .set_panel_column("plot")
       .add_meta_def(FactorMeta("metric", label="Metric"))
       .add_meta_def(NumberMeta("avg_value", label="Average", digits=1))
       .add_meta_def(NumberMeta("max_value", label="Maximum", digits=1))
       .set_default_layout(ncol=2, nrow=2)
       .write()
   )

Model Performance Comparison
============================

Comparing machine learning models across datasets:

.. code-block:: python

   import pandas as pd
   import matplotlib.pyplot as plt
   from sklearn.metrics import confusion_matrix, ConfusionMatrixDisplay
   from trelliscope import Display, FactorMeta, NumberMeta

   # Model results
   results_df = pd.read_csv("model_results.csv")

   def create_confusion_matrix_plot(model_name, dataset, y_true, y_pred):
       cm = confusion_matrix(y_true, y_pred)

       fig, ax = plt.subplots(figsize=(6, 5))
       disp = ConfusionMatrixDisplay(confusion_matrix=cm)
       disp.plot(ax=ax, cmap='Blues')
       ax.set_title(f"{model_name} - {dataset}")
       plt.tight_layout()
       return fig

   # Calculate metrics
   from sklearn.metrics import accuracy_score, f1_score, precision_score, recall_score

   results = []
   for idx, row in results_df.iterrows():
       y_true = eval(row['y_true'])  # Convert string to list
       y_pred = eval(row['y_pred'])

       results.append({
           'model': row['model_name'],
           'dataset': row['dataset'],
           'plot': create_confusion_matrix_plot(
               row['model_name'], row['dataset'], y_true, y_pred
           ),
           'accuracy': accuracy_score(y_true, y_pred),
           'f1_score': f1_score(y_true, y_pred, average='weighted'),
           'precision': precision_score(y_true, y_pred, average='weighted'),
           'recall': recall_score(y_true, y_pred, average='weighted')
       })

   display_df = pd.DataFrame(results)

   display = (
       Display(display_df, name="model_comparison",
               description="ML model performance across datasets")
       .set_panel_column("plot")
       .add_meta_def(FactorMeta("model", label="Model"))
       .add_meta_def(FactorMeta("dataset", label="Dataset"))
       .add_meta_def(NumberMeta("accuracy", label="Accuracy", digits=3))
       .add_meta_def(NumberMeta("f1_score", label="F1 Score", digits=3))
       .add_meta_def(NumberMeta("precision", label="Precision", digits=3))
       .add_meta_def(NumberMeta("recall", label="Recall", digits=3))
       .set_default_layout(ncol=3, nrow=3)
       .set_default_labels(["model", "accuracy"])
       .set_default_sorts([{"varname": "accuracy", "dir": "desc"}])
       .add_view(
           name="best_models",
           filter_list=[{"type": "range", "varname": "accuracy", "min": 0.9}],
           sort_list=[{"varname": "accuracy", "dir": "desc"}]
       )
       .write()
   )

   # Clean up
   for fig in display_df['plot']:
       plt.close(fig)

Distribution Analysis
=====================

Exploring distributions across categories:

.. code-block:: python

   import pandas as pd
   import plotly.graph_objects as go
   from trelliscope import Display, FactorMeta, NumberMeta

   df = pd.read_csv("measurements.csv")

   def create_distribution_plot(data, category):
       fig = go.Figure()

       # Histogram
       fig.add_trace(go.Histogram(
           x=data['value'],
           name='Distribution',
           marker_color='steelblue',
           opacity=0.7
       ))

       # Add mean line
       mean_val = data['value'].mean()
       fig.add_vline(x=mean_val, line_dash="dash", line_color="red",
                     annotation_text=f"Mean: {mean_val:.2f}")

       fig.update_layout(
           title=f"Distribution - {category}",
           xaxis_title="Value",
           yaxis_title="Frequency",
           width=500,
           height=400,
           showlegend=False
       )
       return fig

   # Statistics by category
   results = []
   for category, group in df.groupby('category'):
       results.append({
           'category': category,
           'plot': create_distribution_plot(group, category),
           'mean': group['value'].mean(),
           'median': group['value'].median(),
           'std': group['value'].std(),
           'n': len(group)
       })

   display_df = pd.DataFrame(results)

   display = (
       Display(display_df, name="distributions",
               description="Value distributions by category")
       .set_panel_column("plot")
       .add_meta_def(FactorMeta("category", label="Category"))
       .add_meta_def(NumberMeta("mean", label="Mean", digits=2))
       .add_meta_def(NumberMeta("median", label="Median", digits=2))
       .add_meta_def(NumberMeta("std", label="Std Dev", digits=2))
       .add_meta_def(NumberMeta("n", label="Count", digits=0))
       .set_default_layout(ncol=3, nrow=2)
       .set_default_labels(["category", "mean"])
       .write()
   )

Image Gallery
=============

Creating an image gallery with metadata:

.. code-block:: python

   import pandas as pd
   from pathlib import Path
   from PIL import Image
   from trelliscope import Display, FactorMeta, NumberMeta

   # Scan image directory
   image_dir = Path("images")
   image_files = list(image_dir.glob("*.jpg"))

   # Extract metadata
   results = []
   for img_path in image_files:
       img = Image.open(img_path)
       width, height = img.size

       results.append({
           'image': str(img_path),
           'filename': img_path.name,
           'width': width,
           'height': height,
           'aspect_ratio': width / height,
           'size_mb': img_path.stat().st_size / (1024 * 1024)
       })

   display_df = pd.DataFrame(results)

   display = (
       Display(display_df, name="image_gallery",
               description="Image collection with metadata")
       .set_panel_column("image")
       .add_meta_def(FactorMeta("filename", label="Filename"))
       .add_meta_def(NumberMeta("width", label="Width (px)", digits=0))
       .add_meta_def(NumberMeta("height", label="Height (px)", digits=0))
       .add_meta_def(NumberMeta("aspect_ratio", label="Aspect Ratio", digits=2))
       .add_meta_def(NumberMeta("size_mb", label="Size (MB)", digits=2))
       .set_default_layout(ncol=4, nrow=3)
       .set_default_labels(["filename"])
       .write()
   )

See Also
========

* :doc:`getting_started` - Basic concepts
* :doc:`creating_displays` - Display configuration
* :doc:`panel_types` - Panel rendering options
