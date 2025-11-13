### AFL Player Over/Under Search API (Python + SQLite) — Implementation Spec

### Context
- **Database file path**: `/Users/d/BetChecker-PlayerDatabase/afl_stats.db`
- **Schema reference**: `/Users/d/BetChecker-PlayerDatabase/schema.sql`
- **Primary view**: `vw_complete_game_stats`
  - Columns include: `player_id`, `player_name`, `game_id`, `game_date`, `season_year`, `round_number`, `game_type`, `team_id`, `opponent_team_id`, `opponent_name`, `venue_id`, `venue_name`, `location`, `game_time`, `disposals`, `goals`

### Goal
- **Build a Python API** that returns over/under counts for a single stat for a player across their game history.
- **Support filters** for Home/Away, Venue, Opposition, Round Type, Time of Day.
- **Support partial history** via date ranges and last N games.

### Tech Stack
- **Python**: 3.11+
- **Framework**: FastAPI
- **Server**: Uvicorn
- **Database Driver**: sqlite3 (standard library) or aiosqlite (optional)
- **Testing**: pytest, httpx

### Project Setup (new workspace)
- **Recommended structure**:
  - `app/main.py`
  - `tests/test_search_api.py`
  - `requirements.txt`
  - `.env` (optional)
- **requirements.txt** should include:
  - `fastapi`
  - `uvicorn[standard]`
  - `pydantic`
  - `pytest`
  - `httpx`
  - `python-dotenv` (optional if using `.env`)
- **Environment config**:
  - `DB_PATH=/Users/d/BetChecker-PlayerDatabase/afl_stats.db`
  - Default to this absolute path if `DB_PATH` is not set.

### API Contract
- **Method**: GET
- **Path**: `/search/over-under`
- **Query parameters**:
  - `player_id` (int) or `player_name` (str). Exactly one required.
  - `stat` (str). One of `disposals`, `goals`. Required.
  - `threshold` (int). Required.
  - `strict_over` (bool). Optional. Default false. If true: over uses `>`, under uses `<=`.
  - `location` (str). Optional. One of `Home`, `Away`.
  - `venue_id` (int) or `venue_name` (str). Optional.
  - `opponent_team_id` (int) or `opponent_name` (str). Optional.
  - `game_type` (str). Optional. One of `Pre-Season`, `Regular Season`, `Finals`.
  - `time_of_day` (str). Optional. One of `Day`, `Twilight`, `Night`.
  - `start_date` (YYYY-MM-DD). Optional.
  - `end_date` (YYYY-MM-DD). Optional.
  - `last_n_games` (int). Optional. Positive integer; applied after filters by most recent `game_date`.
- **Response body**:
  - JSON with exactly two fields:
    - `over` (int)
    - `under` (int)

### Behavior Rules
- Resolve `player_name` to `player_id` if `player_id` not provided.
- Build a single SQL query against `vw_complete_game_stats` with optional WHERE clauses for all provided filters.
- **Partial history**:
  - Constrain by `game_date` when `start_date` and/or `end_date` are provided.
  - If `last_n_games` is provided, order the filtered rows by `date(game_date) DESC` and limit to N before aggregation.
- **Over/under logic**:
  - Default: over is `stat >= threshold`, under is `stat < threshold`.
  - If `strict_over=true`: over is `stat > threshold`, under is `stat <= threshold`.

### SQL Construction Notes
- SQLite cannot bind identifiers (column names). Validate `stat` and inline the column name (`disposals` or `goals`) in the SQL string.
- Keep all values parameterized.
- Use a CTE to apply `last_n_games` after filters.

### Validation & Errors
- 400 if both or neither of `player_id` and `player_name` are provided.
- 400 if `stat` is not one of `disposals|goals`.
- 400 if invalid enum for `location|game_type|time_of_day`.
- 400 if `start_date > end_date`.
- 400 if `last_n_games <= 0`.
- 404 if player not found.
- **Error format**: `{ "detail": "<message>" }`

### Performance Guidance
- Query `vw_complete_game_stats` to avoid manual joins.
- Rely on existing indexes on player, opponent, venue, location, game_time, game_date.

### Runbook (local)
- **Start server**:
  - `uvicorn app.main:app --reload`
- **Database path**:
  - Use `DB_PATH=/Users/d/BetChecker-PlayerDatabase/afl_stats.db`
- **Sample curl**:
```bash
curl -G "http://127.0.0.1:8000/search/over-under" \
  --data-urlencode "player_name=Scott Pendlebury" \
  --data-urlencode "stat=disposals" \
  --data-urlencode "threshold=25"
```

### Test Plan (mapped to your steps)
- **Step 1: Single stat, full history**
  - Verify response contains only `over` and `under` for a known player and threshold.
- **Step 2: Single stat, full history with filters**
  - Verify `location=Home`.
  - Verify `location=Away`.
  - Verify `venue_name=<venue>`.
  - Verify `opponent_name=<team>`.
  - Verify `game_type=Regular Season` (and other types).
  - Verify `time_of_day=Night` (and other buckets).
- **Step 3: Partial history**
  - Verify `start_date` and/or `end_date` reduce the sample space.
  - Verify `last_n_games` limits to most recent games after filters.
- **Step 4: Partial history with filters**
  - Combine filters with date range or `last_n_games` and verify counts align with manual SQL.

### Minimal SQL Shape (guidance only)
```sql
WITH base AS (
  SELECT player_id, game_date, /* stat column inlined */ AS stat_value
  FROM vw_complete_game_stats
  WHERE player_id = :player_id
    AND (:location IS NULL OR location = :location)
    AND (:venue_id IS NULL OR venue_id = :venue_id)
    AND (:venue_name IS NULL OR venue_name = :venue_name)
    AND (:opponent_team_id IS NULL OR opponent_team_id = :opponent_team_id)
    AND (:opponent_name IS NULL OR opponent_name = :opponent_name)
    AND (:game_type IS NULL OR game_type = :game_type)
    AND (:time_of_day IS NULL OR game_time = :time_of_day)
    AND (:start_date IS NULL OR date(game_date) >= date(:start_date))
    AND (:end_date IS NULL OR date(game_date) <= date(:end_date))
),
limited AS (
  SELECT *
  FROM base
  ORDER BY date(game_date) DESC
  LIMIT CASE WHEN :last_n_games IS NULL THEN -1 ELSE :last_n_games END
)
SELECT
  SUM(CASE WHEN stat_value /* > or >= */ :threshold THEN 1 ELSE 0 END) AS over,
  SUM(CASE WHEN stat_value /* <= or < */ :threshold THEN 1 ELSE 0 END) AS under
FROM limited;
```

### Deliverables
- Implemented FastAPI endpoint `/search/over-under` with the contract above.
- Configuration to read `DB_PATH` env var with default to `/Users/d/BetChecker-PlayerDatabase/afl_stats.db`.
- Pytest suite covering Steps 1–4.
- README with run and test instructions.



