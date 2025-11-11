==================
Panel Types
==================

py-trelliscope supports multiple panel formats for different visualization needs.

Overview
========

Panel Types
-----------

* **Static Images**: PNG, JPEG (matplotlib, saved images)
* **Interactive HTML**: Plotly, Bokeh, custom HTML
* **Mixed**: Different types in same display

Panel Sources
-------------

* Figure objects (matplotlib.Figure, plotly.Figure)
* File paths (strings, Path objects)
* HTML strings
* URLs (REST, WebSocket)

Matplotlib Panels (PNG)
========================

Basic Usage
-----------

.. code-block:: python

   import matplotlib.pyplot as plt
   import pandas as pd
   from trelliscope import Display

   def create_plot(data):
       fig, ax = plt.subplots(figsize=(6, 4))
       ax.plot(data['x'], data['y'])
       ax.set_title(f"Category {data['category'].iloc[0]}")
       return fig

   # Create plots for each group
   plots = []
   categories = []
   for category, group in df.groupby('category'):
       plots.append(create_plot(group))
       categories.append(category)

   display_df = pd.DataFrame({
       'plot': plots,
       'category': categories
   })

   display = (
       Display(display_df, name="matplotlib_example")
       .set_panel_column("plot")
       .write()
   )

Panel Configuration
-------------------

.. code-block:: python

   # Configure panel dimensions
   display.set_panel_options(
       width=600,
       height=400
   )

Output Format
-------------

Matplotlib figures are saved as PNG files:

* Default: 96 DPI
* Format: PNG with transparency
* Naming: ``0.png``, ``1.png``, etc.

Advanced Matplotlib
-------------------

.. code-block:: python

   import matplotlib.pyplot as plt

   def create_advanced_plot(data):
       fig, (ax1, ax2) = plt.subplots(1, 2, figsize=(10, 4))

       # Plot 1
       ax1.plot(data['x'], data['y'])
       ax1.set_title("Time Series")

       # Plot 2
       ax2.bar(data['category'], data['value'])
       ax2.set_title("Bar Chart")

       plt.tight_layout()
       return fig

Plotly Panels (HTML)
====================

Basic Usage
-----------

.. code-block:: python

   import plotly.graph_objects as go
   import pandas as pd
   from trelliscope import Display

   def create_plotly_plot(data):
       fig = go.Figure()
       fig.add_trace(go.Scatter(
           x=data['x'],
           y=data['y'],
           mode='lines+markers'
       ))
       fig.update_layout(
           title=f"Category {data['category'].iloc[0]}",
           width=500,
           height=400
       )
       return fig

   # Create plots for each group
   plots = []
   categories = []
   for category, group in df.groupby('category'):
       plots.append(create_plotly_plot(group))
       categories.append(category)

   display_df = pd.DataFrame({
       'plot': plots,
       'category': categories
   })

   display = (
       Display(display_df, name="plotly_example")
       .set_panel_column("plot")
       .write()
   )

Interactive Features
--------------------

Plotly panels automatically include:

* Hover tooltips with exact values
* Zoom and pan controls
* Plotly toolbar (download, reset, etc.)
* Interactive legend

Fixed vs Responsive
-------------------

**Fixed dimensions**:

.. code-block:: python

   fig.update_layout(
       width=500,
       height=400
   )

**Responsive sizing**:

.. code-block:: python

   fig.update_layout(
       autosize=True
   )

Note: Fixed dimensions provide consistency; responsive adapts to container.

Output Format
-------------

Plotly figures are saved as self-contained HTML:

* Format: HTML with embedded Plotly.js
* Size: ~15-20KB per panel
* Naming: ``0.html``, ``1.html``, etc.

File Path Panels
================

Pre-generated Images
--------------------

.. code-block:: python

   from pathlib import Path
   import pandas as pd
   from trelliscope import Display

   # Use existing image files
   image_paths = [
       "/path/to/plot1.png",
       "/path/to/plot2.png",
       "/path/to/plot3.png"
   ]

   display_df = pd.DataFrame({
       'plot': image_paths,
       'id': [1, 2, 3]
   })

   display = (
       Display(display_df, name="file_example")
       .set_panel_column("plot")
       .write()
   )

The files are copied to the display's panel directory.

HTML Files
----------

.. code-block:: python

   html_paths = [
       "/path/to/chart1.html",
       "/path/to/chart2.html"
   ]

   display_df = pd.DataFrame({
       'plot': html_paths,
       'id': [1, 2]
   })

   display = (
       Display(display_df, name="html_file_example")
       .set_panel_column("plot")
       .write()
   )

Custom HTML Panels
==================

Inline HTML
-----------

.. code-block:: python

   def create_html_panel(data):
       html = f"""
       <div style="padding: 20px; background: #f0f0f0;">
           <h2>{data['title']}</h2>
           <p>Value: {data['value']}</p>
           <div style="width: 100%; height: 200px; background: #4CAF50;"></div>
       </div>
       """
       return html

   display_df['plot'] = display_df.apply(create_html_panel, axis=1)

   display = (
       Display(display_df, name="custom_html")
       .set_panel_column("plot")
       .write()
   )

With D3.js
----------

.. code-block:: python

   def create_d3_panel(data):
       html = f"""
       <!DOCTYPE html>
       <html>
       <head>
           <script src="https://d3js.org/d3.v7.min.js"></script>
       </head>
       <body>
           <svg id="chart" width="500" height="400"></svg>
           <script>
               const data = {data['values'].tolist()};
               // D3 code here
           </script>
       </body>
       </html>
       """
       return html

Mixed Panel Types
=================

You can create separate displays for different panel types:

.. code-block:: python

   # Display 1: Matplotlib
   display1 = (
       Display(df, name="static_panels")
       .set_panel_column("matplotlib_plot")
       .write()
   )

   # Display 2: Plotly
   display2 = (
       Display(df, name="interactive_panels")
       .set_panel_column("plotly_plot")
       .write()
   )

Performance Comparison
======================

File Sizes
----------

================== ============== ================
Panel Type         Size per Panel Total (100 panels)
================== ============== ================
PNG (matplotlib)   60-80 KB       6-8 MB
JPEG (matplotlib)  30-50 KB       3-5 MB
HTML (Plotly)      15-20 KB       1.5-2 MB
================== ============== ================

Loading Speed
-------------

================== ============ =============
Panel Type         Initial Load Interaction
================== ============ =============
PNG                < 1 second   None (static)
HTML (Plotly)      1-2 seconds  Instant
================== ============ =============

When to Use Each Type
=====================

Use PNG (matplotlib) When:
--------------------------

* Large number of panels (10,000+)
* Simple static visualizations
* Print-ready outputs needed
* Maximum browser compatibility
* No interactivity required

Use HTML (Plotly) When:
-----------------------

* Moderate number of panels (< 5,000)
* Complex data requiring exploration
* Hover tooltips needed
* Zoom/pan functionality useful
* Modern browsers available

Use Custom HTML When:
---------------------

* Specific interactivity requirements
* Custom visualization libraries
* Embedded content needed
* Special formatting required

Best Practices
==============

1. **Consistent Sizing**: Use consistent panel dimensions
2. **Close Figures**: Close matplotlib figures to free memory
3. **Optimize Images**: Use appropriate DPI and format
4. **Test Performance**: Test with representative data sizes
5. **Choose Wisely**: Match panel type to use case

Examples
========

Complete Matplotlib Example
---------------------------

.. code-block:: python

   import matplotlib.pyplot as plt
   import pandas as pd
   from trelliscope import Display

   def create_matplotlib_panel(row):
       fig, ax = plt.subplots(figsize=(5, 4))
       ax.plot(row['x_data'], row['y_data'])
       ax.set_title(f"{row['category']}")
       ax.set_xlabel("X")
       ax.set_ylabel("Y")
       plt.tight_layout()
       return fig

   df['plot'] = df.apply(create_matplotlib_panel, axis=1)

   display = (
       Display(df, name="matplotlib_complete")
       .set_panel_column("plot")
       .set_panel_options(width=500, height=400)
       .infer_metas()
       .write()
   )

   # Clean up
   for fig in df['plot']:
       plt.close(fig)

Complete Plotly Example
-----------------------

.. code-block:: python

   import plotly.graph_objects as go
   import pandas as pd
   from trelliscope import Display

   def create_plotly_panel(row):
       fig = go.Figure()
       fig.add_trace(go.Scatter(
           x=row['x_data'],
           y=row['y_data'],
           mode='lines+markers',
           name=row['category']
       ))
       fig.update_layout(
           title=f"{row['category']}",
           width=500,
           height=400,
           hovermode='closest'
       )
       return fig

   df['plot'] = df.apply(create_plotly_panel, axis=1)

   display = (
       Display(df, name="plotly_complete")
       .set_panel_column("plot")
       .infer_metas()
       .write()
   )

See Also
========

* :doc:`creating_displays` - Display configuration
* :doc:`../api/panels` - Panel API reference
* :doc:`../advanced/custom_panels` - Advanced panel creation
