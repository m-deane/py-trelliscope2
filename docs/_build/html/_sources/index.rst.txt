.. py-trelliscope documentation master file

=====================================
py-trelliscope Documentation
=====================================

**Interactive visualization displays for exploring collections of plots**

py-trelliscope is a Python port of R's trelliscope package, enabling interactive exploration of large collections of visualizations through automatic faceting, filtering, sorting, and rich metadata.

.. image:: https://img.shields.io/badge/version-0.1.0-blue.svg
   :alt: Version 0.1.0

.. image:: https://img.shields.io/badge/python-3.8+-blue.svg
   :alt: Python 3.8+

Key Features
============

* **Interactive Exploration**: Explore hundreds to millions of plots with faceted layouts
* **Rich Metadata**: Filter and sort by cognostics (metadata variables)
* **Multiple Panel Types**: Support for static PNG (matplotlib) and interactive HTML (Plotly)
* **Self-Contained Viewer**: React/Redux viewer with no server required
* **Language-Agnostic**: JSON specification format compatible with R trelliscope

Quick Start
===========

Installation
------------

.. code-block:: bash

   # Basic installation
   pip install py-trelliscope

   # With visualization libraries
   pip install py-trelliscope[viz]

   # Development installation
   git clone https://github.com/your-username/py-trelliscope2.git
   cd py-trelliscope2
   pip install -e ".[viz]"

Basic Usage
-----------

.. code-block:: python

   import pandas as pd
   from trelliscope import Display

   # Create DataFrame with plots and metadata
   df = pd.DataFrame({
       'plot': [fig1, fig2, fig3],
       'category': ['A', 'B', 'C'],
       'value': [10, 20, 30]
   })

   # Create interactive display
   display = (
       Display(df, name="my_display")
       .set_panel_column("plot")
       .infer_metas()
       .write()
   )

User Guide
==========

.. toctree::
   :maxdepth: 2
   :caption: User Documentation

   user_guide/getting_started
   user_guide/creating_displays
   user_guide/meta_variables
   user_guide/panel_types
   user_guide/examples

API Reference
=============

.. toctree::
   :maxdepth: 2
   :caption: API Documentation

   api/display
   api/meta
   api/panels
   api/serialization
   api/inference
   api/export
   api/server

Advanced Topics
===============

.. toctree::
   :maxdepth: 2
   :caption: Advanced Usage

   advanced/architecture
   advanced/panel_interfaces
   advanced/custom_panels
   advanced/performance
   advanced/deployment

Contributing
============

.. toctree::
   :maxdepth: 1

   contributing/development
   contributing/testing
   contributing/documentation

Indices and Tables
==================

* :ref:`genindex`
* :ref:`modindex`
* :ref:`search`

Project Links
=============

* **GitHub**: https://github.com/your-username/py-trelliscope2
* **Issue Tracker**: https://github.com/your-username/py-trelliscope2/issues
* **PyPI**: https://pypi.org/project/py-trelliscope/
* **R Trelliscope**: https://hafen.github.io/trelliscopejs/
