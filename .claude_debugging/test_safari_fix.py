#!/usr/bin/env python
"""Quick test to regenerate index.html with Safari-compatible viewer code."""

import sys
from pathlib import Path

# Add parent directory to path
sys.path.insert(0, str(Path(__file__).parent.parent))

from trelliscope.viewer import generate_viewer_html, write_index_html

# Generate new HTML with the Safari fix
output_dir = Path(__file__).parent / "output"
html = generate_viewer_html("basic_viewer_demo")

# Write to index.html
index_path = output_dir / "index.html"
write_index_html(index_path, html)

print(f"✓ Updated {index_path}")
print("\nGenerated HTML preview:")
print("=" * 80)
print(html[:800])
print("...")
print("=" * 80)
print("\nPlease test in Safari at http://localhost:6543/index.html")
