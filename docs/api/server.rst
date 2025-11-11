==================
Server API
==================

Development server for local testing and preview.

DisplayServer
=============

.. autoclass:: trelliscope.DisplayServer
   :members:
   :undoc-members:
   :show-inheritance:
   :special-members: __init__

Examples
========

Basic Server
------------

.. code-block:: python

   from trelliscope import DisplayServer

   server = DisplayServer(
       display_dir="output",
       port=8000,
       host="localhost"
   )

   server.start()

With Display Creation
---------------------

.. code-block:: python

   from trelliscope import Display, DisplayServer

   # Create display
   display = Display(df, name="example", path="output")
   display.set_panel_column("plot").write()

   # Serve
   server = DisplayServer(display_dir="output")
   server.start()

Multiple Displays
-----------------

.. code-block:: python

   from trelliscope import DisplayServer

   # Serve directory with multiple displays
   server = DisplayServer(
       display_dir="output",
       port=8000
   )

   server.start()
   # Navigate to http://localhost:8000/

Custom Configuration
--------------------

.. code-block:: python

   from trelliscope import DisplayServer

   server = DisplayServer(
       display_dir="output",
       port=8080,
       host="0.0.0.0",  # Allow external connections
       auto_open=True    # Open browser automatically
   )

   server.start()

See Also
========

* :doc:`display` - Display class
* :doc:`export` - Static export for production
