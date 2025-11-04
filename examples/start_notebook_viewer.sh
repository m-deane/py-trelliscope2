#!/bin/bash
# Start HTTP server for notebook_demo display
# This script ensures the viewer runs from the correct directory

SCRIPT_DIR="$( cd "$( dirname "${BASH_SOURCE[0]}" )" && pwd )"
DISPLAY_DIR="$SCRIPT_DIR/output/notebook_demo"
PORT=8762

echo "Starting Trelliscope viewer for notebook_demo..."
echo "Directory: $DISPLAY_DIR"
echo "Port: $PORT"
echo ""

# Check if directory exists
if [ ! -d "$DISPLAY_DIR" ]; then
    echo "Error: Display directory not found at $DISPLAY_DIR"
    echo "Have you run the notebook (11_working_viewer_demo.ipynb) yet?"
    exit 1
fi

# Check if port is in use
if lsof -Pi :$PORT -sTCP:LISTEN -t >/dev/null 2>&1; then
    echo "Warning: Port $PORT is already in use"
    echo "The viewer may already be running, or another service is using this port"
    echo ""
    echo "To see what's using the port:"
    echo "  lsof -i :$PORT"
    echo ""
    echo "To kill the existing process:"
    echo "  lsof -i :$PORT -t | xargs kill -9"
    echo ""
    read -p "Try to start anyway? (y/N) " -n 1 -r
    echo
    if [[ ! $REPLY =~ ^[Yy]$ ]]; then
        exit 1
    fi
fi

# Change to display directory and start server
cd "$DISPLAY_DIR"
echo "Server starting..."
echo ""
echo "✅ Viewer URL: http://localhost:$PORT/"
echo ""
echo "Press Ctrl+C to stop the server"
echo "=================================================================================="
echo ""

# Start server (this will block)
python3 -m http.server $PORT
