==================
Export API
==================

Export utilities for static deployment and validation.

Core Functions
==============

Static Export
-------------

.. autofunction:: trelliscope.export_static

.. autofunction:: trelliscope.export_static_from_display

Validation
----------

.. autofunction:: trelliscope.validate_export

Examples
========

Basic Export
------------

.. code-block:: python

   from trelliscope import Display, export_static

   display = Display(df, name="example")
   display.set_panel_column("plot")

   # Export to directory
   export_static(display, output_dir="deploy")

Export from Display
-------------------

.. code-block:: python

   from trelliscope import export_static_from_display

   # Export already-written display
   export_static_from_display(
       display_path="output/example",
       output_dir="deploy",
       include_viewer=True
   )

Validation
----------

.. code-block:: python

   from trelliscope import validate_export

   # Validate export structure
   is_valid, errors = validate_export("deploy/example")

   if not is_valid:
       for error in errors:
           print(f"Error: {error}")

Multiple Displays
-----------------

.. code-block:: python

   from trelliscope import Display, export_static
   from pathlib import Path

   # Create multiple displays
   display1 = Display(df1, name="display1", path="output")
   display1.set_panel_column("plot").write()

   display2 = Display(df2, name="display2", path="output")
   display2.set_panel_column("plot").write()

   # Export all from same directory
   export_static(
       [display1, display2],
       output_dir="deploy"
   )

See Also
========

* :doc:`display` - Display class
* :doc:`server` - Development server
