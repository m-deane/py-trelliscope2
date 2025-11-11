==================
Getting Started
==================

This guide will help you get started with py-trelliscope for creating interactive visualization displays.

Installation
============

Basic Installation
------------------

Install the core package:

.. code-block:: bash

   pip install py-trelliscope

With Visualization Libraries
-----------------------------

Install with matplotlib and plotly support:

.. code-block:: bash

   pip install py-trelliscope[viz]

Development Installation
------------------------

For development work:

.. code-block:: bash

   git clone https://github.com/your-username/py-trelliscope2.git
   cd py-trelliscope2
   pip install -e ".[viz]"

Requirements
============

* Python 3.8 or higher
* pandas >= 1.0
* numpy >= 1.19

Optional dependencies:

* matplotlib >= 3.0 (for static plots)
* plotly >= 5.0 (for interactive plots)

Core Concepts
=============

Display
-------

A **Display** is a collection of plots (panels) with associated metadata (cognostics). Each row in your DataFrame represents one panel.

Panels
------

**Panels** are the visualizations in your display. They can be:

* matplotlib figures
* plotly figures
* Image file paths
* HTML content

Cognostics (Meta Variables)
----------------------------

**Cognostics** are metadata variables that describe each panel. They enable:

* Filtering by value ranges or categories
* Sorting panels
* Labeling panels in the viewer

Quick Example
=============

Here's a complete example creating a trelliscope display:

.. code-block:: python

   import pandas as pd
   import matplotlib.pyplot as plt
   from trelliscope import Display

   # Create sample data
   data = pd.DataFrame({
       'category': ['A', 'B', 'C'],
       'value': [10, 20, 15]
   })

   # Create plots
   def create_plot(cat, val):
       fig, ax = plt.subplots(figsize=(5, 3))
       ax.bar([cat], [val])
       ax.set_ylim(0, 25)
       return fig

   data['plot'] = [create_plot(cat, val)
                   for cat, val in zip(data['category'], data['value'])]

   # Create display
   display = Display(data, name="first_display", description="My first display")
   display.set_panel_column("plot")
   display.infer_metas()  # Auto-detect cognostic types
   display.write()

   # View in browser
   display.view()

What's Happening
================

1. **Create Data**: We create a DataFrame with categories and values
2. **Generate Plots**: We create matplotlib figures for each row
3. **Create Display**: We instantiate a Display object with our data
4. **Set Panel Column**: We specify which column contains the plots
5. **Infer Meta Variables**: We automatically detect cognostic types
6. **Write Output**: We generate the JSON specification and panel files
7. **View**: We open the interactive viewer in a browser

Fluent API
==========

py-trelliscope supports method chaining for cleaner code:

.. code-block:: python

   display = (
       Display(data, name="first_display")
       .set_panel_column("plot")
       .set_default_layout(ncol=3, nrow=2)
       .set_default_labels(["category", "value"])
       .infer_metas()
       .write()
   )

Output Structure
================

Running ``display.write()`` creates this structure:

.. code-block:: text

   trelliscope_output/
   ├── config.json
   ├── displays/
   │   ├── displayList.json
   │   └── first_display/
   │       ├── displayInfo.json
   │       ├── metaData.json
   │       ├── metaData.js
   │       └── panels/
   │           ├── 0.png
   │           ├── 1.png
   │           └── 2.png
   └── index.html

Next Steps
==========

* :doc:`creating_displays` - Learn display configuration options
* :doc:`meta_variables` - Understand cognostic types
* :doc:`panel_types` - Explore panel rendering options
* :doc:`examples` - See complete examples

See Also
========

* :doc:`../api/display` - Full Display API reference
* :doc:`../api/meta` - Meta variable types
