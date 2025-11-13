import os
import sys

# Add project root to sys.path for imports like `from app.main import app`
PROJECT_ROOT = os.path.abspath(os.path.join(os.path.dirname(__file__), os.pardir))
if PROJECT_ROOT not in sys.path:
    sys.path.insert(0, PROJECT_ROOT)

# Ensure tests use the workspace-local database path by default
DB_PATH = os.path.join(PROJECT_ROOT, "BetChecker-PlayerDatabase", "afl_stats.db")
os.environ.setdefault("DB_PATH", DB_PATH)
