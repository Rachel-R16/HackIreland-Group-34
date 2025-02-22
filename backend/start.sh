#!/bin/bash

echo "Stopping any existing Flask processes..."
pkill -f "flask run" || true

echo "Setting up environment variables..."
export FLASK_APP=api
export FLASK_ENV=development
export FLASK_DEBUG=1
export PYTHONUNBUFFERED=1  # This ensures Python output isn't buffered

echo "Starting Flask server on port 5001..."
flask run --port 5001 --debug --host=0.0.0.0
