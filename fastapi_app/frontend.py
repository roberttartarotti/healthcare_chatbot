"""Launcher for the React dev server, exposed as a console script.

``healthcare-assistant-frontend`` runs the Vite dev server in ``frontend/``,
installing npm dependencies first if they are missing. It's just a convenience
wrapper around ``npm run dev`` so the whole project starts from Python commands.
"""

import shutil
import subprocess
import sys
from pathlib import Path

_FRONTEND_DIR = Path(__file__).resolve().parent.parent / "frontend"


def main() -> None:
    """Install deps if needed, then start the Vite dev server."""
    if shutil.which("npm") is None:
        sys.exit("npm was not found. Install Node.js (which includes npm) and retry.")

    if not (_FRONTEND_DIR / "node_modules").exists():
        print("Installing frontend dependencies (first run)…")
        subprocess.run(["npm", "install"], cwd=_FRONTEND_DIR, check=True)

    print("Starting the frontend at http://localhost:5173 …")
    subprocess.run(["npm", "run", "dev"], cwd=_FRONTEND_DIR, check=True)


if __name__ == "__main__":
    main()
