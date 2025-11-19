# ETL Plan: Extract, Transform, Load

## Overview

Complete plan for Extracting data from API-Sports.io, Transforming it to match our schema, and Loading it into our database.

---

## Schema Review & Required Changes

### ✅ Already Have (from migrations)
- `players.api_player_id` - Added via migration
- `games.api_game_id` - Added via migration

### ⚠️ Need to Add
- `teams.api_team_id` - For consistency (or use team_id directly since API IDs match)

### 🤔 Decision Needed: Additional Stats Fields

**API Provides**:
- disposals ✅ (we have)
- goals ✅ (we have)
- kicks
- handballs
- marks
- tackles
- clearances
- hitouts
- behinds
- free_kicks (for/against)
- goals.assists

**Current Schema**: Only stores `disposals` and `goals`

**Question**: Do we want to store additional stats?
- **Option A**: Keep minimal (disposals + goals only) - simpler, faster
- **Option B**: Add more stats (kicks, marks, tackles, etc.) - more comprehensive

**Recommendation**: Start with Option A, can add more later if needed.

---

## ETL PROCESS BREAKDOWN

---

## 1. EXTRACT (Getting Data from API)

### 1.1 Extract Teams
**Endpoint**: `GET /teams`  
**Frequency**: One-time  
**Requests**: 1

**Extract**:
```python
{
    "id": 1,
    "name": "Adelaide Crows",
    "logo": "https://..."
}
```

### 1.2 Extract Seasons
**Endpoint**: `GET /seasons`  
**Frequency**: One-time (for reference)  
**Requests**: 1

**Extract**:
```python
[2011, 2012, ..., 2025]
```

### 1.3 Extract Players
**Endpoint**: `GET /players?team={team_id}&season={year}`  
**Frequency**: Per team per season  
**Requests**: ~18 teams × 15 seasons = ~270

**Extract**:
```python
{
    "id": 156,
    "name": "Scott Pendlebury"
}
```

### 1.4 Extract Games
**Endpoint**: `GET /games?season={year}&league=1`  
**Frequency**: Per season  
**Requests**: 1 per season = 15

**Extract**:
```python
{
    "game": {"id": 2524},
    "league": {"id": 1, "season": 2023},
    "date": "2023-03-16T19:20:00+00:00",
    "time": "19:20",
    "round": "Regular Season",
    "week": 1,
    "venue": "Melbourne Cricket Ground",
    "teams": {
        "home": {"id": 12, "name": "Richmond Tigers"},
        "away": {"id": 3, "name": "Carlton Blues"}
    },
    "scores": {...}
}
```

### 1.5 Extract Game Player Statistics ⭐ CORE
**Endpoint**: `GET /games/statistics/players?id={game_id}`  
**Frequency**: Per game  
**Requests**: ~216 per season = ~3,240 total

**Extract**:
```python
{
    "game": {"id": 2524},
    "teams": [
        {
            "team": {"id": 3},
            "players": [
                {
                    "player": {"id": 156, "number": 10},
                    "disposals": 25,
                    "goals": {"total": 2, "assists": 1},
                    "kicks": 15,
                    "handballs": 10,
                    "marks": 8,
                    "tackles": 4,
                    ...
                }
            ]
        }
    ]
}
```

---

## 2. TRANSFORM (Mapping API Data to Our Schema)

### 2.1 Transform Teams

**API → Database**:
```python
# Extract
api_team = {"id": 1, "name": "Adelaide Crows", "logo": "..."}

# Transform
team_data = {
    "team_id": api_team["id"],  # Use API ID directly as our team_id
    "team_name": api_team["name"],
    "api_team_id": api_team["id"],  # Store for reference
    "is_active": True
}

# Or simpler: Just use API ID as team_id directly
```

**Transformation Logic**:
- Use API team ID as our `team_id` (they're stable)
- Store team name
- Set `is_active = True` (all teams from API are active)

### 2.2 Transform Players

**API → Database**:
```python
# Extract
api_player = {"id": 156, "name": "Scott Pendlebury"}

# Transform
player_data = {
    "api_player_id": api_player["id"],  # Primary identifier
    "player_name": api_player["name"],
    "first_name": None,  # Not available from API
    "last_name": None,   # Not available from API
    "date_of_birth": None,  # Not available from API
    "debut_year": None  # Not available from API
}
```

**Transformation Logic**:
- Store `api_player_id` as unique identifier
- Store player name
- Leave other fields NULL (can supplement later if needed)

### 2.3 Transform Venues

**API → Database**:
```python
# Extract (from games)
venue_name = "Melbourne Cricket Ground"

# Transform
venue_data = {
    "venue_name": venue_name
}
```

**Transformation Logic**:
- Extract unique venue names from games
- Create venue records (or lookup if exists)
- Simple name matching

### 2.4 Transform Games

**API → Database**:
```python
# Extract
api_game = {
    "game": {"id": 2524},
    "league": {"season": 2023},
    "date": "2023-03-16T19:20:00+00:00",
    "time": "19:20",
    "round": "Regular Season",
    "week": 1,
    "venue": "Melbourne Cricket Ground",
    "teams": {
        "home": {"id": 12},
        "away": {"id": 3}
    }
}

# Transform
game_data = {
    "api_game_id": api_game["game"]["id"],
    "season_year": api_game["league"]["season"],
    "round_number": api_game["week"],  # Parse from "week"
    "game_type": api_game["round"],  # "Regular Season" or "Finals"
    "game_date": parse_date(api_game["date"]),  # "2023-03-16"
    "game_time": api_game["time"],  # "19:20"
    "venue_id": get_or_create_venue(api_game["venue"]),  # Lookup/create
    "home_team_id": api_game["teams"]["home"]["id"],
    "away_team_id": api_game["teams"]["away"]["id"]
}
```

**Transformation Logic**:
- Parse ISO date string to DATE format
- Use `week` field as `round_number` (NULL for finals)
- Use `round` field as `game_type` ("Regular Season" or "Finals")
- Lookup/create venue by name
- Use API team IDs directly

**Date Parsing**:
```python
from datetime import datetime

def parse_api_date(iso_string):
    # "2023-03-16T19:20:00+00:00" -> "2023-03-16"
    dt = datetime.fromisoformat(iso_string.replace('Z', '+00:00'))
    return dt.date()
```

**Game Type Parsing**:
```python
def parse_game_type(round_text):
    if "Regular Season" in round_text:
        return "Regular Season"
    elif "Finals" in round_text:
        return "Finals"
    else:
        return "Regular Season"  # Default
```

### 2.5 Transform Player Game Statistics ⭐ CORE

**API → Database**:
```python
# Extract (from game statistics endpoint)
game_stats = {
    "game": {"id": 2524},
    "teams": [
        {
            "team": {"id": 3},
            "players": [
                {
                    "player": {"id": 156, "number": 10},
                    "disposals": 25,
                    "goals": {"total": 2, "assists": 1},
                    "kicks": 15,
                    "handballs": 10,
                    ...
                }
            ]
        },
        {
            "team": {"id": 12},
            "players": [...]
        }
    ]
}

# Transform (for each player)
for team_data in game_stats["teams"]:
    team_id = team_data["team"]["id"]
    
    # Find opponent team
    opponent_team_id = [
        t["team"]["id"] 
        for t in game_stats["teams"] 
        if t["team"]["id"] != team_id
    ][0]
    
    # Get game details for venue and home/away
    game = get_game_by_api_id(game_stats["game"]["id"])
    
    for player_stat in team_data["players"]:
        api_player_id = player_stat["player"]["id"]
        
        # Determine location (Home or Away)
        if team_id == game["home_team_id"]:
            location = "Home"
        else:
            location = "Away"
        
        # Determine game_time (Day/Twilight/Night)
        game_time = determine_game_time(game["game_time"])
        
        stat_data = {
            "player_id": get_player_id_by_api_id(api_player_id),
            "game_id": get_game_id_by_api_id(game_stats["game"]["id"]),
            "team_id": team_id,
            "opponent_team_id": opponent_team_id,
            "venue_id": game["venue_id"],
            "location": location,
            "game_time": game_time,
            "disposals": player_stat["disposals"],
            "goals": player_stat["goals"]["total"]
        }
```

**Transformation Logic**:
- Lookup player_id by api_player_id
- Lookup game_id by api_game_id
- Determine location (Home/Away) by comparing team_id to game's home/away
- Determine game_time from game time string
- Extract disposals and goals from API response

**Location Determination**:
```python
def determine_location(team_id, home_team_id, away_team_id):
    if team_id == home_team_id:
        return "Home"
    elif team_id == away_team_id:
        return "Away"
    else:
        raise ValueError(f"Team {team_id} not in game")
```

**Game Time Determination**:
```python
def determine_game_time(time_string):
    # "19:20" -> "Night"
    # "14:00" -> "Day"
    # "16:30" -> "Twilight"
    hour = int(time_string.split(":")[0])
    
    if hour < 15:
        return "Day"
    elif hour < 18:
        return "Twilight"
    else:
        return "Night"
```

---

## 3. LOAD (Inserting into Database)

### 3.1 Load Teams

**Process**:
```python
def load_teams(api_teams):
    for api_team in api_teams:
        # Check if exists
        existing = db.get_team_by_api_id(api_team["id"])
        
        if existing:
            continue  # Skip if already exists
        
        # Insert
        db.insert_team(
            team_id=api_team["id"],  # Use API ID directly
            team_name=api_team["name"],
            is_active=True
        )
```

**Database Operation**:
```sql
INSERT INTO teams (team_id, team_name, is_active)
VALUES (?, ?, 1)
ON CONFLICT(team_id) DO NOTHING;
```

### 3.2 Load Players

**Process**:
```python
def load_players(api_players, team_id, season):
    for api_player in api_players:
        # Use get_or_create pattern
        player_id = db.get_or_create_player(
            player_name=api_player["name"],
            api_player_id=api_player["id"]
        )
```

**Database Operation**:
```sql
-- Check if exists
SELECT player_id FROM players WHERE api_player_id = ?;

-- If not exists, insert
INSERT INTO players (api_player_id, player_name)
VALUES (?, ?);
```

### 3.3 Load Venues

**Process**:
```python
def load_venue(venue_name):
    # Get or create venue
    venue_id = db.get_or_create_venue(venue_name)
    return venue_id
```

**Database Operation**:
```sql
-- Check if exists
SELECT venue_id FROM venues WHERE venue_name = ?;

-- If not exists, insert
INSERT INTO venues (venue_name) VALUES (?);
```

### 3.4 Load Games

**Process**:
```python
def load_game(api_game):
    # Transform data
    game_data = transform_game(api_game)
    
    # Get or create venue
    venue_id = db.get_or_create_venue(game_data["venue_name"])
    game_data["venue_id"] = venue_id
    
    # Insert game
    game_id = db.get_or_create_game(**game_data)
    return game_id
```

**Database Operation**:
```sql
-- Check if exists
SELECT game_id FROM games WHERE api_game_id = ?;

-- If not exists, insert
INSERT INTO games (
    api_game_id, season_year, round_number, game_type,
    game_date, game_time, venue_id, home_team_id, away_team_id
) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?);
```

### 3.5 Load Player Game Statistics ⭐ CORE

**Process**:
```python
def load_game_statistics(api_game_stats):
    game_id = get_game_id_by_api_id(api_game_stats["game"]["id"])
    game = db.get_game(game_id)
    
    for team_data in api_game_stats["teams"]:
        team_id = team_data["team"]["id"]
        opponent_team_id = get_opponent_team_id(api_game_stats, team_id)
        
        for player_stat in team_data["players"]:
            api_player_id = player_stat["player"]["id"]
            player_id = db.get_player_id_by_api_id(api_player_id)
            
            # Check if stats already exist
            existing = db.get_stat(player_id, game_id)
            if existing:
                continue  # Skip if already loaded
            
            # Determine location
            location = "Home" if team_id == game["home_team_id"] else "Away"
            
            # Insert stats
            db.insert_player_stats(
                player_id=player_id,
                game_id=game_id,
                team_id=team_id,
                opponent_team_id=opponent_team_id,
                venue_id=game["venue_id"],
                location=location,
                game_time=determine_game_time(game["game_time"]),
                disposals=player_stat["disposals"],
                goals=player_stat["goals"]["total"]
            )
```

**Database Operation**:
```sql
-- Check if exists
SELECT stat_id FROM player_game_stats 
WHERE player_id = ? AND game_id = ?;

-- If not exists, insert
INSERT INTO player_game_stats (
    player_id, game_id, team_id, opponent_team_id,
    venue_id, location, game_time, disposals, goals
) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?);
```

---

## Complete ETL Flow

### Step-by-Step Process

```python
# 1. EXTRACT & LOAD: Teams (one-time)
teams = extract_teams()  # 1 request
load_teams(teams)

# 2. EXTRACT: Seasons (reference)
seasons = extract_seasons()  # 1 request

# 3. EXTRACT & LOAD: Players (per team/season)
for season in [2023, 2024, 2025]:  # Prioritize recent
    for team in teams:
        players = extract_players(team["id"], season)  # ~54 requests
        load_players(players, team["id"], season)

# 4. EXTRACT & LOAD: Games (per season)
for season in [2023, 2024, 2025]:
    games = extract_games(season)  # 3 requests
    load_games(games)  # Also extracts venues

# 5. EXTRACT & LOAD: Game Statistics ⭐ CORE
for season in [2023, 2024, 2025]:
    games = db.get_games_for_season(season)
    for game in games:
        stats = extract_game_statistics(game["api_game_id"])  # ~648 requests
        load_game_statistics(stats)
```

---

## Data Quality Checks

### Before Loading
- ✅ Validate API response structure
- ✅ Check for required fields
- ✅ Handle missing/null values

### During Loading
- ✅ Skip duplicates (check API IDs)
- ✅ Handle foreign key constraints
- ✅ Log errors for manual review

### After Loading
- ✅ Run validation tests
- ✅ Check for duplicate players
- ✅ Verify data completeness

---

## Error Handling

### API Errors
- **Rate Limit**: Wait and retry with exponential backoff
- **404 Not Found**: Log and skip (game stats may not be available)
- **Invalid Response**: Log error, continue with next item

### Database Errors
- **Foreign Key Violation**: Ensure parent records exist first
- **Unique Constraint**: Skip duplicate (already exists)
- **Data Type Mismatch**: Transform/validate before insert

---

## Summary

**Extract**: Get data from API endpoints  
**Transform**: Map API fields to our schema, parse dates, determine locations  
**Load**: Insert into database with duplicate checking

**Key Transformations**:
- API IDs → Our IDs (lookup/create)
- ISO dates → DATE format
- Round text → game_type
- Week number → round_number
- Team comparison → Home/Away location
- Time string → Day/Twilight/Night

**Schema Changes Needed**:
- ✅ Already have: `api_player_id`, `api_game_id`
- ⚠️ Consider: `api_team_id` (or use team_id directly)
- 🤔 Decision: Add more stats fields? (Start with disposals + goals)

