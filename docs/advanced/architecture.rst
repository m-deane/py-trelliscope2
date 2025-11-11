==================
Architecture
==================

py-trelliscope uses a 3-tier hybrid architecture.

Overview
========

Architecture Layers
-------------------

1. **Python Backend**: Data processing and JSON generation
2. **File System**: JSON specifications and panel assets
3. **JavaScript Viewer**: React/Redux interactive viewer

This separation enables:

* Language-agnostic specifications
* Reuse of existing viewer infrastructure
* Flexible deployment options

Python Backend
==============

Core Components
---------------

Display Class
^^^^^^^^^^^^^

Primary interface for creating displays:

* DataFrame validation
* Meta variable inference
* Panel rendering
* JSON serialization

Meta Variable System
^^^^^^^^^^^^^^^^^^^^

Type hierarchy for cognostics:

* Base MetaVariable class
* Specialized types (Factor, Number, etc.)
* Auto-inference engine
* Type validation

Panel Management
^^^^^^^^^^^^^^^^

Panel rendering and storage:

* Adapter pattern for visualization libraries
* File system management
* Panel interface abstractions

Serialization
^^^^^^^^^^^^^

JSON output generation:

* displayInfo.json writer
* metaData.json/js writers
* Schema validation

File System Layer
=================

Directory Structure
-------------------

.. code-block:: text

   {appdir}/
   ├── config.json              # Multi-display configuration
   ├── displays/
   │   ├── displayList.json     # Display registry
   │   └── {display_name}/
   │       ├── displayInfo.json # Display specification
   │       ├── metaData.json    # Panel metadata (JSON)
   │       ├── metaData.js      # Panel metadata (JS)
   │       └── panels/
   │           ├── 0.png        # Panel files
   │           └── ...

JSON Specifications
-------------------

displayInfo.json
^^^^^^^^^^^^^^^^

Complete display configuration:

.. code-block:: json

   {
     "name": "display_name",
     "description": "...",
     "n": 100,
     "metas": [...],
     "cogData": [...],
     "state": {...},
     "panelInterface": {...}
   }

metaData.json
^^^^^^^^^^^^^

Separate metadata for viewer:

.. code-block:: json

   [
     {
       "panelKey": "0",
       "panel": "panels/0.png",
       "category": "A",
       "value": 10
     }
   ]

metaData.js
^^^^^^^^^^^

Browser-loadable metadata:

.. code-block:: javascript

   window.metaData = [...];

JavaScript Viewer
=================

Technology Stack
----------------

* **React**: UI components
* **Redux**: State management
* **trelliscopejs-lib**: Viewer library (v0.7.16)

Viewer Features
---------------

* Panel grid layout
* Interactive filtering
* Sorting and labeling
* View management
* Panel detail view

Data Flow
=========

Display Creation Flow
---------------------

1. User creates DataFrame with panels and metadata
2. Display class validates and processes data
3. Meta variables inferred or specified
4. Panels rendered to files
5. JSON specifications generated
6. Files written to disk
7. Viewer loads JSON and displays panels

Viewer Loading Flow
-------------------

1. Browser loads index.html
2. Viewer JavaScript initializes
3. Loads displayInfo.json
4. Loads metaData.js
5. Renders panel grid
6. Loads panel files on demand
7. Applies filters/sorts from state

Panel Interfaces
================

File-Based (Local)
------------------

Panels stored as files on disk:

* **Type**: ``file`` or ``iframe``
* **Formats**: PNG, JPEG, HTML
* **Loading**: Direct file access

REST API
--------

Panels loaded from HTTP endpoints:

* **Type**: ``rest``
* **Protocol**: HTTP GET
* **Format**: JSON with base64 or URLs

WebSocket
---------

Streaming panel updates:

* **Type**: ``websocket``
* **Protocol**: WebSocket
* **Use case**: Real-time updates

Design Patterns
===============

Adapter Pattern
---------------

Used for visualization library integration:

* MatplotlibAdapter
* PlotlyAdapter
* Extensible for new libraries

Builder Pattern
---------------

Fluent API for display configuration:

.. code-block:: python

   display = (
       Display(df, name="example")
       .set_panel_column("plot")
       .set_default_layout(ncol=4)
       .write()
   )

Strategy Pattern
----------------

Panel interface selection:

* LocalPanelInterface
* RESTPanelInterface
* WebSocketPanelInterface

Performance Considerations
==========================

Scalability
-----------

* **Small (< 100 panels)**: All strategies work well
* **Medium (100-1,000)**: File-based preferred
* **Large (1,000-10,000)**: Lazy loading recommended
* **Very Large (> 10,000)**: REST/WebSocket required

Memory Management
-----------------

* Stream panel generation
* Close matplotlib figures immediately
* Use lazy evaluation where possible

File Size Optimization
----------------------

* PNG: 60-80 KB per panel
* JPEG: 30-50 KB per panel (lossy)
* HTML: 15-20 KB per panel (Plotly)

Choose format based on needs vs size tradeoffs.

Extension Points
================

Custom Meta Types
-----------------

Extend MetaVariable base class:

.. code-block:: python

   @attrs.define
   class CustomMeta(MetaVariable):
       type: str = attrs.field(init=False, default="custom")
       custom_field: str = ""

       def to_dict(self):
           result = super().to_dict()
           result['customField'] = self.custom_field
           return result

Custom Panel Adapters
---------------------

Implement PanelRenderer interface:

.. code-block:: python

   class CustomAdapter(PanelRenderer):
       def can_render(self, obj):
           return isinstance(obj, CustomFigure)

       def render(self, obj, output_path):
           # Rendering logic
           pass

Custom Panel Interfaces
-----------------------

Extend PanelInterface base class:

.. code-block:: python

   class CustomPanelInterface(PanelInterface):
       def to_dict(self):
           return {
               "type": "custom",
               "endpoint": self.endpoint
           }

See Also
========

* :doc:`panel_interfaces` - Panel interface details
* :doc:`custom_panels` - Creating custom panels
* :doc:`performance` - Optimization strategies
