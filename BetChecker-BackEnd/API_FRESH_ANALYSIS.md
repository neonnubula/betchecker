# AFL API - Fresh Analysis: What Data Is Actually Available

## Approach: Start from API Reality, Not Our Schema

Instead of trying to force the API into our schema, let's understand what the API actually provides and design our approach accordingly.

---

## ✅ Confirmed Working Endpoints

### 1. `/teams` - Teams List
**What it provides:**
```json
{
  "id": 1,
  "name": "Adelaide Crows",
  "logo": "https://media.api-sports.io/afl/teams/1.png"
}
```

**Available Data:**
- ✅ Team ID (stable identifier)
- ✅ Team name
- ✅ Logo URL

**What we can do:**
- Map teams directly to our `teams` table
- Use API team_id as our team_id (or map it)

---

### 2. `/players` - Players List
**Required Parameters:** 
- `id` OR (`team` + `season`) OR (`name` + `season`)

**What it provides:**
```json
{
  "id": 156,
  "name": "Scott Pendlebury"
}
```

**Available Data:**
- ✅ Player ID (stable identifier - this is KEY!)
- ✅ Player name (full name)
- ❌ No date of birth
- ❌ No first/last name breakdown
- ❌ No other details

**Key Insight:** 
- **API provides stable player IDs** - we can use these as primary identifiers
- Player ID persists across seasons (same player = same ID)
- This solves our duplicate name problem differently than planned

**What we can do:**
- Use `api_player_id` as the primary way to identify players
- Store API ID in database
- Match players by API ID, not name + DOB

---

### 3. `/games` - Games/Fixtures
**Required Parameters:**
- `season` + `league` (league = 1 for AFL)

**What it provides:**
```json
{
  "game": {
    "id": 2524
  },
  "league": {
    "id": 1,
    "season": 2023
  },
  "date": "2023-03-16T19:20:00+00:00",
  "time": "19:20",
  "timestamp": "1678994400",
  "timezone": "UTC",
  "round": "Regular Season",  // or "Finals"
  "week": 1,  // Round number for regular season
  "venue": "Melbourne Cricket Ground",
  "attendance": null,
  "status": {
    "long": "Finished",
    "short": "FT"
  },
  "teams": {
    "home": {
      "id": 12,
      "name": "Richmond Tigers",
      "logo": "https://media.api-sports.io/afl/teams/12.png"
    },
    "away": {
      "id": 3,
      "name": "Carlton Blues",
      "logo": "https://media.api-sports.io/afl/teams/3.png"
    }
  },
  "scores": {
    "home": {
      "score": 58,
      "goals": 8,
      "behinds": 10,
      "psgoals": 0,
      "psbehinds": 0
    },
    "away": {
      "score": 58,
      "goals": 8,
      "behinds": 10,
      "psgoals": 0,
      "psbehinds": 0
    }
  }
}
```

**Available Data:**
- ✅ Game ID (stable identifier)
- ✅ Date and time
- ✅ Venue (as string)
- ✅ Home and away teams (with IDs)
- ✅ Round information (`round` text + `week` number)
- ✅ Season year
- ✅ Team scores
- ⚠️ Round number needs parsing (`week` for regular season)
- ⚠️ Game type needs parsing (`round` field: "Regular Season" vs "Finals")

**What we can do:**
- Map games directly to our `games` table
- Parse round/week to get round_number
- Parse round text to get game_type
- Create/lookup venues from venue string

---

### 4. `/leagues` - League Information
**What it provides:**
```json
{
  "id": 1,
  "name": "AFL Premiership",
  "logo": "https://media.api-sports.io/afl/leagues/1.png",
  "season": 2011,
  "start": "2011-03-24",
  "end": "2011-10-01",
  "current": false
}
```

**Available Data:**
- League details
- Season ranges
- Current status

**What we can do:**
- Use to validate seasons
- Get season date ranges

---

### 5. `/seasons` - Available Seasons
**What it provides:**
```json
2011
```

**Available Data:**
- List of available season years

**What we can do:**
- Know which seasons are available
- Plan scraping by season

---

## ⚠️ Endpoints That Exist But Need Testing

### `/players/statistics` - Player Statistics
**Status:** Endpoint exists but hit rate limit during testing
**Parameters:** Likely `player` (ID) and `season`

**What we need to find out:**
- What statistics are included?
- Is it per-game stats or aggregated?
- Does it include which team the player was on?
- Does it include disposals and goals?

**This is CRITICAL** - we need this to populate `player_game_stats` table.

---

### `/standings` - League Standings
**Status:** Endpoint exists but limited on free plan
**Parameters:** `season` + `league`

**What it might provide:**
- Team standings/positions
- Points, wins, losses
- Not directly needed for our use case, but could be useful

---

## ❌ Endpoints That Don't Exist

- `/players/{id}` - Use `/players?id={id}` instead
- `/players/{id}/statistics` - Use `/players/statistics?player={id}` instead
- `/games/{id}` - Use `/games?id={id}` instead
- `/games/{id}/players` - Doesn't exist
- `/games/{id}/statistics` - Doesn't exist
- `/venues` - Doesn't exist (venue is just a string in games)
- `/rounds` - Doesn't exist
- `/fixtures` - Use `/games` instead

---

## Key Insights from Fresh Analysis

### 1. **API Uses Stable IDs**
- Players have stable IDs across seasons
- Games have stable IDs
- Teams have stable IDs
- **We should use these IDs as primary identifiers**

### 2. **No Date of Birth Available**
- API doesn't provide DOB
- **We can't use name + DOB strategy**
- **Solution: Use API player_id as primary identifier**

### 3. **Minimal Player Data**
- Only ID and name
- No first/last name breakdown
- No DOB, height, weight, etc.
- **We work with what we have: ID + name**

### 4. **Game Data Is Rich**
- Complete game information
- Teams, venue, date, scores
- **We can map this directly to our games table**

### 5. **Statistics Endpoint Unknown**
- `/players/statistics` exists but structure unknown
- **Need to test this once rate limit resets**
- **This is the missing piece for player stats**

---

## Revised Data Model Based on API Reality

### Players Table
```sql
CREATE TABLE players (
    player_id INTEGER PRIMARY KEY AUTOINCREMENT,
    api_player_id INTEGER UNIQUE NOT NULL,  -- ⭐ Use API ID as unique identifier
    player_name TEXT NOT NULL,
    -- No DOB available from API
    -- Can add DOB later if we supplement with web scraping
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);
```

**Key Change:** Use `api_player_id` as the unique identifier instead of name + DOB

### Games Table
```sql
CREATE TABLE games (
    game_id INTEGER PRIMARY KEY AUTOINCREMENT,
    api_game_id INTEGER UNIQUE NOT NULL,  -- ⭐ Use API game ID
    season_year INTEGER NOT NULL,
    round_number INTEGER,  -- Parse from 'week' field
    game_type TEXT NOT NULL,  -- Parse from 'round' field ("Regular Season" or "Finals")
    game_date DATE NOT NULL,  -- Parse from ISO date string
    game_time TIME,  -- Parse from time string
    venue_id INTEGER NOT NULL,  -- Lookup/create from venue string
    home_team_id INTEGER NOT NULL,  -- Use API team ID
    away_team_id INTEGER NOT NULL,  -- Use API team ID
    -- Can store scores if needed
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);
```

**Key Change:** Use `api_game_id` and `api_team_id` to match API data

### Player Game Stats Table
```sql
CREATE TABLE player_game_stats (
    stat_id INTEGER PRIMARY KEY AUTOINCREMENT,
    player_id INTEGER NOT NULL,  -- References our players table (via api_player_id lookup)
    game_id INTEGER NOT NULL,  -- References our games table (via api_game_id lookup)
    team_id INTEGER NOT NULL,  -- Which team player was on (from statistics response)
    opponent_team_id INTEGER NOT NULL,  -- Other team in the game
    venue_id INTEGER NOT NULL,  -- From game
    location TEXT NOT NULL,  -- 'Home' or 'Away' (determine from team_id vs home/away)
    game_time TEXT,  -- 'Day', 'Twilight', 'Night' (parse from game time)
    disposals INTEGER DEFAULT 0,  -- From statistics response
    goals INTEGER DEFAULT 0,  -- From statistics response
    -- Other stats from API if available
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    UNIQUE(player_id, game_id)
);
```

**Key Change:** Structure depends on what `/players/statistics` provides

---

## What We Need to Test Next

### Priority 1: Player Statistics Endpoint
```python
# Test this once rate limit resets:
GET /players/statistics?player=156&season=2023
```

**Questions to answer:**
1. What's the response structure?
2. Is it per-game or aggregated?
3. What statistics are included?
4. Does it include team information?
5. Does it include disposals and goals?

### Priority 2: Game Filtering
```python
# Test game filtering options:
GET /games?team=4&season=2023  # Games for specific team
GET /games?id=2524  # Single game by ID
```

**Questions to answer:**
1. Can we get games by team?
2. Can we get a single game by ID?
3. What other filters are available?

---

## Revised Scraping Strategy

### Phase 1: Master Data (One-Time)
1. **Teams**: Scrape `/teams` → Store all teams with API IDs
2. **Venues**: Extract unique venues from `/games` → Create venues table
3. **Players**: Scrape `/players?team={id}&season={year}` for each team/season → Store with API IDs

### Phase 2: Games (By Season)
1. **Games**: Scrape `/games?season={year}&league=1` → Store games with API IDs
2. **Parse**: Extract round numbers, game types, venues

### Phase 3: Player Statistics (TBD - Need to Test)
1. **Statistics**: Scrape `/players/statistics?player={id}&season={year}`
2. **Map**: Match to games and players using API IDs
3. **Store**: Insert into player_game_stats

### Phase 4: Team History
1. **Track**: When inserting stats, detect team changes
2. **Update**: player_team_history table

---

## Key Differences from Original Plan

### Original Plan (Name + DOB)
- Use player name + date of birth as unique identifier
- Handle duplicates by checking name + DOB

### Revised Plan (API IDs)
- Use API player_id as unique identifier
- Handle duplicates by checking API ID
- Supplement with name matching if API ID unavailable

### Benefits of Revised Approach
- ✅ Simpler (no DOB needed)
- ✅ More reliable (API IDs are stable)
- ✅ Faster (direct ID lookup vs name + DOB matching)
- ✅ Works with available API data

### Trade-offs
- ❌ Dependent on API maintaining stable IDs
- ❌ Can't distinguish players with same name if API has duplicate IDs (unlikely)
- ❌ No DOB for other analysis purposes

---

## Next Steps

1. **Wait for rate limit** to reset (10 requests/minute)
2. **Test `/players/statistics` endpoint** - This is critical!
3. **Document statistics response structure**
4. **Update database schema** to use API IDs
5. **Update Database Manager** to use API ID matching
6. **Build scraper** based on actual API structure
7. **Test with sample data**

---

## Summary: What We Know vs What We Need

### ✅ What We Know
- Teams endpoint: Works perfectly
- Players endpoint: Works, provides ID + name
- Games endpoint: Works, provides complete game data
- API uses stable IDs for everything

### ❓ What We Need to Test
- Player statistics endpoint structure
- How to get per-game player stats
- What statistics are available

### 🎯 What We Can Build Now
- Teams scraper
- Games scraper  
- Players scraper (basic - ID + name)
- Database schema updates for API IDs

### ⏳ What We Need to Wait For
- Statistics endpoint testing
- Per-game stats structure
- Complete player stats scraper

