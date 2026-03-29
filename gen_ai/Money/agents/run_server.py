"""
run_server.py — Start the AI Money Mentor FastAPI backend.

Usage:
    python run_server.py              # default: localhost:8000
    python run_server.py --port 8080
    python run_server.py --reload     # auto-reload on code changes (dev mode)
"""

import argparse
import sys
from pathlib import Path

# Ensure src/ is on the path
sys.path.insert(0, str(Path(__file__).resolve().parent / "src"))

import uvicorn

if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="AI Money Mentor API Server")
    parser.add_argument("--host",   default="0.0.0.0",  help="Bind host (default: 0.0.0.0)")
    parser.add_argument("--port",   default=8000, type=int, help="Bind port (default: 8000)")
    parser.add_argument("--reload", action="store_true",   help="Enable auto-reload (dev mode)")
    args = parser.parse_args()

    print(f"\n🚀  AI Money Mentor API")
    print(f"    http://{args.host}:{args.port}")
    print(f"    Docs → http://localhost:{args.port}/docs\n")

    uvicorn.run(
        "agents.backend.app:app",
        host=args.host,
        port=args.port,
        reload=args.reload,
    )
