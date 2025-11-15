#!/usr/bin/env python3
"""
Trelliscope Panel Server

Simple Flask server to serve panel images for trelliscopejs viewer.
The viewer v0.7.16 requires panels to be served via REST API.

Usage:
    python panel_server.py

Then open: http://localhost:5000

This serves:
- Static files from output/ directory
- Panel images via REST API at /api/panels/<display_name>/<panel_id>
"""

from flask import Flask, send_file, send_from_directory, jsonify
from flask_cors import CORS
from pathlib import Path
import logging

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

app = Flask(__name__)
CORS(app)  # Enable CORS for development

# Base directory for trelliscope output
OUTPUT_DIR = Path(__file__).parent / "output"
DISPLAYS_DIR = OUTPUT_DIR / "displays"

@app.route('/')
def index():
    """Serve the main index.html"""
    index_path = OUTPUT_DIR / "index.html"
    if index_path.exists():
        return send_file(index_path)
    return "Trelliscope output not found. Run a display generation script first.", 404

@app.route('/<path:path>')
def serve_static(path):
    """Serve static files (CSS, JS, JSON configs)"""
    try:
        return send_from_directory(OUTPUT_DIR, path)
    except Exception as e:
        logger.error(f"Error serving {path}: {e}")
        return str(e), 404

@app.route('/api/panels/<display_name>/<panel_id>')
def serve_panel(display_name, panel_id):
    """
    Serve a panel image for a specific display.

    Args:
        display_name: Name of the display (e.g., "minimal_manual")
        panel_id: Panel identifier (e.g., "0", "1", "2")

    Returns:
        PNG image file
    """
    # Construct panel path
    panel_path = DISPLAYS_DIR / display_name / "panels" / f"{panel_id}.png"

    logger.info(f"Panel request: {display_name}/{panel_id}")
    logger.debug(f"Looking for: {panel_path}")

    if panel_path.exists():
        logger.info(f"✓ Serving panel: {panel_path}")
        return send_file(panel_path, mimetype='image/png')
    else:
        logger.error(f"✗ Panel not found: {panel_path}")
        return f"Panel not found: {display_name}/{panel_id}", 404

@app.route('/api/panels/<display_name>/<panel_id>.<ext>')
def serve_panel_with_extension(display_name, panel_id, ext):
    """
    Serve a panel with explicit extension (for compatibility).

    Supports: .png, .jpg, .html
    """
    panel_path = DISPLAYS_DIR / display_name / "panels" / f"{panel_id}.{ext}"

    logger.info(f"Panel request: {display_name}/{panel_id}.{ext}")

    if panel_path.exists():
        # Determine MIME type
        mime_types = {
            'png': 'image/png',
            'jpg': 'image/jpeg',
            'jpeg': 'image/jpeg',
            'html': 'text/html'
        }
        mime_type = mime_types.get(ext.lower(), 'application/octet-stream')

        logger.info(f"✓ Serving panel: {panel_path} as {mime_type}")
        return send_file(panel_path, mimetype=mime_type)
    else:
        logger.error(f"✗ Panel not found: {panel_path}")
        return f"Panel not found: {display_name}/{panel_id}.{ext}", 404

@app.route('/api/displays')
def list_displays():
    """List all available displays (for debugging)"""
    if not DISPLAYS_DIR.exists():
        return jsonify({"displays": [], "error": "No displays directory found"})

    displays = []
    for display_dir in DISPLAYS_DIR.iterdir():
        if display_dir.is_dir():
            info_file = display_dir / "displayInfo.json"
            if info_file.exists():
                displays.append({
                    "name": display_dir.name,
                    "path": str(display_dir.relative_to(OUTPUT_DIR))
                })

    return jsonify({"displays": displays, "count": len(displays)})

@app.route('/api/health')
def health_check():
    """Health check endpoint"""
    return jsonify({
        "status": "ok",
        "output_dir": str(OUTPUT_DIR),
        "displays_dir_exists": DISPLAYS_DIR.exists()
    })

if __name__ == '__main__':
    print("=" * 60)
    print("Trelliscope Panel Server")
    print("=" * 60)
    print(f"Output directory: {OUTPUT_DIR.absolute()}")
    print(f"Displays directory: {DISPLAYS_DIR.absolute()}")
    print()
    print("Endpoints:")
    print("  http://localhost:5000/              - Main viewer")
    print("  http://localhost:5000/api/health    - Health check")
    print("  http://localhost:5000/api/displays  - List displays")
    print("  http://localhost:5000/api/panels/<display>/<id> - Serve panel")
    print()
    print("Starting server...")
    print("=" * 60)

    app.run(
        host='0.0.0.0',
        port=5001,
        debug=True,
        use_reloader=False  # Disable reloader for background running
    )
