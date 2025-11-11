# Factor Indexing Solution - 1-Based vs 0-Based

## Critical Discovery

**Date**: 2025-11-07
**Issue**: Categorical (factor) variables showing "[missing]" in viewer
**Root Cause**: Indexing mismatch between Python (0-based) and R/viewer (1-based)

## The Problem

The trelliscopejs-lib JavaScript viewer expects **R-style 1-based factor indexing**, not JavaScript/Python-style 0-based indexing.

### Example:
```python
# Python DataFrame with categorical
df = pd.DataFrame({
    'country': ['Algeria', 'Denmark', 'Germany']
})
# After factorization: [0, 1, 2]  (0-based indices)
```

In R, factors are 1-indexed:
```r
# R factor
country <- factor(c("Algeria", "Denmark", "Germany"))
# Levels: 1, 2, 3  (1-based indices)
```

The viewer JavaScript code does:
```javascript
const label = levels[factor - 1];  // Expects 1-based, subtracts 1
```

## Why It Failed

### Initial State (Broken):
- Python data: `country: 0` (0-based)
- Viewer calculates: `levels[0 - 1]` → `levels[-1]` → `undefined` → "[missing]"

### String Workaround Attempt (Also Broken):
- Converted to: `country: "0"` (string)
- Viewer calculates: `levels["0"]` → `undefined` (array needs numeric index)

### Correct Solution (Working):
- Convert to: `country: 1` (1-based)
- Viewer calculates: `levels[1 - 1]` → `levels[0]` → "Algeria" ✓

## The Fix

### Code Changes

Modified `trelliscope/serialization.py` in three functions:

1. **`_serialize_cog_data()` lines 263-278**
2. **`write_metadata_json()` lines 346-356**
3. **`write_metadata_js()` lines 430-440**

Added conversion logic that handles BOTH numeric indices AND string values:
```python
# CRITICAL: Convert factor indices from 0-based to 1-based (R-style)
# The trelliscopejs viewer expects R-style 1-based factor indexing
# where levels[1-1] = levels[0] = first level
meta = display._meta_vars.get(varname)
if meta and meta.type == "factor":
    if isinstance(value, (int, float)):
        # Numeric categorical code (0, 1, 2...)
        value = int(value) + 1  # Convert 0-based to 1-based
    elif isinstance(value, str) and hasattr(meta, 'levels') and meta.levels:
        # String value - look up index in levels and convert to 1-based
        try:
            idx = meta.levels.index(value)
            value = idx + 1  # Convert to 1-based index
        except (ValueError, AttributeError):
            # Keep string value if not in levels
            pass
```

### Enhancement (2025-11-07)

**Extended to handle string factor values**: The serialization now accepts either:
- **Categorical indices** (0, 1, 2...) from `pd.Categorical` → converts to (1, 2, 3...)
- **String values** ("Algeria", "Denmark"...) → looks up in levels → converts to (1, 2, 3...)

This makes the system more flexible - you don't need to convert strings to categoricals first.

### Data Format

**Before Fix (0-based - WRONG)**:
```json
{
  "cogData": [
    {
      "country": 0,  // ❌ Python-style 0-based
      "panelKey": "0"
    }
  ],
  "metas": [
    {
      "varname": "country",
      "type": "factor",
      "levels": ["Algeria", "Denmark", "Germany"]
    }
  ]
}
```

**After Fix (1-based - CORRECT)**:
```json
{
  "cogData": [
    {
      "country": 1,  // ✅ R-style 1-based
      "panelKey": "0"
    }
  ],
  "metas": [
    {
      "varname": "country",
      "type": "factor",
      "levels": ["Algeria", "Denmark", "Germany"]
    }
  ]
}
```

### Viewer Mapping

With 1-based indexing:
- Python index 0 → JSON value 1 → Viewer: `levels[1-1]` → `levels[0]` → "Algeria"
- Python index 1 → JSON value 2 → Viewer: `levels[2-1]` → `levels[1]` → "Denmark"
- Python index 2 → JSON value 3 → Viewer: `levels[3-1]` → `levels[2]` → "Germany"

## Testing

### Verification Script
```bash
cd examples/output/refinery_plotly/displays/refinery_plotly
python3 -c "
import json
with open('displayInfo.json') as f:
    info = json.load(f)
    country_val = info['cogData'][0]['country']
    print(f'Country value: {country_val} (type: {type(country_val).__name__})')
    print(f'Expected: 1 (not 0)')
    assert country_val == 1, 'Should be 1-based!'
    print('✅ Correct 1-based indexing')
"
```

### Browser Test
1. Start server: `python3 -m http.server 8875`
2. Open: http://localhost:8875/
3. Check country filter shows "Algeria" (not "[missing]")

## Impact

This affects **all factor/categorical variables** in trelliscope displays:
- ✅ Categorical filters now work correctly
- ✅ Factor labels display properly
- ✅ Sorting by factors works
- ✅ Compatible with R-generated displays

## Related Files

- `trelliscope/serialization.py` - JSON serialization (FIXED)
- `trelliscope/meta.py` - Factor meta variable definition (no changes needed)
- `trelliscope/inference.py` - Type inference (no changes needed)

## Lessons Learned

1. **Check viewer expectations** - The viewer was built for R, uses R conventions
2. **Test with index 0** - Zero is a special case that exposes falsy bugs
3. **Don't guess at fixes** - String conversion seemed logical but broke array access
4. **Follow the data flow** - Trace from Python → JSON → JavaScript → Display

## Future Considerations

### Option 1: Keep Python 0-based internally
- ✅ Natural for Python developers
- ✅ Matches pandas categorical encoding
- ✅ Conversion happens only at serialization boundary
- **Current implementation**

### Option 2: Use 1-based throughout
- ❌ Unnatural for Python
- ❌ Would require converting pandas categoricals
- ❌ More error-prone
- **Not recommended**

### Recommendation
Keep current approach - Python uses 0-based internally, convert to 1-based only when serializing to JSON for viewer compatibility.

## References

- Original bug report: Session Nov 7, 2025
- Test display: `examples/output/refinery_plotly/`
- Viewer library: trelliscopejs-lib v0.7.16
- R trelliscope: Uses 1-based factor indexing
