import os
import sqlite3
from typing import Optional
from fastapi import FastAPI, HTTPException, Query
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel

# Calculate database path relative to this file's location
# __file__ is app/main.py, so we go up one level to BetChecker-BackEnd, then into BetChecker-PlayerDatabase
_current_file = os.path.abspath(__file__)  # /path/to/BetChecker-BackEnd/app/main.py
_app_dir = os.path.dirname(_current_file)  # /path/to/BetChecker-BackEnd/app
_backend_dir = os.path.dirname(_app_dir)  # /path/to/BetChecker-BackEnd
DEFAULT_DB_PATH = os.path.join(_backend_dir, "BetChecker-PlayerDatabase", "afl_stats.db")

# Allow override via environment variable
DB_PATH = os.getenv("DB_PATH", DEFAULT_DB_PATH)

# Ensure the path is absolute
DB_PATH = os.path.abspath(DB_PATH)

app = FastAPI(title="AFL Player Over/Under Search API")

@app.get("/")
def root():
    """Root endpoint - redirects to API docs"""
    return {
        "message": "AFL Player Over/Under Search API",
        "docs": "/docs",
        "endpoint": "/search/over-under"
    }

@app.on_event("startup")
async def startup_event():
    """Log database path on startup for debugging"""
    import logging
    logger = logging.getLogger("uvicorn")
    logger.info(f"Database path configured: {DB_PATH}")
    logger.info(f"Database exists: {os.path.exists(DB_PATH)}")
    if not os.path.exists(DB_PATH):
        logger.error(f"WARNING: Database file not found at {DB_PATH}")
        logger.error(f"Current working directory: {os.getcwd()}")
        logger.error(f"__file__ location: {__file__}")
        logger.error(f"Backend directory: {_backend_dir}")

# Enable CORS for frontend access
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # In production, replace with specific frontend URL
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


class OverUnderResponse(BaseModel):
    over: int
    under: int


def get_connection() -> sqlite3.Connection:
    try:
        # Debug: Log the actual path being used
        if not os.path.exists(DB_PATH):
            raise HTTPException(
                status_code=500, 
                detail=f"Database file not found at: {DB_PATH}. Please check DB_PATH environment variable or ensure the database exists."
            )
        conn = sqlite3.connect(DB_PATH)
        conn.row_factory = sqlite3.Row
        return conn
    except sqlite3.Error as e:
        raise HTTPException(status_code=500, detail=f"Database connection error: {e}")


VALID_STATS = {"disposals", "goals"}


@app.get("/search/over-under", response_model=OverUnderResponse)
def search_over_under(
    player_id: Optional[int] = Query(None),
    player_name: Optional[str] = Query(None),
    stat: str = Query(...),
    threshold: float = Query(...),
    strict_over: bool = Query(False),
):
    # Validate identifier parameters
    if (player_id is None and not player_name) or (player_id is not None and player_name):
        raise HTTPException(status_code=400, detail="Provide exactly one of player_id or player_name")

    # Validate stat
    if stat not in VALID_STATS:
        raise HTTPException(status_code=400, detail="Invalid stat. Must be one of disposals|goals")

    with get_connection() as conn:
        # Resolve player_id from player_name if needed
        if player_id is None:
            cur = conn.execute(
                "SELECT player_id FROM vw_complete_game_stats WHERE player_name = ? LIMIT 1",
                (player_name,),
            )
            row = cur.fetchone()
            if not row:
                raise HTTPException(status_code=404, detail="Player not found")
            player_id = int(row["player_id"])  # type: ignore

        # Build SQL dynamically for stat comparator
        over_op = ">" if strict_over else ">="
        under_op = "<=" if strict_over else "<"
        # Inline the stat column name (validated)
        stat_col = stat

        sql = f"""
            WITH base AS (
                SELECT player_id, game_date, {stat_col} AS stat_value
                FROM vw_complete_game_stats
                WHERE player_id = :player_id
            )
            SELECT
                SUM(CASE WHEN stat_value {over_op} :threshold THEN 1 ELSE 0 END) AS over,
                SUM(CASE WHEN stat_value {under_op} :threshold THEN 1 ELSE 0 END) AS under
            FROM base
        """
        cur = conn.execute(sql, {"player_id": player_id, "threshold": threshold})
        row = cur.fetchone()
        over = int(row["over"]) if row and row["over"] is not None else 0
        under = int(row["under"]) if row and row["under"] is not None else 0
        return OverUnderResponse(over=over, under=under)


