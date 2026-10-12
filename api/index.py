import os
import sys

# Compute project directories
CURRENT_DIR = os.path.dirname(os.path.abspath(__file__))
PROJECT_ROOT = os.path.abspath(os.path.join(CURRENT_DIR, ".."))

# Ensure Python can resolve modules from both root and api directories
for p in (PROJECT_ROOT, CURRENT_DIR):
    if p not in sys.path:
        sys.path.insert(0, p)

# Import the FastAPI application instance for Vercel Serverless
try:
    from app import app
except (ImportError, ModuleNotFoundError):
    from directory_finder.app import app
