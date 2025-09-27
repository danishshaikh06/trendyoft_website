@echo off
echo 🚀 Generating Static Site from Database...
echo.

cd /d "%~dp0"
python generate_static_site.py

echo.
echo ✅ Static site generation completed!
echo.
echo 📖 How to use:
echo    1. Server running: Open index.html (gets live data from server)
echo    2. Server stopped: Open index.html (automatically uses cached data)
echo    3. Completely offline: Open index_offline.html
echo.
echo 💡 Run this script again after adding new products to update cached data!
echo.

pause
