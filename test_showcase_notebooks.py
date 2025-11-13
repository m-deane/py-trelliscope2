#!/usr/bin/env python3
"""Test script to validate Phase 4 showcase notebooks."""

import json
import sys
import tempfile
import traceback
from pathlib import Path

def extract_code_cells(notebook_path):
    """Extract Python code cells from Jupyter notebook."""
    with open(notebook_path, 'r') as f:
        nb = json.load(f)

    code_cells = []
    for cell in nb.get('cells', []):
        if cell.get('cell_type') == 'code':
            source = cell.get('source', [])
            if isinstance(source, list):
                code = ''.join(source)
            else:
                code = source
            code_cells.append(code)

    return code_cells

def test_notebook(notebook_path, skip_viewer_launch=True):
    """Test a single notebook by executing its code cells."""
    print(f"\n{'='*70}")
    print(f"Testing: {notebook_path.name}")
    print('='*70)

    try:
        code_cells = extract_code_cells(notebook_path)
        print(f"Found {len(code_cells)} code cells")

        # Create execution namespace
        namespace = {}

        for i, code in enumerate(code_cells, 1):
            # Skip the last cell that launches the viewer
            if skip_viewer_launch and i == len(code_cells):
                if 'app.run' in code or 'run_server' in code:
                    print(f"  Cell {i}: SKIPPED (viewer launch)")
                    continue

            # Skip cells with only comments or empty
            code_stripped = code.strip()
            if not code_stripped:
                print(f"  Cell {i}: SKIPPED (empty)")
                continue

            # Skip if ALL non-empty lines are comments
            lines = [line.strip() for line in code_stripped.split('\n') if line.strip()]
            if all(line.startswith('#') for line in lines):
                print(f"  Cell {i}: SKIPPED (all comments)")
                continue

            try:
                exec(code, namespace)
                print(f"  Cell {i}: OK")
            except Exception as e:
                print(f"  Cell {i}: ERROR - {type(e).__name__}: {str(e)}")
                if '--verbose' in sys.argv:
                    traceback.print_exc()
                return False

        print(f"\n✓ {notebook_path.name} - ALL CELLS PASSED")
        return True

    except Exception as e:
        print(f"\n✗ {notebook_path.name} - FAILED: {type(e).__name__}: {str(e)}")
        if '--verbose' in sys.argv:
            traceback.print_exc()
        return False

def main():
    """Test all Phase 4 showcase notebooks."""
    showcase_dir = Path('examples/phase4_showcase')

    if not showcase_dir.exists():
        print(f"Error: {showcase_dir} not found")
        return 1

    notebooks = sorted(showcase_dir.glob('*.ipynb'))

    if not notebooks:
        print(f"No notebooks found in {showcase_dir}")
        return 1

    print(f"\nFound {len(notebooks)} notebooks to test:")
    for nb in notebooks:
        print(f"  - {nb.name}")

    results = {}
    for notebook in notebooks:
        results[notebook.name] = test_notebook(notebook)

    # Summary
    print(f"\n{'='*70}")
    print("SUMMARY")
    print('='*70)

    passed = sum(results.values())
    total = len(results)

    for name, result in results.items():
        status = "✓ PASS" if result else "✗ FAIL"
        print(f"{status}: {name}")

    print(f"\nTotal: {passed}/{total} passed")

    if passed == total:
        print("\n🎉 All notebooks passed!")
        return 0
    else:
        print(f"\n⚠️  {total - passed} notebook(s) failed")
        return 1

if __name__ == '__main__':
    sys.exit(main())
