"""
ASGI config for trendyoft project.
This module contains the ASGI application used by ASGI servers.
"""

from main import app

# Export the FastAPI app for ASGI servers
application = app

# This allows both uvicorn and gunicorn to find the app
if __name__ == "__main__":
    import uvicorn
    import os
    host = os.getenv("HOST", "0.0.0.0")
    port = int(os.getenv("PORT", 8000))
    uvicorn.run(app, host=host, port=port)
