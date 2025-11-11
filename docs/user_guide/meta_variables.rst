==================
Meta Variables
==================

Meta variables (cognostics) provide metadata about each panel that enables filtering, sorting, and labeling.

Overview
========

What are Meta Variables?
-------------------------

Meta variables describe characteristics of each panel:

* **Categorical data**: Categories, groups, labels
* **Numeric data**: Measurements, counts, scores
* **Temporal data**: Dates, timestamps
* **Links**: URLs to related resources

They enable interactive exploration in the viewer through:

* Filtering by value ranges or categories
* Sorting panels
* Displaying panel information

Type System
===========

py-trelliscope supports 7 meta variable types:

+-------------+-------------------+---------------------------+
| Type        | Python Type       | Use Case                  |
+=============+===================+===========================+
| factor      | categorical       | Categories with levels    |
+-------------+-------------------+---------------------------+
| number      | int, float        | Continuous numeric values |
+-------------+-------------------+---------------------------+
| currency    | float             | Monetary values           |
+-------------+-------------------+---------------------------+
| date        | datetime          | Dates without time        |
+-------------+-------------------+---------------------------+
| time        | datetime          | Dates with time component |
+-------------+-------------------+---------------------------+
| href        | str               | URLs and hyperlinks       |
+-------------+-------------------+---------------------------+
| graph       | any               | Sparklines, mini-plots    |
+-------------+-------------------+---------------------------+

Automatic Inference
===================

Basic Inference
---------------

py-trelliscope can automatically infer meta variable types:

.. code-block:: python

   import pandas as pd
   from trelliscope import Display

   df = pd.DataFrame({
       'plot': [fig1, fig2, fig3],
       'category': pd.Categorical(['A', 'B', 'C']),
       'value': [10.5, 20.3, 15.7],
       'date': pd.to_datetime(['2025-01-01', '2025-01-02', '2025-01-03'])
   })

   display = Display(df, name="auto_example")
   display.set_panel_column("plot")
   display.infer_metas()  # Automatic type detection

Result:
* ``category`` → FactorMeta
* ``value`` → NumberMeta
* ``date`` → TimeMeta

Inference Rules
---------------

**Factor (categorical)**:
* pandas.Categorical type
* Object column with < 50 unique values
* Boolean columns

**Number**:
* int64, int32, float64, float32 dtypes
* Numeric object columns

**Date/Time**:
* datetime64 dtype
* Object columns with parseable date strings

Manual Definition
=================

Factor Meta
-----------

.. code-block:: python

   from trelliscope import FactorMeta

   category_meta = FactorMeta(
       varname="category",
       label="Category",
       desc="Product category",
       levels=["A", "B", "C"]
   )

   display.add_meta_def(category_meta)

Number Meta
-----------

.. code-block:: python

   from trelliscope import NumberMeta

   value_meta = NumberMeta(
       varname="value",
       label="Value",
       desc="Transaction value",
       digits=2,      # Decimal places
       locale=True    # Use locale formatting
   )

   display.add_meta_def(value_meta)

Currency Meta
-------------

.. code-block:: python

   from trelliscope import CurrencyMeta

   price_meta = CurrencyMeta(
       varname="price",
       label="Price (USD)",
       desc="Product price",
       code="USD",
       digits=2
   )

   display.add_meta_def(price_meta)

Date Meta
---------

.. code-block:: python

   from trelliscope import DateMeta

   date_meta = DateMeta(
       varname="date",
       label="Transaction Date",
       desc="Date of transaction"
   )

   display.add_meta_def(date_meta)

Time Meta
---------

.. code-block:: python

   from trelliscope import TimeMeta

   time_meta = TimeMeta(
       varname="timestamp",
       label="Timestamp",
       desc="Event timestamp with timezone"
   )

   display.add_meta_def(time_meta)

Href Meta
---------

.. code-block:: python

   from trelliscope import HrefMeta

   link_meta = HrefMeta(
       varname="url",
       label="Documentation",
       desc="Link to product documentation"
   )

   display.add_meta_def(link_meta)

Graph Meta
----------

For mini-visualizations:

.. code-block:: python

   from trelliscope import GraphMeta

   graph_meta = GraphMeta(
       varname="sparkline",
       label="Trend",
       desc="7-day trend sparkline"
   )

   display.add_meta_def(graph_meta)

Mixed Approach
==============

Combine automatic and manual:

.. code-block:: python

   from trelliscope import Display, NumberMeta

   display = Display(df, name="mixed_example")
   display.set_panel_column("plot")

   # Manual for important columns
   display.add_meta_def(
       NumberMeta("revenue", label="Revenue (USD)", digits=2)
   )

   # Automatic for the rest
   display.infer_metas()

This approach:
1. Defines critical meta variables explicitly
2. Infers remaining columns automatically

Advanced Usage
==============

Excluding Columns
-----------------

.. code-block:: python

   # Don't create metas for these columns
   display.infer_metas(exclude=['internal_id', 'temp_col'])

Custom Labels
-------------

.. code-block:: python

   from trelliscope import NumberMeta

   display.add_meta_def(
       NumberMeta(
           varname="gdp",
           label="GDP (Billions USD)",  # Custom label
           desc="Gross domestic product in billions"
       )
   )

Conditional Formatting
----------------------

.. code-block:: python

   # Number with conditional precision
   if df['value'].max() > 1000:
       digits = 0  # No decimals for large numbers
   else:
       digits = 2

   display.add_meta_def(
       NumberMeta("value", digits=digits)
   )

Meta Variable Properties
=========================

All meta variables support:

varname
-------
Column name in DataFrame (required)

label
-----
Display name in viewer (defaults to varname)

desc
----
Tooltip description in viewer

Type-Specific Properties
------------------------

**NumberMeta / CurrencyMeta**:
* ``digits``: Decimal places to display
* ``locale``: Use locale-specific formatting

**CurrencyMeta**:
* ``code``: Currency code (USD, EUR, etc.)

**FactorMeta**:
* ``levels``: Ordered list of valid values

Examples
========

E-commerce Display
------------------

.. code-block:: python

   from trelliscope import Display, FactorMeta, CurrencyMeta, NumberMeta

   display = (
       Display(df, name="products")
       .set_panel_column("product_image")
       .add_meta_def(FactorMeta("category", levels=["Electronics", "Clothing", "Books"]))
       .add_meta_def(CurrencyMeta("price", code="USD", digits=2))
       .add_meta_def(NumberMeta("rating", digits=1))
       .add_meta_def(NumberMeta("reviews", digits=0))
       .write()
   )

Time Series Display
-------------------

.. code-block:: python

   from trelliscope import Display, TimeMeta, NumberMeta

   display = (
       Display(df, name="timeseries")
       .set_panel_column("plot")
       .add_meta_def(TimeMeta("timestamp"))
       .add_meta_def(NumberMeta("value", digits=2))
       .add_meta_def(NumberMeta("change_pct", digits=1))
       .write()
   )

Geographic Display
------------------

.. code-block:: python

   from trelliscope import Display, FactorMeta, NumberMeta, HrefMeta

   display = (
       Display(df, name="countries")
       .set_panel_column("map")
       .add_meta_def(FactorMeta("continent"))
       .add_meta_def(FactorMeta("country"))
       .add_meta_def(NumberMeta("population", digits=0, locale=True))
       .add_meta_def(HrefMeta("wiki_url", label="Wikipedia"))
       .write()
   )

Best Practices
==============

1. **Explicit is Better**: Define important meta variables explicitly
2. **Meaningful Labels**: Use clear, descriptive labels
3. **Appropriate Types**: Choose the right meta type for your data
4. **Consistent Formatting**: Use consistent decimal places and formats
5. **Add Descriptions**: Provide helpful tooltip descriptions

See Also
========

* :doc:`creating_displays` - Display configuration
* :doc:`../api/meta` - Full meta variable API
* :doc:`../api/inference` - Inference details
