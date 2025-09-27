#!/bin/bash

# Startup script for Render deployment
echo "Starting Trendyoft FastAPI application..."

# Set default port if not provided
export PORT=${PORT:-8000}

# Start the application with uvicorn
exec uvicorn main:app --host 0.0.0.0 --port $PORT --workers 1
