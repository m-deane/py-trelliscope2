==================
Display API
==================

The :class:`~trelliscope.Display` class is the main entry point for creating interactive trelliscope displays.

Display Class
=============

.. autoclass:: trelliscope.Display
   :members:
   :undoc-members:
   :show-inheritance:
   :special-members: __init__

Core Methods
============

Creating Displays
-----------------

.. automethod:: trelliscope.Display.__init__

Configuration
-------------

.. automethod:: trelliscope.Display.set_panel_column
.. automethod:: trelliscope.Display.set_default_layout
.. automethod:: trelliscope.Display.set_default_labels
.. automethod:: trelliscope.Display.set_default_filters
.. automethod:: trelliscope.Display.set_default_sorts

Meta Variables
--------------

.. automethod:: trelliscope.Display.add_meta_def
.. automethod:: trelliscope.Display.infer_metas
.. automethod:: trelliscope.Display.set_metas

Views
-----

.. automethod:: trelliscope.Display.add_view

Output
------

.. automethod:: trelliscope.Display.write
.. automethod:: trelliscope.Display.view

Panel Options
-------------

.. automethod:: trelliscope.Display.set_panel_options

Examples
========

Basic Display
-------------

.. code-block:: python

   import pandas as pd
   from trelliscope import Display

   df = pd.DataFrame({
       'plot': [fig1, fig2, fig3],
       'category': ['A', 'B', 'C'],
       'value': [10, 20, 30]
   })

   display = Display(df, name="basic_example")
   display.set_panel_column("plot")
   display.write()

Fluent API
----------

.. code-block:: python

   display = (
       Display(df, name="fluent_example")
       .set_panel_column("plot")
       .set_default_layout(ncol=3, nrow=2)
       .set_default_labels(["category", "value"])
       .infer_metas()
       .write()
   )

With Custom Metas
-----------------

.. code-block:: python

   from trelliscope import Display, NumberMeta, FactorMeta

   display = (
       Display(df, name="custom_meta_example")
       .set_panel_column("plot")
       .add_meta_def(FactorMeta("category", levels=["A", "B", "C"]))
       .add_meta_def(NumberMeta("value", digits=2))
       .write()
   )

With Views
----------

.. code-block:: python

   display = (
       Display(df, name="views_example")
       .set_panel_column("plot")
       .add_view(
           name="high_values",
           filter_list=[{"type": "range", "varname": "value", "min": 20}],
           sort_list=[{"varname": "value", "dir": "desc"}]
       )
       .write()
   )

See Also
========

* :doc:`meta` - Meta variable types and inference
* :doc:`panels` - Panel rendering and management
* :doc:`serialization` - JSON output format
