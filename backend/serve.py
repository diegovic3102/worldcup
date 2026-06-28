"""Production entry point: serves the Flask app with Waitress.

Used by the Windows service (NSSM) so the backend survives reboots and
restarts. nginx proxies /api/ to this host:port, so it binds to localhost
only. Override with HOST / PORT environment variables if needed.
"""
import os

from waitress import serve

from app import app

if __name__ == "__main__":
    host = os.getenv("HOST", "0.0.0.0")
    port = int(os.getenv("PORT", "5001"))
    print(f"Serving sucesores-worldcup backend on http://{host}:{port}")
    serve(app, host=host, port=port)
