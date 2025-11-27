#!/bin/bash

echo "========================================"
echo "  Nagarik Connect - Starting Server"
echo "========================================"
echo ""

# Check if Python is installed
if ! command -v python3 &> /dev/null; then
    echo "ERROR: Python 3 is not installed"
    echo "Please install Python 3.8 or higher"
    exit 1
fi

echo "Python found!"
echo ""

# Check if virtual environment exists
if [ ! -d "venv" ]; then
    echo "Creating virtual environment..."
    python3 -m venv venv
    echo "Virtual environment created!"
    echo ""
fi

# Activate virtual environment
echo "Activating virtual environment..."
source venv/bin/activate

# Install/Update dependencies
echo "Installing dependencies..."
pip install -r requirements.txt --quiet

echo ""
echo "========================================"
echo "  Starting Flask Application"
echo "========================================"
echo ""
echo "Server will start at: http://localhost:5000"
echo ""
echo "Admin Login: http://localhost:5000/admin"
echo "  Username: admin"
echo "  Password: admin@123"
echo ""
echo "Press Ctrl+C to stop the server"
echo "========================================"
echo ""

# Run the Flask app
python app.py
