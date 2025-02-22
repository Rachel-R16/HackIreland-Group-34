#!/bin/bash

echo "Setting up environment variables..."
export FLASK_APP=wsgi.py
export FLASK_ENV=development
export FLASK_DEBUG=1
export PYTHONUNBUFFERED=1

echo "Stopping any existing Flask processes..."
pkill -f "flask run" || true

echo "Installing requirements if needed..."
if [ -f "requirements.txt" ]; then
    pip install -r requirements.txt
fi

echo "Starting Flask server..."
python wsgi.py
