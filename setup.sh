#!/bin/bash
# Setup and installation script for Video Processing Application

set -e

echo "=== Video Processing Application Setup ==="

# Create necessary directories
mkdir -p uploads
mkdir -p processed
mkdir -p models
mkdir -p results
mkdir -p logs
mkdir -p temp

echo "✓ Created directories"

# Create virtual environment if it doesn't exist
if [ ! -d "venv" ]; then
    echo "Creating virtual environment..."
    python3 -m venv venv
    echo "✓ Virtual environment created"
fi

# Activate virtual environment
source venv/bin/activate

# Upgrade pip
echo "Upgrading pip..."
pip install --upgrade pip

# Install dependencies from requirements.txt if it exists
if [ -f "requirements.txt" ]; then
    echo "Installing dependencies from requirements.txt..."
    pip install -r requirements.txt
else
    echo "Installing dependencies from config.py..."
    pip install flask flask-cors flask-sqlalchemy flask-migrate celery redis requests pillow numpy scikit-learn tensorflow
fi

echo "✓ Dependencies installed"

# Initialize database (if using SQLite)
if [ -f "database.db" ]; then
    echo "✓ Database already exists"
else
    echo "Initializing database..."
    python -c "from app import db; db.create_all()" 2>/dev/null || echo "Note: Database initialization may require manual setup"
fi

# Set proper permissions
chmod -R 755 uploads processed models results logs temp

echo "✓ Permissions set"

echo ""
echo "=== Setup Complete ==="
echo ""
echo "To run the application:"
echo "  source venv/bin/activate"
echo "  python app.py"
echo ""
echo "To view the application:"
echo "  Open http://localhost:5000 in your browser"
echo ""

# Deactivate virtual environment
deactivate