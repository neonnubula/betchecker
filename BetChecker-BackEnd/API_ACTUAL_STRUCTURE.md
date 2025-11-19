# API-Sports.io AFL API - Actual Structure

## Test Results (Based on API Key Testing)

### ✅ Working Endpoints

#### 1. Teams Endpoint
**URL**: `GET /teams`

**Response Structure**:
```json
{
  "get": "teams",
  "parameters": [],
  "errors": [],
  "results": 18,
  "response": [
    {
      "id": 1,
      "name": "Adelaide Crows",
      "logo": "https://media.api-sports.io/afl/teams/1.png"
    }
  ]
}
```

**Status**: ✅ Works perfectly
**Data Available**: Team ID, name, logo
**Mapping**: Direct to our `teams` table

---

#### 2. Players Endpoint
**URL**: `GET /players`

**Required Parameters**: At least one of:
- `id` - Player ID
- `name` - Player name
- `team` - Team ID
- `season` - Season year
- `search` - Search term

**Response Structure**:
```json
{
  "get": "players",
  "parameters": {"team": "4", "season": "2023"},
  "errors": [],
  "results": 38,
  "response": [
    {
      "id": 156,
      "name": "Scott Pendlebury"
    }
  ]
}
```

**Status**: ⚠️ **LIMITED DATA**
**Data Available**: 
- ✅ Player ID (stable)
- ✅ Player name
- ❌ **NO DATE OF BIRTH** ⚠️
- ❌ No first/last name
- ❌ No debut year
- ❌ No other player details

**Critical Issue**: **Date of birth is NOT available in player endpoint**

**Impact**: 
- Cannot use name + DOB for duplicate handling
- Must use API player_id as primary identifier
- Need alternative strategy for duplicate names

---

#### 3. Games Endpoint
**URL**: `GET /games`

**Required Parameters**:
- `season` - Season year
- `league` - League ID (1 for AFL)

**Response Structure**:
```json
{
  "get": "games",
  "parameters": {"season": "2023", "league": "1"},
  "errors": [],
  "results": 216,
  "response": [
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
      "round": "Regular Season",
      "week": 1,
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
          "behinds": 10
        },
        "away": {
          "score": 58,
          "goals": 8,
          "behinds": 10
        }
      }
    }
  ]
}
```

**Status**: ✅ Works
**Data Available**:
- ✅ Game ID
- ✅ Date and time
- ✅ Venue name
- ✅ Home and away teams
- ✅ Round information
- ✅ Season year
- ❌ Round number (only "Regular Season" or week number)
- ❌ Game type (need to parse from round field)

**Mapping Notes**:
- `round` field contains "Regular Season" or "Finals" - need to parse
- `week` field is round number for regular season
- Venue is just a string, need to create/lookup in venues table

---

### ❌ Endpoints That Don't Exist

- `/players/search` - Use `/players?name=...` instead
- `/players/{id}/statistics` - Not available
- `/players/statistics` - Not available
- `/statistics` - Not available
- `/games/{id}/players` - Not available
- `/games/{id}/statistics` - Not available
- `/fixtures` - Use `/games` instead
- `/rounds` - Not available
- `/standings` - Exists but free plan limited to 2021-2023

---

## Critical Findings

### 🚨 Major Issue: No Date of Birth

**Problem**: The API does not provide player date of birth in the `/players` endpoint.

**Impact on Our Implementation**:
1. **Cannot use name + DOB for duplicate handling** as planned
2. **Must use API player_id as primary identifier**
3. **Need alternative strategy** for handling players with same name

### Solution Strategy

**Option 1: Use API Player ID as Primary Key**
- Store `api_player_id` in players table
- Use API ID to identify players (stable across seasons)
- Handle duplicate names by checking if API ID already exists
- **Pros**: Simple, reliable
- **Cons**: If API changes IDs, we lose connection

**Option 2: Use Name + Team + Season**
- Combine player name with team and season to create unique identifier
- **Pros**: Works with current API data
- **Cons**: Same player on different teams/seasons = different records (not ideal)

**Option 3: Hybrid Approach** ⭐ **RECOMMENDED**
- Use API player_id as primary identifier
- Store API ID in database
- For duplicate names, check if API ID exists first
- If API ID not available (edge case), fall back to name matching
- **Pros**: Best of both worlds
- **Cons**: Slightly more complex

---

## Missing Data

### What We Need But Don't Have

1. **Player Statistics Per Game**
   - No endpoint found for player stats in individual games
   - Need to investigate further or use alternative source

2. **Player Date of Birth**
   - Not in `/players` endpoint
   - May need to supplement with web scraping

3. **Round Number**
   - Only have "week" number and "Regular Season" text
   - Need to parse or calculate round number

4. **Game Type**
   - Need to parse from "round" field ("Regular Season" vs "Finals")

---

## Updated Implementation Plan

### Phase 1: Schema Update

Add `api_player_id` field to players table:

```sql
ALTER TABLE players ADD COLUMN api_player_id INTEGER UNIQUE;
CREATE INDEX idx_players_api_id ON players(api_player_id);
```

### Phase 2: Database Manager Update

Update `get_or_create_player()` to:
1. Check for existing player by `api_player_id` first
2. If not found, check by name (for backwards compatibility)
3. Store API ID when creating new player

### Phase 3: Player Scraping

1. Fetch players by team and season
2. Store API player_id
3. Handle duplicates using API ID

### Phase 4: Game Scraping

1. Fetch games by season and league
2. Parse round information
3. Create/lookup venues
4. Store game data

### Phase 5: Statistics (TBD)

**Need to find**: How to get player statistics per game
- May need to check API documentation PDF more carefully
- May need alternative data source
- May need to contact API support

---

## Rate Limits

**Free Plan Limitations**:
- Standings endpoint: Only seasons 2021-2023
- Other endpoints: Check your dashboard for limits

**Best Practices**:
- Cache responses
- Add delays between requests
- Batch requests when possible

---

## Next Steps

1. **Update Database Schema**: Add `api_player_id` field
2. **Update Database Manager**: Use API ID for player identification
3. **Find Statistics Endpoint**: Review PDF documentation for player stats
4. **Test with Sample Data**: Scrape a few teams/players/games
5. **Validate**: Run validation tests
6. **Handle Missing DOB**: Decide on strategy (supplement with web scraping or accept limitation)

---

## Questions to Answer

1. **Is there a player statistics endpoint we missed?**
   - Review PDF documentation carefully
   - Check for endpoints like `/players/{id}/games` or similar

2. **Can we get DOB from another source?**
   - Web scraping player profile pages
   - Another API
   - Manual data entry for key players

3. **How to get player stats per game?**
   - May be in a different endpoint format
   - May require different API plan
   - May need to use alternative source

---

## Field Mapping (Updated)

```python
API_FIELD_MAPPING = {
    'team': {
        'id': 'team_id',  # Use API team ID
        'name': 'team_name',
    },
    'player': {
        'id': 'api_player_id',  # ⭐ CRITICAL - Use this for identification
        'name': 'player_name',
        # DOB: NOT AVAILABLE ⚠️
    },
    'game': {
        'id': 'api_game_id',  # Use API game ID
        'date': 'game_date',  # Parse from ISO string
        'time': 'game_time',  # Parse from time string
        'season': 'season_year',  # From league.season
        'round': 'round_number',  # Parse from week or round field
        'round_text': 'game_type',  # "Regular Season" or "Finals"
        'venue': 'venue_name',  # String, need to create/lookup
        'home_team_id': 'home_team_id',  # From teams.home.id
        'away_team_id': 'away_team_id',  # From teams.away.id
    },
    'stats': {
        # ⚠️ NOT FOUND YET - Need to investigate
        'disposals': 'TBD',
        'goals': 'TBD',
        'team': 'TBD',
    }
}
```

---

## Summary

**What Works**:
- ✅ Teams endpoint - perfect
- ✅ Games endpoint - good, needs parsing
- ✅ Players endpoint - works but limited data

**What's Missing**:
- ❌ Player date of birth
- ❌ Player statistics per game (not found yet)
- ❌ Detailed player information

**Impact**:
- Need to revise duplicate handling strategy
- May need to supplement with web scraping for DOB
- Need to find statistics endpoint or alternative source

