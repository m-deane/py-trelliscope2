==================
Serialization API
==================

JSON serialization for trelliscope display specifications.

Core Functions
==============

Display Info
------------

.. autofunction:: trelliscope.serialize_display_info

.. autofunction:: trelliscope.write_display_info

Metadata Files
--------------

.. autofunction:: trelliscope.serialization.write_metadata_json

.. autofunction:: trelliscope.serialization.write_metadata_js

Utilities
---------

.. autofunction:: trelliscope.serialize_to_json_string

JSON Schema
===========

displayInfo.json Structure
---------------------------

The main display configuration file follows this schema:

.. code-block:: json

   {
     "name": "display_name",
     "description": "Display description",
     "keysig": "unique_key_signature",
     "n": 10,
     "height": 500,
     "width": 500,
     "tags": [],
     "keycols": [],
     "metas": [
       {
         "varname": "category",
         "label": "Category",
         "type": "factor",
         "levels": ["A", "B", "C"]
       }
     ],
     "cogInterface": {
       "name": "display_name",
       "group": "common",
       "type": "JSON"
     },
     "cogInfo": {},
     "cogDistns": {},
     "cogData": [],
     "state": {
       "layout": {"ncol": 3, "nrow": 2},
       "labels": ["category"],
       "filters": [],
       "sorts": []
     },
     "views": [],
     "panelInterface": {
       "type": "file",
       "base": "panels",
       "panelCol": "panel"
     }
   }

metaData.json Structure
-----------------------

Separate metadata file for viewer:

.. code-block:: json

   [
     {
       "panelKey": "0",
       "panel": "panels/0.png",
       "category": "A",
       "value": 10
     }
   ]

metaData.js Structure
---------------------

JavaScript wrapper for browser loading:

.. code-block:: javascript

   window.metaData = [
     {
       "panelKey": "0",
       "panel": "panels/0.png",
       "category": "A",
       "value": 10
     }
   ];

Panel Interface Types
=====================

File-Based Panels
-----------------

.. code-block:: json

   {
     "panelInterface": {
       "type": "file",
       "base": "panels",
       "panelCol": "panel"
     }
   }

Iframe Panels (HTML)
--------------------

.. code-block:: json

   {
     "panelInterface": {
       "type": "iframe",
       "base": "panels",
       "panelCol": "panel"
     }
   }

REST API Panels
---------------

.. code-block:: json

   {
     "panelInterface": {
       "type": "rest",
       "baseUrl": "http://localhost:5001/api/panels",
       "panelCol": "panel"
     }
   }

Examples
========

Custom Serialization
--------------------

.. code-block:: python

   from trelliscope import Display, serialize_display_info

   display = Display(df, name="example")
   display.set_panel_column("plot")

   # Serialize to dict
   config = serialize_display_info(display)

   # Modify config
   config['state']['layout']['ncol'] = 5

   # Write to file
   import json
   with open('custom_config.json', 'w') as f:
       json.dump(config, f, indent=2)

Direct JSON Output
------------------

.. code-block:: python

   from trelliscope import serialize_to_json_string

   display = Display(df, name="example")
   json_str = serialize_to_json_string(display)

   # Use in API response
   return Response(json_str, mimetype='application/json')

Validation
----------

.. code-block:: python

   from trelliscope import write_display_info
   from pathlib import Path

   display = Display(df, name="example")

   # Write with validation
   try:
       write_display_info(display, Path("output"))
   except ValueError as e:
       print(f"Invalid configuration: {e}")

See Also
========

* :doc:`display` - Display class configuration
* :doc:`export` - Export utilities
* :doc:`../advanced/architecture` - JSON specification details
