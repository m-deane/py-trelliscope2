#!/usr/bin/env python
"""Clean up Safari debugging test files."""

from pathlib import Path
import shutil

output_dir = Path(__file__).parent / "output"

# Test files to archive
test_files = [
    "check_browser.html",
    "test_safari.html",
    "index_debug.html",
    "index_fixed.html",
    "index_react.html",
    "index_working.html",
    "index_importmap.html",
    "index_global.html",
    "trelliscope-lib.min.js",
    "trelliscope.css",
]

# Create archive directory
archive_dir = output_dir / "safari_debug_archive"
archive_dir.mkdir(exist_ok=True)

# Move test files to archive
moved_count = 0
for filename in test_files:
    file_path = output_dir / filename
    if file_path.exists():
        dest_path = archive_dir / filename
        shutil.move(str(file_path), str(dest_path))
        print(f"✓ Archived: {filename}")
        moved_count += 1

# Keep index_final.html as a reference
final_html = output_dir / "index_final.html"
if final_html.exists():
    dest_path = archive_dir / "index_final.html"
    shutil.copy(str(final_html), str(dest_path))
    final_html.unlink()
    print(f"✓ Archived (with copy): index_final.html")
    moved_count += 1

print(f"\n✓ Archived {moved_count} test files to {archive_dir}")
print(f"\nRemaining files in output/:")
for f in sorted(output_dir.iterdir()):
    if f.is_file():
        print(f"  - {f.name}")
