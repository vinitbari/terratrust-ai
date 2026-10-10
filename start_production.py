"""TerraTrust AI — Production / Hackathon Demo Runner.

Launches the unified full-stack application (Frontend UI + FastAPI + Scikit-Learn ML Model)
on a single port (8000).
"""

import os
import sys
import subprocess
from pathlib import Path

ROOT_DIR = Path(__file__).resolve().parent
API_DIR = ROOT_DIR / "apps" / "api"
WEB_DIR = ROOT_DIR / "apps" / "web"
WEB_DIST = WEB_DIR / "dist"


def ensure_frontend_built():
    """Verify that frontend assets are compiled, or build them if missing."""
    if not (WEB_DIST / "index.html").exists():
        print("[TerraTrust AI] Frontend build not found. Compiling React + Vite...")
        subprocess.run(["npm", "run", "build", "--workspace=web"], cwd=ROOT_DIR, check=True)
        print("[TerraTrust AI] Frontend successfully built to apps/web/dist")
    else:
        print("[TerraTrust AI] Frontend production assets ready.")


def run_server():
    """Start Uvicorn production server."""
    port = int(os.environ.get("PORT", 8000))
    host = os.environ.get("HOST", "0.0.0.0")

    # Set default database to SQLite if not provided
    if "DATABASE_URL" not in os.environ:
        os.environ["DATABASE_URL"] = f"sqlite:///{API_DIR / 'fin03.db'}"

    # Ensure API directory is in Python path
    sys.path.insert(0, str(API_DIR))

    import uvicorn
    from app.main import app

    print(f"\n========================================================")
    print(f">> TerraTrust AI is running live on: http://localhost:{port}")
    print(f">> Swagger API Documentation:       http://localhost:{port}/docs")
    print(f">> AI/ML Yield Inference Endpoint:  http://localhost:{port}/predict-yield")
    print(f">> Demo Credentials:                 officer@fin03.local / password123")
    print(f"========================================================\n")

    uvicorn.run(app, host=host, port=port)


if __name__ == "__main__":
    ensure_frontend_built()
    run_server()
