import os
import sys

# Compute project directories
CURRENT_DIR = os.path.dirname(os.path.abspath(__file__))
PROJECT_ROOT = os.path.abspath(os.path.join(CURRENT_DIR, ".."))

# Ensure Python can resolve modules from both root and api directories
for p in (PROJECT_ROOT, CURRENT_DIR):
    if p not in sys.path:
        sys.path.insert(0, p)

# Import the FastAPI application instance
try:
    from app import app as raw_app
except (ImportError, ModuleNotFoundError):
    from directory_finder.app import app as raw_app

# Vercel ASGI path-restoring middleware
class VercelPathMiddleware:
    """Ensures FastAPI matches the true incoming URL path under Vercel serverless."""
    def __init__(self, inner_app):
        self.inner_app = inner_app

    async def __call__(self, scope, receive, send):
        if scope.get("type") == "http":
            headers = dict(scope.get("headers", []))
            # Inspect headers where Vercel passes the original requested path
            for header_key in (b"x-matched-path", b"x-forwarded-uri", b"x-original-uri"):
                raw_val = headers.get(header_key, b"").decode("utf-8").strip()
                if raw_val:
                    clean_path = raw_val.split("?")[0]
                    # If Vercel rewrote the internal path to index.py, restore the real path
                    if not clean_path.endswith(".py") and clean_path != "/api":
                        scope["path"] = clean_path
                        break
        await self.inner_app(scope, receive, send)

# Expose app for Vercel Serverless Function
app = VercelPathMiddleware(raw_app)
