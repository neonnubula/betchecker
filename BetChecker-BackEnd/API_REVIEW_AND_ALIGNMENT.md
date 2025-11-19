# API Review and Alignment Checklist

## Overview

This document reviews our scraping implementation against the actual API-Sports.io AFL API documentation to ensure alignment.

## What We've Built So Far

### 1. Database Schema ✅
- **Players table**: `player_id`, `player_name`, `date_of_birth`, `first_name`, `last_name`, `debut_year`
- **Teams table**: `team_id`, `team_name`, `is_active`
- **Venues table**: `venue_id`, `venue_name`
- **Games table**: `game_id`, `season_year`, `round_number`, `game_type`, `game_date`, `game_time`, `venue_id`, `home_team_id`, `away_team_id`
- **Player Game Stats table**: `stat_id`, `player_id`, `game_id`, `team_id`, `opponent_team_id`, `venue_id`, `location`, `game_time`, `disposals`, `goals`
- **Player Team History table**: `history_id`, `player_id`, `team_id`, `start_date`, `end_date`, `is_current`

### 2. Database Manager ✅
- `get_or_create_team()` - Handles team insertion
- `get_or_create_venue()` - Handles venue insertion
- `get_or_create_player()` - **CRITICAL**: Uses name + DOB for duplicate handling
- `get_or_create_game()` - Handles game insertion with deduplication
- `insert_player_stats()` - Inserts stats + automatically handles team history updates

### 3. Validation Tests ✅
- 15 comprehensive SQL tests
- Python test runner script
- Tests for duplicates, data integrity, completeness

### 4. API Integration Guide ✅
- Created based on typical API-Sports.io patterns
- Python client implementation
- Test script for API exploration

## Key Information to Verify from API Documentation

### Critical Questions

#### 1. Player Data Structure
- [ ] **Does the API return player date of birth?**
  - Field name: `birth.date`, `date_of_birth`, `dob`, or other?
  - Format: ISO date string, timestamp, or other?
  - **Impact**: Critical for duplicate player handling

- [ ] **What player fields are available?**
  - Name (full name, first, last)
  - DOB (as above)
  - Height, weight
  - Debut year
  - Photo URL
  - **Impact**: Determines what we can store

- [ ] **Player ID structure**
  - Is there a stable player ID we can use?
  - Does it persist across seasons?
  - **Impact**: Can we use API player_id instead of generating our own?

#### 2. Endpoints Available
- [ ] **Players endpoint**
  - URL: `/players`, `/players/{id}`, or other?
  - Can we search by name?
  - Can we get all players?
  - **Impact**: How we fetch player data

- [ ] **Fixtures/Games endpoint**
  - URL: `/fixtures`, `/games`, or other?
  - Can we filter by season?
  - Can we filter by team?
  - What game data is included?
  - **Impact**: How we fetch game data

- [ ] **Player Statistics endpoint**
  - URL: `/players/{id}/statistics`, `/fixtures/{id}/players`, or other?
  - Can we get stats per game?
  - Can we get stats per season?
  - What statistics are available?
  - **Impact**: How we fetch player stats

- [ ] **Teams endpoint**
  - URL: `/teams`, `/teams/{id}`, or other?
  - What team data is included?
  - **Impact**: How we fetch team data

#### 3. Statistics Available
- [ ] **What stats are in the API response?**
  - Disposals? (Field name?)
  - Goals? (Field name?)
  - Other stats we might want?
  - **Impact**: Maps to our `disposals` and `goals` fields

- [ ] **Statistics structure**
  - Per-game stats?
  - Aggregated season stats?
  - Both?
  - **Impact**: How we structure our scraping

#### 4. Game/Fixture Data
- [ ] **What game information is included?**
  - Date and time?
  - Venue?
  - Home/away teams?
  - Round number?
  - Season year?
  - Game type (regular season, finals)?
  - **Impact**: Maps to our `games` table

- [ ] **Team assignment in stats**
  - How do we know which team a player was on?
  - Is it in the statistics response?
  - Or do we need to match with fixture data?
  - **Impact**: Critical for team assignment logic

#### 5. Rate Limits & Authentication
- [ ] **Authentication method**
  - Header name: `x-rapidapi-key`, `x-api-key`, or other?
  - Base URL: `https://v1.afl.api-sports.io` or other?
  - **Impact**: How we authenticate requests

- [ ] **Rate limits**
  - Requests per day?
  - Requests per minute?
  - **Impact**: How we pace our scraping

#### 6. Historical Data
- [ ] **How far back does data go?**
  - All seasons from 2006+?
  - Recent seasons only?
  - **Impact**: May need web scraping for older data

## Alignment Checklist

### ✅ Already Aligned (Based on Assumptions)

1. **Player duplicate handling**
   - Our `get_or_create_player()` uses name + DOB
   - Should work if API provides DOB

2. **Team history tracking**
   - Our `insert_player_stats()` automatically detects team changes
   - Should work if we can determine player's team from API

3. **Database structure**
   - Our schema supports all common AFL data
   - Should accommodate API responses

4. **Validation tests**
   - Tests are generic and should work with any data source
   - No changes needed

### ⚠️ Needs Verification

1. **DOB availability**
   - **Risk**: If API doesn't provide DOB, we can't handle duplicate names
   - **Mitigation**: Use player_id from API as primary identifier if stable

2. **Team assignment**
   - **Risk**: If stats don't include team info, need to match with fixtures
   - **Mitigation**: May need to join fixture data with player stats

3. **Statistics field names**
   - **Risk**: Field names may differ from our assumptions
   - **Mitigation**: Map API fields to our schema fields

4. **Game identification**
   - **Risk**: May need to match games differently than assumed
   - **Mitigation**: Use API game_id if stable, or match by date + teams

### 🔧 Likely Needed Adjustments

1. **Update API client** (`API_SPORTS_IO_GUIDE.md`)
   - Adjust endpoint URLs based on actual API
   - Update field mappings
   - Fix authentication headers

2. **Update Database Manager** (`SCRAPING_IMPLEMENTATION.md`)
   - Adjust player creation logic if using API player_id
   - Update team assignment logic based on API structure
   - Adjust game matching logic

3. **Update test script** (`scripts/test_api_sports.py`)
   - Adjust endpoints to match actual API
   - Update field extraction logic

## Implementation Strategy

### Phase 1: API Exploration
1. Run `scripts/test_api_sports.py` with your API key
2. Inspect actual response structures
3. Document field names and structures
4. Identify any missing data (especially DOB)

### Phase 2: Mapping & Updates
1. Map API fields to our database schema
2. Update API client with correct endpoints
3. Update Database Manager if needed
4. Create field mapping dictionary

### Phase 3: Scraper Implementation
1. Implement player scraper
2. Implement game/fixture scraper
3. Implement stats scraper
4. Add team history logic
5. Test with small dataset

### Phase 4: Validation
1. Run validation tests
2. Check for duplicates
3. Verify team assignments
4. Validate data completeness

## Field Mapping Template

Once we have the actual API structure, fill this in:

```python
API_FIELD_MAPPING = {
    'player': {
        'id': 'api_player_id',  # If we want to store API ID
        'name': 'player_name',
        'first_name': 'first_name',
        'last_name': 'last_name',
        'dob': 'date_of_birth',  # CRITICAL - verify field name
        'debut_year': 'debut_year',
    },
    'team': {
        'id': 'api_team_id',
        'name': 'team_name',
    },
    'game': {
        'id': 'api_game_id',
        'date': 'game_date',
        'season': 'season_year',
        'round': 'round_number',
        'venue': 'venue_name',
        'home_team': 'home_team_id',
        'away_team': 'away_team_id',
    },
    'stats': {
        'disposals': 'disposals',  # Verify field name
        'goals': 'goals',  # Verify field name
        'team': 'team_id',  # How is team determined?
    }
}
```

## Next Steps

1. **Extract key info from PDF**
   - List all endpoints
   - Document response structures
   - Note field names
   - Check for DOB availability

2. **Update documentation**
   - Fix `API_SPORTS_IO_GUIDE.md` with actual endpoints
   - Update field mappings
   - Adjust examples

3. **Test API**
   - Run test script
   - Make sample requests
   - Verify DOB is available
   - Check rate limits

4. **Build scraper**
   - Start with players endpoint
   - Then games/fixtures
   - Then player statistics
   - Integrate with Database Manager

5. **Validate**
   - Run validation tests
   - Check for duplicates
   - Verify data quality

## Questions to Answer

Please review the API documentation and answer:

1. **What is the base URL?**
   - Example: `https://v1.afl.api-sports.io`

2. **What are the main endpoints?**
   - Players: `?`
   - Games/Fixtures: `?`
   - Statistics: `?`
   - Teams: `?`

3. **Does player data include date of birth?**
   - Yes/No
   - If yes, what's the field name?

4. **What statistics are available?**
   - Disposals: field name?
   - Goals: field name?
   - Others?

5. **How is team assignment determined?**
   - In statistics response?
   - Need to match with fixture?

6. **What's the authentication method?**
   - Header name?
   - Base URL?

Once we have these answers, we can quickly align everything!

