==================
Type Inference API
==================

Automatic type inference from pandas DataFrames.

Core Functions
==============

.. autofunction:: trelliscope.infer_meta_from_series

.. autofunction:: trelliscope.infer_meta_dict

Inference Rules
===============

Pandas dtype Mapping
--------------------

The inference system maps pandas dtypes to trelliscope meta variable types:

==================== =================== ===================
Pandas dtype         Meta type           Conditions
==================== =================== ===================
category             FactorMeta          Always
int64, int32         NumberMeta          Always
float64, float32     NumberMeta          Always
datetime64[ns]       TimeMeta            Always
bool                 FactorMeta          2 levels
object               FactorMeta          < 50 unique values
object               NumberMeta          Numeric strings
object               DateMeta            Date-like strings
object               TimeMeta            Datetime strings
==================== =================== ===================

Categorical Inference
---------------------

Object columns become FactorMeta when:

* Number of unique values < 50
* Number of unique values < 50% of total rows
* Values are non-numeric strings

Numeric Inference
-----------------

Columns become NumberMeta when:

* Dtype is int or float
* Object column contains only numeric strings
* Column name suggests numeric data (e.g., "count", "value")

Date/Time Inference
-------------------

Columns become DateMeta or TimeMeta when:

* Dtype is datetime64
* Object column contains ISO date strings
* Object column contains parseable date strings

Examples
========

Automatic Inference
-------------------

.. code-block:: python

   import pandas as pd
   from trelliscope import infer_meta_dict

   df = pd.DataFrame({
       'category': pd.Categorical(['A', 'B', 'C']),
       'value': [1.5, 2.3, 3.1],
       'count': [10, 20, 30],
       'date': pd.to_datetime(['2025-01-01', '2025-01-02', '2025-01-03'])
   })

   # Infer all columns
   metas = infer_meta_dict(df)

   # Results:
   # category -> FactorMeta
   # value -> NumberMeta
   # count -> NumberMeta
   # date -> TimeMeta

Single Column Inference
-----------------------

.. code-block:: python

   from trelliscope import infer_meta_from_series

   series = pd.Series(['A', 'B', 'C', 'A'])
   meta = infer_meta_from_series(series, varname='category')

   print(type(meta))  # FactorMeta
   print(meta.levels)  # ['A', 'B', 'C']

Override Inference
------------------

.. code-block:: python

   from trelliscope import Display, NumberMeta

   display = Display(df, name="example")

   # Infer most columns
   display.infer_metas()

   # Override specific column
   display.add_meta_def(NumberMeta("value", digits=1))

Selective Inference
-------------------

.. code-block:: python

   from trelliscope import infer_meta_dict

   # Infer only specific columns
   metas = infer_meta_dict(
       df[['category', 'value']],
       exclude=['panel']
   )

Custom Labels
-------------

.. code-block:: python

   from trelliscope import infer_meta_from_series

   meta = infer_meta_from_series(
       df['value'],
       varname='value',
       label='Value (USD)',
       desc='Total transaction value'
   )

Edge Cases
==========

Mixed Object Columns
--------------------

Object columns with mixed types:

.. code-block:: python

   # Mixed numeric/string
   series = pd.Series([1, 2, 'N/A', 3])
   # -> Inferred as FactorMeta

   # Mostly numeric strings
   series = pd.Series(['1.5', '2.3', '3.1'])
   # -> Inferred as NumberMeta

High Cardinality
----------------

High-cardinality categoricals:

.. code-block:: python

   # 100 unique values in 1000 rows
   series = pd.Series([f'cat_{i}' for i in range(100)] * 10)
   # -> Inferred as FactorMeta (< 50% unique)

   # 600 unique values in 1000 rows
   series = pd.Series(range(1000))
   # -> Inferred as NumberMeta (>= 50% unique)

Date Formats
------------

Various date string formats:

.. code-block:: python

   # ISO format
   dates = pd.Series(['2025-01-01', '2025-01-02'])
   # -> DateMeta

   # US format
   dates = pd.Series(['01/01/2025', '01/02/2025'])
   # -> DateMeta

   # With time
   dates = pd.Series(['2025-01-01 10:30:00', '2025-01-02 11:45:00'])
   # -> TimeMeta

Configuration
=============

Inference Parameters
--------------------

Default inference thresholds can be customized:

.. code-block:: python

   from trelliscope.inference import InferenceConfig

   config = InferenceConfig(
       max_factor_levels=100,  # Max unique values for factor
       factor_threshold=0.5,   # Max proportion unique for factor
       date_parse_attempts=3   # Max date parsing attempts
   )

   metas = infer_meta_dict(df, config=config)

See Also
========

* :doc:`meta` - Meta variable types
* :doc:`display` - Using inferred metas in displays
