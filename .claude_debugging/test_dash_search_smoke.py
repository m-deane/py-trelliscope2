"""
Smoke test for global search functionality in Dash viewer.
"""

import sys
from pathlib import Path

# Add parent directory to path
sys.path.insert(0, str(Path(__file__).parent.parent))

import pandas as pd
from trelliscope.dash_viewer.components.search import (
    search_dataframe,
    get_searchable_columns,
    format_search_summary,
    create_search_panel
)

print("=" * 60)
print("GLOBAL SEARCH SMOKE TEST")
print("=" * 60)

# Test 1: search_dataframe function
print("\n1. Testing search_dataframe()...")
df = pd.DataFrame({
    'id': list(range(5)),
    'country': ['United States', 'United Kingdom', 'Germany', 'France', 'Japan'],
    'category': ['North America', 'Europe', 'Europe', 'Europe', 'Asia'],
    'value': [100, 80, 70, 65, 90]
})

# Search for "United"
result_df, match_count, total = search_dataframe(df, "United", ['country', 'category'])
print(f"✓ Search for 'United': Found {match_count} of {total}")
assert match_count == 2, f"Expected 2 matches, got {match_count}"  # US and UK

# Search for "Europe"
result_df, match_count, total = search_dataframe(df, "Europe", ['category'])
print(f"✓ Search for 'Europe': Found {match_count} of {total}")
assert match_count == 3, f"Expected 3 matches, got {match_count}"  # UK, Germany, France

# Empty search (should return all)
result_df, match_count, total = search_dataframe(df, "", ['country'])
print(f"✓ Empty search: Found {match_count} of {total}")
assert match_count == 5, f"Expected 5 matches, got {match_count}"

# Case insensitive search
result_df, match_count, total = search_dataframe(df, "UNITED", ['country'])
print(f"✓ Case insensitive search 'UNITED': Found {match_count} of {total}")
assert match_count == 2, f"Expected 2 matches, got {match_count}"

# No matches
result_df, match_count, total = search_dataframe(df, "xyz123", ['country', 'category'])
print(f"✓ No matches search 'xyz123': Found {match_count} of {total}")
assert match_count == 0, f"Expected 0 matches, got {match_count}"

# Test 2: get_searchable_columns function
print("\n2. Testing get_searchable_columns()...")
display_info = {
    'metas': [
        {'varname': 'country', 'type': 'factor'},
        {'varname': 'value', 'type': 'number'},
        {'varname': 'description', 'type': 'string'},
        {'varname': 'url', 'type': 'href'},
        {'varname': 'date', 'type': 'date'}
    ]
}

searchable = get_searchable_columns(display_info)
print(f"✓ Searchable columns: {searchable}")
# Should include: country, country_label (factor), description (string), url (href)
# Should NOT include: value (number), date (date)
assert 'country' in searchable
assert 'country_label' in searchable
assert 'description' in searchable
assert 'url' in searchable
assert 'value' not in searchable
assert 'date' not in searchable

# Test 3: format_search_summary function
print("\n3. Testing format_search_summary()...")
summary1 = format_search_summary(5, 10, "test")
print(f"✓ Summary (5/10, 'test'): {summary1}")
assert "5 of 10" in summary1

summary2 = format_search_summary(0, 10, "xyz")
print(f"✓ Summary (0/10, 'xyz'): {summary2}")
assert "No matches" in summary2

summary3 = format_search_summary(10, 10, "all")
print(f"✓ Summary (10/10, 'all'): {summary3}")
assert "All 10" in summary3

summary4 = format_search_summary(10, 10, "")
print(f"✓ Summary (no search): {summary4}")
assert "No active search" in summary4

# Test 4: create_search_panel UI
print("\n4. Testing create_search_panel()...")
search_panel = create_search_panel()
print(f"✓ Search panel created: {type(search_panel)}")
assert search_panel is not None

# Test 5: Integration test with factor labels
print("\n5. Testing with factor label columns...")
df_with_labels = pd.DataFrame({
    'country': [0, 1, 2],  # 0-based indices
    'country_label': ['USA', 'UK', 'Germany'],
    'value': [100, 80, 70]
})

# Search in label column
result_df, match_count, total = search_dataframe(df_with_labels, "UK", ['country_label'])
print(f"✓ Search in factor labels 'UK': Found {match_count} of {total}")
assert match_count == 1

# Search partial match
result_df, match_count, total = search_dataframe(df_with_labels, "U", ['country_label'])
print(f"✓ Partial search 'U': Found {match_count} of {total}")
assert match_count == 2  # USA and UK

print("\n" + "=" * 60)
print("ALL SEARCH SMOKE TESTS PASSED ✓")
print("=" * 60)
print("\nSearch functionality ready for integration!")
print("\nNext steps:")
print("  1. Test in browser with real display")
print("  2. Verify search works with filters")
print("  3. Test performance with large datasets")
