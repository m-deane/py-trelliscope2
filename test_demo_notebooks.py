#!/usr/bin/env python3
"""
Test all demo notebooks for execution errors.

Runs all cells except the final app.run() cell which would block execution.
"""

import json
import sys
from pathlib import Path

def test_notebook(notebook_path):
    """Execute all cells in a notebook except viewer launch cells."""
    print(f"\n{'='*70}")
    print(f"Testing: {notebook_path.name}")
    print('='*70)

    with open(notebook_path, 'r', encoding='utf-8') as f:
        nb = json.load(f)

    cells = nb['cells']
    code_cells = [c for c in cells if c['cell_type'] == 'code']

    print(f"Found {len(code_cells)} code cells")

    # Create execution namespace
    exec_globals = {}

    for i, cell in enumerate(code_cells, 1):
        source = ''.join(cell['source'])

        # Skip empty cells
        code_stripped = source.strip()
        if not code_stripped:
            print(f"  Cell {i}: SKIPPED (empty)")
            continue

        # Skip cells with only comments
        lines = [line.strip() for line in code_stripped.split('\n') if line.strip()]
        if all(line.startswith('#') for line in lines):
            print(f"  Cell {i}: SKIPPED (all comments)")
            continue

        # Skip viewer launch cells (app.run blocks execution)
        if 'app.run(' in source or '.run(' in source:
            print(f"  Cell {i}: SKIPPED (viewer launch)")
            continue

        # Execute cell
        try:
            exec(source, exec_globals)
            print(f"  Cell {i}: OK")
        except Exception as e:
            print(f"  Cell {i}: ERROR - {type(e).__name__}: {e}")
            return False

    return True


def main():
    """Test all demo notebooks."""
    demo_dir = Path('examples/demo_notebooks')

    if not demo_dir.exists():
        print(f"Error: Directory {demo_dir} not found")
        sys.exit(1)

    # Find all notebooks
    notebooks = sorted(demo_dir.glob('*.ipynb'))

    if not notebooks:
        print(f"No notebooks found in {demo_dir}")
        sys.exit(1)

    print(f"Found {len(notebooks)} notebooks to test:")
    for nb in notebooks:
        print(f"  - {nb.name}")

    # Test each notebook
    results = {}
    for nb_path in notebooks:
        try:
            passed = test_notebook(nb_path)
            results[nb_path.name] = passed
        except Exception as e:
            print(f"\n❌ FATAL ERROR in {nb_path.name}: {e}")
            results[nb_path.name] = False

    # Summary
    print("\n" + "="*70)
    print("SUMMARY")
    print("="*70)

    for nb_name, passed in results.items():
        status = "✓ PASS" if passed else "✗ FAIL"
        print(f"{status}: {nb_name}")

    passed_count = sum(1 for p in results.values() if p)
    total_count = len(results)

    print(f"\nTotal: {passed_count}/{total_count} passed")

    if passed_count == total_count:
        print("\n🎉 All notebooks passed!")
        sys.exit(0)
    else:
        print(f"\n❌ {total_count - passed_count} notebook(s) failed")
        sys.exit(1)


if __name__ == '__main__':
    main()
