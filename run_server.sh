#!/bin/bash
# Run VideoConnoisseur application

echo "=== Video Processing Application ==="
echo ""

# Check if Python is available
if ! command -v python &> /dev/null; then
    echo "Error: Python is not installed"
    exit 1
fi

# Initialize database and start the application
echo "Initializing database..."
python -c "
import os
import sys
sys.path.insert(0, '.')
from app import init_db
init_db()
print('Database initialized successfully')
"

echo ""
echo "Starting Flask server on http://0.0.0.0:5000"
echo "Press Ctrl+C to stop the server"
echo ""

# Start the application
python -c "
import os
import sys
sys.path.insert(0, '.')
from app import app
app.run(host='0.0.0.0', port=5000, debug=True, threaded=True)
"