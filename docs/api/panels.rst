==================
Panels API
==================

Panel rendering and management for different visualization libraries.

Panel Manager
=============

.. autoclass:: trelliscope.panels.PanelManager
   :members:
   :undoc-members:
   :show-inheritance:
   :special-members: __init__

Panel Renderer
==============

.. autoclass:: trelliscope.panels.PanelRenderer
   :members:
   :undoc-members:
   :show-inheritance:

Visualization Adapters
======================

Matplotlib Adapter
------------------

.. autoclass:: trelliscope.panels.MatplotlibAdapter
   :members:
   :undoc-members:
   :show-inheritance:

Plotly Adapter
--------------

.. autoclass:: trelliscope.panels.PlotlyAdapter
   :members:
   :undoc-members:
   :show-inheritance:

Panel Interfaces
================

.. autoclass:: trelliscope.PanelInterface
   :members:
   :undoc-members:
   :show-inheritance:

LocalPanelInterface
-------------------

.. autoclass:: trelliscope.LocalPanelInterface
   :members:
   :undoc-members:
   :show-inheritance:

RESTPanelInterface
------------------

.. autoclass:: trelliscope.RESTPanelInterface
   :members:
   :undoc-members:
   :show-inheritance:

WebSocketPanelInterface
-----------------------

.. autoclass:: trelliscope.WebSocketPanelInterface
   :members:
   :undoc-members:
   :show-inheritance:

Factory Function
----------------

.. autofunction:: trelliscope.create_panel_interface

Examples
========

Matplotlib Panels
-----------------

.. code-block:: python

   import matplotlib.pyplot as plt
   import pandas as pd
   from trelliscope import Display

   def create_plot(data):
       fig, ax = plt.subplots()
       ax.plot(data['x'], data['y'])
       return fig

   plots = [create_plot(group) for _, group in df.groupby('category')]

   display_df = pd.DataFrame({
       'plot': plots,
       'category': df['category'].unique()
   })

   display = Display(display_df, name="matplotlib_example")
   display.set_panel_column("plot")
   display.write()

Plotly Panels
-------------

.. code-block:: python

   import plotly.graph_objects as go
   import pandas as pd
   from trelliscope import Display

   def create_plotly(data):
       fig = go.Figure()
       fig.add_trace(go.Scatter(x=data['x'], y=data['y']))
       return fig

   plots = [create_plotly(group) for _, group in df.groupby('category')]

   display_df = pd.DataFrame({
       'plot': plots,
       'category': df['category'].unique()
   })

   display = Display(display_df, name="plotly_example")
   display.set_panel_column("plot")
   display.write()

File Paths
----------

.. code-block:: python

   from pathlib import Path
   import pandas as pd
   from trelliscope import Display

   # Pre-generated plots
   plot_paths = [
       Path("plots/plot1.png"),
       Path("plots/plot2.png"),
       Path("plots/plot3.png")
   ]

   display_df = pd.DataFrame({
       'plot': [str(p) for p in plot_paths],
       'id': [1, 2, 3]
   })

   display = Display(display_df, name="file_example")
   display.set_panel_column("plot")
   display.write()

Custom Panel Interface
----------------------

.. code-block:: python

   from trelliscope import Display, RESTPanelInterface

   # REST API panels
   interface = RESTPanelInterface(
       base_url="http://localhost:5001/api/panels"
   )

   display = Display(df, name="rest_example")
   display.set_panel_interface(interface)
   display.write()

Supported Panel Types
=====================

Static Images
-------------

* **PNG**: Standard raster format (matplotlib default)
* **JPEG**: Compressed raster format
* **SVG**: Vector format (matplotlib with svg backend)

Interactive HTML
----------------

* **Plotly HTML**: Self-contained interactive plots
* **Bokeh HTML**: Interactive visualizations
* **Custom HTML**: Any HTML content

Panel Sources
=============

1. **Figure Objects**: matplotlib.Figure, plotly.Figure
2. **File Paths**: Strings or Path objects to image files
3. **HTML Strings**: Raw HTML content
4. **REST URLs**: Dynamic loading from API
5. **WebSocket**: Streaming panel updates

See Also
========

* :doc:`display` - Display class configuration
* :doc:`../user_guide/panel_types` - Panel type guide
* :doc:`../advanced/custom_panels` - Creating custom panels
