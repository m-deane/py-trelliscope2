==================
Meta Variables API
==================

Meta variables (cognostics) provide metadata about each panel that enables filtering, sorting, and labeling in the viewer.

Base Class
==========

.. autoclass:: trelliscope.MetaVariable
   :members:
   :undoc-members:
   :show-inheritance:
   :special-members: __init__

Meta Variable Types
===================

FactorMeta
----------

Categorical variables with defined levels.

.. autoclass:: trelliscope.FactorMeta
   :members:
   :undoc-members:
   :show-inheritance:
   :special-members: __init__

NumberMeta
----------

Numeric continuous variables.

.. autoclass:: trelliscope.NumberMeta
   :members:
   :undoc-members:
   :show-inheritance:
   :special-members: __init__

CurrencyMeta
------------

Monetary values with formatting.

.. autoclass:: trelliscope.CurrencyMeta
   :members:
   :undoc-members:
   :show-inheritance:
   :special-members: __init__

DateMeta
--------

Date values without time component.

.. autoclass:: trelliscope.DateMeta
   :members:
   :undoc-members:
   :show-inheritance:
   :special-members: __init__

TimeMeta
--------

Datetime/timestamp values.

.. autoclass:: trelliscope.TimeMeta
   :members:
   :undoc-members:
   :show-inheritance:
   :special-members: __init__

HrefMeta
--------

Hyperlinks with optional labels.

.. autoclass:: trelliscope.HrefMeta
   :members:
   :undoc-members:
   :show-inheritance:
   :special-members: __init__

GraphMeta
---------

Sparklines and mini-visualizations.

.. autoclass:: trelliscope.GraphMeta
   :members:
   :undoc-members:
   :show-inheritance:
   :special-members: __init__

Type Inference
==============

Automatic type inference from pandas Series.

.. autofunction:: trelliscope.infer_meta_from_series

.. autofunction:: trelliscope.infer_meta_dict

Examples
========

Creating Meta Variables
-----------------------

.. code-block:: python

   from trelliscope import FactorMeta, NumberMeta, DateMeta

   # Factor (categorical)
   category_meta = FactorMeta(
       varname="category",
       label="Category",
       levels=["A", "B", "C"]
   )

   # Number
   value_meta = NumberMeta(
       varname="value",
       label="Value",
       digits=2,
       locale=True
   )

   # Date
   date_meta = DateMeta(
       varname="date",
       label="Date"
   )

Auto-Inference
--------------

.. code-block:: python

   import pandas as pd
   from trelliscope import Display

   df = pd.DataFrame({
       'plot': [fig1, fig2],
       'category': pd.Categorical(['A', 'B']),
       'value': [10.5, 20.3],
       'date': pd.to_datetime(['2025-01-01', '2025-01-02'])
   })

   # Automatic inference
   display = Display(df, name="auto_example")
   display.infer_metas()  # Infers factor, number, date types

Manual Override
---------------

.. code-block:: python

   from trelliscope import Display, NumberMeta

   display = Display(df, name="manual_example")

   # Override inference for specific column
   display.add_meta_def(NumberMeta("value", digits=1))

   # Infer rest automatically
   display.infer_metas()

Currency Formatting
-------------------

.. code-block:: python

   from trelliscope import CurrencyMeta

   price_meta = CurrencyMeta(
       varname="price",
       label="Price (USD)",
       code="USD",
       digits=2
   )

Hyperlinks
----------

.. code-block:: python

   from trelliscope import HrefMeta

   link_meta = HrefMeta(
       varname="url",
       label="Documentation Link"
   )

Type Mapping
============

Pandas dtype to Meta type inference:

================= ==================
Pandas dtype      Meta type
================= ==================
category          FactorMeta
int64, float64    NumberMeta
datetime64        TimeMeta
object (dates)    DateMeta or TimeMeta
object (strings)  FactorMeta (if few unique values)
================= ==================

See Also
========

* :doc:`display` - Display class using meta variables
* :doc:`inference` - Type inference details
