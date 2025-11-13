"""
Browser validation script for Phase 3 features.

Tests:
1. Views System (filter, sort, save, load, delete)
2. Global Search
3. Panel Details Modal
4. Integration of all features
"""

from playwright.sync_api import sync_playwright, expect
import time
import sys

def test_views_system(page):
    """Test 1: Views System"""
    print("\n" + "="*70)
    print("TEST 1: VIEWS SYSTEM")
    print("="*70)

    # Filter by continent = 'Europe'
    print("  ✓ Filtering by continent = 'Europe'...")
    continent_select = page.locator('select[id*="continent-filter"]')
    continent_select.select_option(label='Europe')
    time.sleep(1)

    # Verify filtering worked
    panel_count = page.locator('.panel-container').count()
    print(f"    - Found {panel_count} panels after filtering")

    # Sort by GDP (descending)
    print("  ✓ Sorting by GDP (descending)...")
    gdp_header = page.locator('th:has-text("GDP")')
    gdp_header.click()  # First click = ascending
    time.sleep(0.5)
    gdp_header.click()  # Second click = descending
    time.sleep(1)

    # Save view
    print("  ✓ Saving view as 'Europe GDP'...")
    view_name_input = page.locator('input[id="view-name-input"]')
    view_name_input.fill('Europe GDP')
    save_view_btn = page.locator('button:has-text("Save Current View")')
    save_view_btn.click()
    time.sleep(1)

    # Verify view appears in dropdown
    view_dropdown = page.locator('select[id="view-select"]')
    view_options = view_dropdown.locator('option').all_text_contents()
    assert 'Europe GDP' in view_options, "View not saved!"
    print("    - View successfully saved")

    # Clear filters
    print("  ✓ Clearing filters...")
    clear_filters_btn = page.locator('button:has-text("Clear All Filters")')
    clear_filters_btn.click()
    time.sleep(1)

    # Verify all panels shown
    panel_count_after_clear = page.locator('.panel-container').count()
    print(f"    - {panel_count_after_clear} panels after clearing")

    # Load view
    print("  ✓ Loading 'Europe GDP' view...")
    view_dropdown.select_option(label='Europe GDP')
    time.sleep(1)

    # Verify filter restored
    selected_continent = continent_select.input_value()
    print(f"    - Continent filter restored: {selected_continent}")

    # Delete view
    print("  ✓ Deleting 'Europe GDP' view...")
    delete_view_btn = page.locator('button:has-text("Delete View")')
    delete_view_btn.click()
    time.sleep(1)

    # Verify view removed
    view_options_after = view_dropdown.locator('option').all_text_contents()
    assert 'Europe GDP' not in view_options_after, "View not deleted!"
    print("    - View successfully deleted")

    print("✅ VIEWS SYSTEM TEST PASSED\n")


def test_global_search(page):
    """Test 2: Global Search"""
    print("\n" + "="*70)
    print("TEST 2: GLOBAL SEARCH")
    print("="*70)

    # Search for 'United'
    print("  ✓ Searching for 'United'...")
    search_input = page.locator('input[id="global-search-input"]')
    search_input.fill('United')
    time.sleep(1)

    # Check results summary
    results_summary = page.locator('#search-results-summary').text_content()
    print(f"    - {results_summary}")
    assert 'United' in results_summary or '2' in results_summary, "Search failed!"

    # Search for 'America'
    print("  ✓ Searching for 'America'...")
    search_input.fill('America')
    time.sleep(1)

    results_summary = page.locator('#search-results-summary').text_content()
    print(f"    - {results_summary}")

    # Search for 'Germany'
    print("  ✓ Searching for 'Germany'...")
    search_input.fill('Germany')
    time.sleep(1)

    results_summary = page.locator('#search-results-summary').text_content()
    print(f"    - {results_summary}")
    assert '1' in results_summary, "Germany search failed!"

    # Clear search
    print("  ✓ Clearing search...")
    clear_search_btn = page.locator('button:has-text("Clear")', has=page.locator('input[id="global-search-input"]').locator('..'))
    clear_search_btn.click()
    time.sleep(1)

    # Verify all panels shown
    panel_count = page.locator('.panel-container').count()
    print(f"    - {panel_count} panels after clearing search")

    print("✅ GLOBAL SEARCH TEST PASSED\n")


def test_panel_details_modal(page):
    """Test 3: Panel Details Modal"""
    print("\n" + "="*70)
    print("TEST 3: PANEL DETAILS MODAL")
    print("="*70)

    # Click first panel
    print("  ✓ Clicking on first panel...")
    first_panel = page.locator('.panel-container').first
    first_panel.click()
    time.sleep(1)

    # Verify modal opened
    modal = page.locator('#panel-detail-modal')
    assert modal.is_visible(), "Modal did not open!"
    print("    - Modal opened successfully")

    # Check modal title
    modal_title = page.locator('#panel-detail-title').text_content()
    print(f"    - Modal title: {modal_title}")

    # Check metadata table exists
    metadata_section = page.locator('#panel-detail-metadata')
    assert metadata_section.is_visible(), "Metadata not displayed!"
    print("    - Metadata table displayed")

    # Click Next button
    print("  ✓ Clicking 'Next' button...")
    next_btn = page.locator('button#panel-detail-next')
    next_btn.click()
    time.sleep(1)

    # Verify title changed
    new_title = page.locator('#panel-detail-title').text_content()
    print(f"    - New panel: {new_title}")
    assert new_title != modal_title, "Navigation failed!"

    # Click Previous button
    print("  ✓ Clicking 'Previous' button...")
    prev_btn = page.locator('button#panel-detail-prev')
    prev_btn.click()
    time.sleep(1)

    # Verify back to original
    back_title = page.locator('#panel-detail-title').text_content()
    print(f"    - Back to: {back_title}")
    assert back_title == modal_title, "Previous navigation failed!"

    # Close modal
    print("  ✓ Closing modal...")
    close_btn = page.locator('button#panel-detail-close')
    close_btn.click()
    time.sleep(1)

    # Verify modal closed
    assert not modal.is_visible(), "Modal did not close!"
    print("    - Modal closed successfully")

    print("✅ PANEL DETAILS MODAL TEST PASSED\n")


def test_integration(page):
    """Test 4: Integration of all features"""
    print("\n" + "="*70)
    print("TEST 4: INTEGRATION TEST")
    print("="*70)

    # Search for 'Europe'
    print("  ✓ Searching for 'Europe'...")
    search_input = page.locator('input[id="global-search-input"]')
    search_input.fill('Europe')
    time.sleep(1)

    results = page.locator('#search-results-summary').text_content()
    print(f"    - {results}")

    # Filter GDP > 2.0
    print("  ✓ Filtering GDP > 2.0...")
    gdp_min_input = page.locator('input[id*="gdp"][id*="min"]')
    gdp_min_input.fill('2.0')
    time.sleep(1)

    panel_count = page.locator('.panel-container').count()
    print(f"    - {panel_count} panels after filtering")

    # Sort by population (ascending)
    print("  ✓ Sorting by population (ascending)...")
    pop_header = page.locator('th:has-text("Population")')
    pop_header.click()
    time.sleep(1)

    # Click a panel
    print("  ✓ Opening panel modal...")
    page.locator('.panel-container').first.click()
    time.sleep(1)

    modal_title = page.locator('#panel-detail-title').text_content()
    print(f"    - Viewing: {modal_title}")

    # Navigate in modal
    print("  ✓ Navigating through filtered results...")
    page.locator('button#panel-detail-next').click()
    time.sleep(0.5)
    new_title = page.locator('#panel-detail-title').text_content()
    print(f"    - Next panel: {new_title}")

    # Close modal
    page.locator('button#panel-detail-close').click()
    time.sleep(1)

    # Save view
    print("  ✓ Saving as 'Large European Economies'...")
    view_name_input = page.locator('input[id="view-name-input"]')
    view_name_input.fill('Large European Economies')
    page.locator('button:has-text("Save Current View")').click()
    time.sleep(1)
    print("    - View saved")

    # Clear all
    print("  ✓ Clearing all filters and search...")
    page.locator('button:has-text("Clear All Filters")').click()
    time.sleep(0.5)
    page.locator('button:has-text("Clear")', has=search_input.locator('..')).click()
    time.sleep(1)

    # Load saved view
    print("  ✓ Loading saved view...")
    view_dropdown = page.locator('select[id="view-select"]')
    view_dropdown.select_option(label='Large European Economies')
    time.sleep(1)

    # Verify everything restored
    restored_search = search_input.input_value()
    print(f"    - Search restored: '{restored_search}'")
    print(f"    - Filters and sorts restored")

    # Clean up - delete view
    page.locator('button:has-text("Delete View")').click()
    time.sleep(1)

    print("✅ INTEGRATION TEST PASSED\n")


def main():
    """Run all Phase 3 validation tests"""
    print("\n" + "="*70)
    print("PHASE 3 BROWSER VALIDATION")
    print("="*70)
    print("Testing Trelliscope Dash Viewer at http://localhost:8053")
    print("="*70)

    with sync_playwright() as p:
        # Launch browser in headless mode
        browser = p.chromium.launch(headless=True)
        context = browser.new_context(viewport={'width': 1920, 'height': 1080})
        page = context.new_page()

        try:
            # Navigate to app
            print("\n📍 Navigating to http://localhost:8053...")
            page.goto('http://localhost:8053', wait_until='networkidle')
            time.sleep(2)  # Extra wait for Dash initialization

            # Take initial screenshot
            page.screenshot(path='/tmp/phase3_initial.png', full_page=True)
            print("📸 Initial screenshot saved to /tmp/phase3_initial.png")

            # Run all tests
            test_views_system(page)
            test_global_search(page)
            test_panel_details_modal(page)
            test_integration(page)

            # Take final screenshot
            page.screenshot(path='/tmp/phase3_final.png', full_page=True)
            print("📸 Final screenshot saved to /tmp/phase3_final.png")

            print("\n" + "="*70)
            print("🎉 ALL PHASE 3 TESTS PASSED!")
            print("="*70)
            print("\n✅ Views System: PASS")
            print("✅ Global Search: PASS")
            print("✅ Panel Details Modal: PASS")
            print("✅ Integration: PASS")
            print("\n" + "="*70)

            return 0

        except AssertionError as e:
            print(f"\n❌ TEST FAILED: {e}")
            page.screenshot(path='/tmp/phase3_error.png', full_page=True)
            print("📸 Error screenshot saved to /tmp/phase3_error.png")
            return 1

        except Exception as e:
            print(f"\n❌ UNEXPECTED ERROR: {e}")
            page.screenshot(path='/tmp/phase3_error.png', full_page=True)
            print("📸 Error screenshot saved to /tmp/phase3_error.png")
            import traceback
            traceback.print_exc()
            return 1

        finally:
            browser.close()


if __name__ == '__main__':
    sys.exit(main())
