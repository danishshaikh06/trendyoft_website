@echo off
echo Starting Trendyoft E-commerce Server...
echo.
echo Server will be available at: http://localhost:8000
echo Press Ctrl+C to stop the server
echo.

cd /d "%~dp0"
python main.py

pause
