# Full Data Scraping Plan - API to Database

## Overview

This document outlines the complete strategy for scraping AFL data from API-Sports.io and populating our database. We'll use their API to fill our own database tables systematically.

---

## API Endpoints Summary

### 1. Seasons
**Endpoint**: `GET /seasons`  
**Purpose**: Discover available seasons  
**Returns**: `[2011, 2012, ..., 2025]` (15 seasons)  
**Requests**: 1 (one-time)

### 2. Teams
**Endpoint**: `GET /teams`  
**Purpose**: Get all AFL teams  
**Returns**: 18 teams with `id`, `name`, `logo`  
**Requests**: 1 (one-time)

### 3. Players
**Endpoint**: `GET /players?team={team_id}&season={year}`  
**Purpose**: Get players for each team/season  
**Returns**: Player `id` and `name`  
**Requests**: ~18 teams × 15 seasons = ~270 requests (or prioritize recent seasons)

### 4. Games
**Endpoint**: `GET /games?season={year}&league=1`  
**Purpose**: Get all games for a season  
**Returns**: Complete game data (date, venue, teams, scores, round info)  
**Requests**: 1 per season = 15 requests

### 5. Game Player Statistics ⭐ **CORE DATA**
**Endpoint**: `GET /games/statistics/players?id={game_id}`  
**Purpose**: Get per-game player statistics  
**Returns**: All players with stats for that game  
**Requests**: ~216 games per season × 15 seasons = ~3,240 requests

---

## Database Mapping

### Teams Table
**API → Database**:
```python
API: {"id": 1, "name": "Adelaide Crows", "logo": "..."}
DB:  team_id=1, team_name="Adelaide Crows", api_team_id=1
```
- Use API team ID directly as our team_id
- Store team_name from API
- Logo URL optional (can store if needed)

### Players Table
**API → Database**:
```python
API: {"id": 156, "name": "Scott Pendlebury"}
DB:  api_player_id=156, player_name="Scott Pendlebury"
```
- Store API player ID as `api_player_id` (unique identifier)
- Store player name
- No DOB available from API

### Venues Table
**API → Database**:
```python
API: "venue": "Melbourne Cricket Ground" (from games endpoint)
DB:  venue_name="Melbourne Cricket Ground"
```
- Extract unique venues from games
- Create/lookup venues by name

### Games Table
**API → Database**:
```python
API: {
  "game": {"id": 2524},
  "date": "2023-03-16T19:20:00+00:00",
  "time": "19:20",
  "round": "Regular Season",
  "week": 1,
  "venue": "Melbourne Cricket Ground",
  "teams": {"home": {"id": 12}, "away": {"id": 3}}
}
DB: {
  api_game_id=2524,
  season_year=2023,
  round_number=1,  # from "week"
  game_type="Regular Season",  # from "round"
  game_date="2023-03-16",
  game_time="19:20",
  venue_id=<lookup>,
  home_team_id=12,
  away_team_id=3
}
```

### Player Game Stats Table ⭐ **CORE DATA**
**API → Database**:
```python
API: {
  "player": {"id": 156, "number": 10},
  "disposals": 25,
  "goals": {"total": 2, "assists": 1},
  "kicks": 15,
  "handballs": 10,
  ...
}
DB: {
  player_id=<lookup by api_player_id>,
  game_id=<lookup by api_game_id>,
  team_id=12,  # from team context
  opponent_team_id=3,  # other team in game
  venue_id=<from game>,
  location="Home" or "Away",  # determine from team_id vs home/away
  disposals=25,
  goals=2,
  ...
}
```

---

## Scraping Strategy

### Phase 1: Master Data (One-Time Setup)
**Order**: Teams → Venues (from games) → Players

1. **Teams** (1 request)
   - Scrape `/teams`
   - Insert all teams with API IDs
   - **Status**: Complete, no updates needed

2. **Venues** (Extract from games)
   - Scrape games first to discover venues
   - Extract unique venue names
   - Create venues table entries
   - **Status**: Done during game scraping

3. **Players** (~270 requests for all seasons, or prioritize recent)
   - For each season (prioritize recent):
     - For each team:
       - Scrape `/players?team={id}&season={year}`
       - Insert players with API IDs
   - **Optimization**: Can skip if player already exists (check by api_player_id)

### Phase 2: Games Data (Per Season)
**Order**: Games → Venues (extract) → Game Statistics

1. **Games** (1 request per season)
   - Scrape `/games?season={year}&league=1`
   - Extract venues (create if needed)
   - Insert games with API IDs
   - **Status**: Can do incrementally per season

2. **Game Player Statistics** ⭐ **CORE** (~216 requests per season)
   - For each game:
     - Scrape `/games/statistics/players?id={game_id}`
     - Process each team's players
     - Insert into `player_game_stats`
   - **Status**: This is the critical data for our search function

---

## Rate Limiting Strategy

### Free Plan Limits
- **Daily**: 100 requests/day
- **Per Minute**: 10 requests/minute (6 seconds between requests)

### Request Budget Per Phase

**Phase 1: Master Data**
- Teams: 1 request
- Players: ~270 requests (all seasons) OR ~90 requests (last 5 seasons)
- **Total**: ~271 requests (~3 days) OR ~91 requests (~1 day)

**Phase 2: Games & Stats**
- Games: 15 requests (1 per season)
- Game Stats: ~3,240 requests (all seasons) OR ~1,080 requests (last 5 seasons)
- **Total**: ~3,255 requests (~33 days) OR ~1,095 requests (~11 days)

### Optimization Strategies

1. **Prioritize Recent Seasons**
   - Start with 2023, 2024, 2025
   - Add older seasons incrementally
   - **Benefit**: Get core functionality working faster

2. **Incremental Updates**
   - Only scrape new games (check `api_game_id` not in DB)
   - Only scrape new players (check `api_player_id` not in DB)
   - **Benefit**: Daily updates use minimal requests

3. **Batch Processing**
   - Process one season at a time
   - Track progress in database
   - Resume from last completed season

4. **Skip Existing Data**
   - Check if game stats already exist before scraping
   - Check if player already exists before inserting
   - **Benefit**: Idempotent scraping, can re-run safely

---

## Scraping Order (Recommended)

### Initial Setup (Day 1)
1. ✅ Scrape teams (1 request)
2. ✅ Scrape seasons list (1 request) - for reference
3. ✅ Scrape players for recent seasons (2023-2025) (~54 requests)
4. ✅ Scrape games for recent seasons (3 requests)
5. ✅ Extract venues from games
6. **Remaining**: ~41 requests for testing

### Core Data Collection (Days 2-12)
**Per Season** (2023-2025):
1. Scrape games (1 request)
2. Extract venues
3. Scrape game statistics (~216 requests per season)
   - Process each game
   - Insert player stats
4. **Total per season**: ~217 requests (~2-3 days)

### Historical Data (Optional, Days 13+)
- Add older seasons incrementally
- Prioritize by need
- Can run in background

---

## Data Relationships & Dependencies

### Dependency Chain
```
Seasons (reference)
    ↓
Teams (master data)
    ↓
Players (master data, per team/season)
    ↓
Games (requires teams, venues)
    ↓
Game Statistics (requires games, players, teams)
```

### Lookup Requirements
- **Player Stats → Player**: Lookup by `api_player_id`
- **Player Stats → Game**: Lookup by `api_game_id`
- **Player Stats → Team**: Use API team ID directly
- **Game → Venue**: Lookup/create by venue name
- **Game → Teams**: Use API team IDs directly

---

## Error Handling & Data Quality

### Common Issues

1. **Missing Game Statistics**
   - Some games may not have statistics available
   - **Handle**: Skip and log, continue with next game

2. **Player Not Found**
   - Player ID in stats doesn't exist in players table
   - **Handle**: Create player record with API ID (name may be missing)

3. **Venue Variations**
   - Same venue with different names (e.g., "MCG" vs "Melbourne Cricket Ground")
   - **Handle**: Normalize venue names, create mapping

4. **Rate Limit Hit**
   - **Handle**: Wait and retry, track daily usage

5. **Incomplete Data**
   - Some fields may be null
   - **Handle**: Use defaults (0 for stats), log warnings

---

## Implementation Checklist

### Database Setup
- [x] Add `api_player_id` to players table
- [x] Add `api_game_id` to games table
- [x] Add `api_team_id` to teams table (or use team_id directly)
- [x] Create indexes on API IDs for fast lookups

### Scraper Functions
- [ ] `scrape_teams()` - Get all teams
- [ ] `scrape_seasons()` - Get available seasons
- [ ] `scrape_players(team_id, season)` - Get players for team/season
- [ ] `scrape_games(season)` - Get all games for season
- [ ] `scrape_game_statistics(game_id)` - Get player stats for game
- [ ] `process_game_stats(game_data)` - Parse and insert stats

### Data Processing
- [ ] `get_or_create_venue(venue_name)` - Venue lookup/create
- [ ] `get_player_by_api_id(api_player_id)` - Player lookup
- [ ] `get_game_by_api_id(api_game_id)` - Game lookup
- [ ] `determine_location(team_id, home_team_id, away_team_id)` - Home/Away

### Rate Limiting
- [ ] Request counter/tracker
- [ ] Delay between requests (6+ seconds)
- [ ] Daily limit checker
- [ ] Retry logic with exponential backoff

### Progress Tracking
- [ ] Track scraped seasons
- [ ] Track scraped games per season
- [ ] Resume capability
- [ ] Logging system

---

## Example Scraping Flow

```python
# 1. Setup
teams = scrape_teams()  # 1 request
seasons = scrape_seasons()  # 1 request

# 2. Master Data
for season in [2023, 2024, 2025]:  # Prioritize recent
    for team in teams:
        players = scrape_players(team['id'], season)  # ~54 requests
        insert_players(players)

# 3. Games
for season in [2023, 2024, 2025]:
    games = scrape_games(season)  # 3 requests
    extract_venues(games)
    insert_games(games)

# 4. Game Statistics ⭐ CORE
for season in [2023, 2024, 2025]:
    games = get_games_for_season(season)
    for game in games:
        stats = scrape_game_statistics(game['api_game_id'])  # ~648 requests
        process_and_insert_stats(stats)
```

---

## Next Steps

1. **Build scraper functions** based on this plan
2. **Test with one season** (2023) first
3. **Validate data quality** using our validation tests
4. **Scale up** to multiple seasons
5. **Set up incremental updates** for new games

---

## Summary

**Total Requests Needed**:
- **Master Data**: ~271 requests (all seasons) or ~91 requests (recent 5)
- **Games**: 15 requests (1 per season)
- **Game Statistics**: ~3,240 requests (all seasons) or ~1,080 requests (recent 5)

**Timeline** (Free Plan - 100 requests/day):
- **Recent 5 seasons**: ~12 days
- **All 15 seasons**: ~36 days

**Priority**: Focus on recent seasons (2023-2025) first to get core functionality working, then add historical data incrementally.

