# AFL Player Over/Under Search API

A FastAPI backend service that provides over/under statistics for AFL players across their game history.

## Tech Stack

- **Python 3.12+**
- **FastAPI** - Modern, fast web framework
- **Uvicorn** - ASGI server
- **SQLite** - Database
- **Pytest** - Testing framework

## Setup

1. **Install dependencies:**
```bash
python3 -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt
```

2. **Environment (optional):**
   - Database path defaults to `BetChecker-PlayerDatabase/afl_stats.db`
   - Override with `DB_PATH` environment variable if needed

## Running the Server

**Development mode (with auto-reload):**
```bash
source .venv/bin/activate
uvicorn app.main:app --reload --host 0.0.0.0 --port 8000
```

**Production mode:**
```bash
source .venv/bin/activate
uvicorn app.main:app --host 0.0.0.0 --port 8000
```

The API will be available at:
- **API**: http://localhost:8000
- **Interactive Docs**: http://localhost:8000/docs
- **Alternative Docs**: http://localhost:8000/redoc

## API Endpoint

### GET `/search/over-under`

Returns over/under counts for a player's stat across their game history.

**Query Parameters:**
- `player_id` (int, optional) - Player ID
- `player_name` (str, optional) - Player name (exactly one of player_id or player_name required)
- `stat` (str, required) - One of: `disposals`, `goals`
- `threshold` (float, required) - The threshold value
- `strict_over` (bool, optional) - If true: over uses `>`, under uses `<=`. Default: false (over uses `>=`, under uses `<`)

**Response:**
```json
{
  "over": 150,
  "under": 50
}
```

**Example Request:**
```bash
curl "http://localhost:8000/search/over-under?player_name=Scott%20Pendlebury&stat=disposals&threshold=23.5"
```

**Example Response:**
```json
{
  "over": 2,
  "under": 0
}
```

**Error Responses:**
- `400` - Invalid parameters (e.g., missing player identifier, invalid stat)
- `404` - Player not found
- `500` - Database connection error

## Testing

Run tests:
```bash
source .venv/bin/activate
pytest tests/ -v
```

Run specific test:
```bash
pytest tests/test_search_api.py::test_over_under_returns_two_fields_only -v
```

## Database

- **Location**: `BetChecker-PlayerDatabase/afl_stats.db`
- **Primary View**: `vw_complete_game_stats`
- See `BetChecker-PlayerDatabase/README.md` for schema details

## Deployment (Railway)

1. **Create a project**
   - In Railway, select **New Project → Deploy from Repo** and connect the Git repository that contains this backend.
   - When prompted for a root directory, enter `BetChecker-BackEnd`.

2. **Configure the service**
   - **Build Command:** `pip install -r requirements.txt`
   - **Start Command:** `uvicorn app.main:app --host 0.0.0.0 --port $PORT`

3. **Environment variables**
   - Add `DB_PATH=BetChecker-BackEnd/BetChecker-PlayerDatabase/afl_stats.db`.
   - Add any future secrets (e.g., API keys) under the **Variables** tab.

4. **Deploy**
   - Trigger a manual deploy. Railway will install dependencies and launch Uvicorn bound to the provided `$PORT`.
   - Use the **Logs** panel to confirm the database file is found and the API starts without errors.

5. **Verify**
   - Visit `https://<railway-domain>/docs` to confirm the FastAPI docs load.
   - Test the main endpoint: `https://<railway-domain>/search/over-under?player_name=Scott%20Pendlebury&stat=disposals&threshold=23.5`.

### Notes on SQLite in Railway

- The SQLite file bundled in `BetChecker-PlayerDatabase/afl_stats.db` ships with each deploy. For read-only analytics this is sufficient.
- If you need to persist writes or updates, provision a [Railway Volume](https://docs.railway.app/guides/volumes) and point `DB_PATH` to the mounted path (commonly `/mnt/data/afl_stats.db`).
- Keep the `CORSMiddleware` origins in `app/main.py` up-to-date with your deployed frontend domain once it is live.

