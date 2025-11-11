==================
Creating Displays
==================

This guide covers display creation and configuration options.

Basic Display Creation
======================

Minimum Requirements
--------------------

A display requires:

1. A pandas DataFrame
2. A unique name
3. A panel column designation

.. code-block:: python

   from trelliscope import Display
   import pandas as pd

   df = pd.DataFrame({
       'plot': [fig1, fig2, fig3],
       'category': ['A', 'B', 'C']
   })

   display = Display(df, name="basic_display")
   display.set_panel_column("plot")
   display.write()

With Description
----------------

Add a human-readable description:

.. code-block:: python

   display = Display(
       df,
       name="basic_display",
       description="Analysis of categories A, B, and C"
   )

Custom Output Path
------------------

Specify where files are written:

.. code-block:: python

   from pathlib import Path

   display = Display(
       df,
       name="basic_display",
       path=Path("custom_output")
   )

Layout Configuration
====================

Default Layout
--------------

Set the default panel grid layout:

.. code-block:: python

   display = Display(df, name="layout_example")
   display.set_default_layout(ncol=4, nrow=3)

This creates a 4-column, 3-row grid (12 panels per page).

Page Size
---------

Configure pagination:

.. code-block:: python

   display.set_default_layout(
       ncol=5,
       nrow=4,
       page=1  # Start on first page
   )

Arrangement
-----------

Control panel ordering:

.. code-block:: python

   # Row-wise arrangement (default)
   display.set_default_layout(arrangement="row")

   # Column-wise arrangement
   display.set_default_layout(arrangement="col")

Labels Configuration
====================

Default Labels
--------------

Set which variables appear as panel labels:

.. code-block:: python

   display.set_default_labels(["category", "value"])

The viewer displays these as text overlays on panels.

No Labels
---------

.. code-block:: python

   display.set_default_labels([])

Filtering Configuration
=======================

Filters allow users to narrow down panels in the viewer.

Number Range Filters
--------------------

.. code-block:: python

   display.set_default_filters([
       {
           "type": "range",
           "varname": "value",
           "min": 10,
           "max": 50
       }
   ])

Category Filters
----------------

.. code-block:: python

   display.set_default_filters([
       {
           "type": "category",
           "varname": "category",
           "values": ["A", "B"]  # Show only A and B
       }
   ])

Multiple Filters
----------------

Combine multiple filters:

.. code-block:: python

   display.set_default_filters([
       {"type": "range", "varname": "value", "min": 10},
       {"type": "category", "varname": "category", "values": ["A"]}
   ])

Sorting Configuration
=====================

Single Sort
-----------

.. code-block:: python

   display.set_default_sorts([
       {"varname": "value", "dir": "desc"}
   ])

Multiple Sorts
--------------

Sorts are applied in order (precedence):

.. code-block:: python

   display.set_default_sorts([
       {"varname": "category", "dir": "asc"},   # Primary
       {"varname": "value", "dir": "desc"}      # Secondary
   ])

Panel Options
=============

Panel Dimensions
----------------

.. code-block:: python

   display.set_panel_options(
       width=600,
       height=400
   )

Aspect Ratio
------------

.. code-block:: python

   display.set_panel_options(
       aspect=1.5  # Width/height ratio
   )

Views
=====

Create Named Views
------------------

Views are predefined display configurations:

.. code-block:: python

   display.add_view(
       name="high_values",
       filter_list=[{"type": "range", "varname": "value", "min": 20}],
       sort_list=[{"varname": "value", "dir": "desc"}],
       layout={"ncol": 3, "nrow": 2}
   )

Multiple Views
--------------

.. code-block:: python

   display.add_view(
       name="view_a",
       filter_list=[{"type": "category", "varname": "category", "values": ["A"]}]
   )

   display.add_view(
       name="view_b",
       filter_list=[{"type": "category", "varname": "category", "values": ["B"]}]
   )

Complete Example
================

Here's a fully configured display:

.. code-block:: python

   from trelliscope import Display, NumberMeta, FactorMeta
   from pathlib import Path

   display = (
       Display(
           df,
           name="complete_example",
           description="Comprehensive display configuration",
           path=Path("output")
       )
       .set_panel_column("plot")
       .add_meta_def(FactorMeta("category", levels=["A", "B", "C"]))
       .add_meta_def(NumberMeta("value", digits=2))
       .set_default_layout(ncol=4, nrow=3)
       .set_default_labels(["category", "value"])
       .set_default_filters([
           {"type": "range", "varname": "value", "min": 10}
       ])
       .set_default_sorts([
           {"varname": "value", "dir": "desc"}
       ])
       .add_view(
           name="high_values",
           filter_list=[{"type": "range", "varname": "value", "min": 20}]
       )
       .set_panel_options(width=500, height=400)
       .write()
   )

Writing and Viewing
===================

Write to Disk
-------------

.. code-block:: python

   display.write()

This generates all JSON files and panel assets.

View in Browser
---------------

.. code-block:: python

   display.view()

This starts a local server and opens the viewer.

Write and View
--------------

.. code-block:: python

   display.write().view()

Method chaining works after write().

Best Practices
==============

1. **Unique Names**: Use descriptive, unique names for displays
2. **Descriptions**: Always provide clear descriptions
3. **Meta Variables**: Define explicit meta variables for important columns
4. **Layout**: Choose layouts that make sense for your data
5. **Views**: Create views for common exploration patterns
6. **Testing**: Test with small datasets first

See Also
========

* :doc:`meta_variables` - Configuring cognostics
* :doc:`panel_types` - Panel rendering options
* :doc:`../api/display` - Full API reference
