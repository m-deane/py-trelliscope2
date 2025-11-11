Factor Indexing
===============

.. module:: trelliscope.serialization
   :synopsis: Factor indexing conversion for viewer compatibility

Overview
--------

The trelliscope package automatically converts factor (categorical) indices from Python's 0-based indexing to R-style 1-based indexing expected by the trelliscopejs viewer.

This critical conversion ensures that categorical filters work correctly in the viewer, preventing the "[missing]" bug that occurs when index 0 is incorrectly treated as invalid.

Why 1-Based Indexing?
---------------------

The trelliscopejs-lib viewer was built for R, which uses 1-based factor indexing. The viewer JavaScript code performs:

.. code-block:: javascript

   const label = levels[factor - 1];

This means:

* **Python**: ``factor = 0`` → **Viewer**: ``levels[0 - 1]`` → ``levels[-1]`` → ``undefined`` → **"[missing]"** ❌
* **Python**: ``factor = 1`` → **Viewer**: ``levels[1 - 1]`` → ``levels[0]`` → **"Algeria"** ✅

Automatic Conversion
-------------------

The conversion happens automatically during JSON serialization in three functions:

1. :func:`_serialize_cog_data` - Converts data for displayInfo.json
2. :func:`write_metadata_json` - Converts data for metaData.json
3. :func:`write_metadata_js` - Converts data for metaData.js

Example Usage
------------

**Numeric Categorical Indices**

.. code-block:: python

   import pandas as pd
   from trelliscope import Display
   from trelliscope.meta import FactorMeta

   # Create DataFrame with categorical column (0-based indices)
   df = pd.DataFrame({
       'country': pd.Categorical(['Algeria', 'Denmark', 'Germany']),
       'value': [100, 200, 300]
   })

   display = Display(df, name="example")
   display.add_meta_variable(
       FactorMeta(varname="country", label="Country",
                 levels=['Algeria', 'Denmark', 'Germany'])
   )

   # Internally: country has indices [0, 1, 2]
   # After serialization: cogData has [1, 2, 3]
   display.write()

**String Factor Values**

.. code-block:: python

   # Create DataFrame with string column (not categorical)
   df = pd.DataFrame({
       'country': ['Algeria', 'Denmark', 'Germany'],  # Strings!
       'value': [100, 200, 300]
   })

   display = Display(df, name="example")
   display.add_meta_variable(
       FactorMeta(varname="country", label="Country",
                 levels=['Algeria', 'Denmark', 'Germany'])
   )

   # Strings automatically converted to 1-based indices:
   # 'Algeria' → 1, 'Denmark' → 2, 'Germany' → 3
   display.write()

Implementation Details
---------------------

The conversion logic handles multiple cases:

**Numeric Indices (0-based → 1-based)**

.. code-block:: python

   if isinstance(value, (int, float)) and not (isinstance(value, float) and value != value):
       value = int(value) + 1  # 0 → 1, 1 → 2, etc.

**String Values (lookup → 1-based)**

.. code-block:: python

   elif isinstance(value, str) and hasattr(meta, 'levels') and meta.levels:
       try:
           idx = meta.levels.index(value)  # Find index in levels
           value = idx + 1  # Convert to 1-based
       except (ValueError, AttributeError):
           pass  # Keep string if not in levels

**Special Cases**

* **NaN/None**: Preserved as-is (not converted)
* **Strings not in levels**: Preserved as-is
* **Non-factor columns**: Unchanged

Data Flow Example
----------------

From Python DataFrame to Viewer:

.. code-block:: text

   DataFrame (Python)
   ┌─────────┬────────┐
   │ country │ value  │
   ├─────────┼────────┤
   │ 0       │ 100    │  ← Categorical index
   │ 1       │ 200    │
   │ 2       │ 300    │
   └─────────┴────────┘

         ↓ Serialization (automatic conversion)

   displayInfo.json / metaData.json
   {
     "cogData": [
       {"country": 1, "value": 100},  ← 1-based index
       {"country": 2, "value": 200},
       {"country": 3, "value": 300}
     ],
     "metas": [{
       "varname": "country",
       "type": "factor",
       "levels": ["Algeria", "Denmark", "Germany"]  ← 0-indexed array
     }]
   }

         ↓ Viewer JavaScript

   Viewer Calculation: levels[factor - 1]
   ┌────────┬───────────────┬─────────────┬──────────┐
   │ factor │ Calculation   │ Array Index │ Result   │
   ├────────┼───────────────┼─────────────┼──────────┤
   │ 1      │ levels[1 - 1] │ levels[0]   │ Algeria  │ ✓
   │ 2      │ levels[2 - 1] │ levels[1]   │ Denmark  │ ✓
   │ 3      │ levels[3 - 1] │ levels[2]   │ Germany  │ ✓
   └────────┴───────────────┴─────────────┴──────────┘

Testing
-------

The factor indexing conversion is thoroughly tested in :mod:`tests.unit.test_factor_indexing`:

* 17 comprehensive tests covering all conversion scenarios
* Edge cases: NaN, None, empty DataFrames, unicode
* End-to-end validation with viewer compatibility
* 100% test pass rate

See Also
--------

* :doc:`/user_guide/categorical_data` - Guide to working with categorical data
* :doc:`/api/serialization` - JSON serialization API reference
* :doc:`/api/meta` - Meta variable types
* `Factor Indexing Solution <../.claude_plans/FACTOR_INDEXING_SOLUTION.md>`_ - Technical analysis

Troubleshooting
--------------

**Problem**: Categorical filter shows "[missing]" instead of category names

**Solution**: This was the original bug, now fixed. If you still see this:

1. Verify you're using the latest code (not cached)
2. Check that factor indices in JSON are integers (not strings)
3. Confirm indices are 1-based (first value should be 1, not 0)

**Verification**:

.. code-block:: python

   import json

   # Check generated JSON
   with open('displays/your_display/metaData.json') as f:
       data = json.load(f)

   # Should be int with value 1 (not 0, not "0")
   print(data[0]['your_factor_column'])  # Expected: 1
   print(type(data[0]['your_factor_column']))  # Expected: <class 'int'>

References
----------

* :doc:`/CLAUDE` - Project documentation
* GitHub: `py-trelliscope2 <https://github.com/your-repo/py-trelliscope2>`_
