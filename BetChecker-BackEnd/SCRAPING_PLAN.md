# AFL Statistics Scraping Plan

## Overview
This document outlines the strategy for scraping AFL statistics and populating the database. The focus is on handling duplicate player names, tracking team movements, and ensuring data integrity.

## Key Schema Requirements

### 1. Player Identification
- **Primary Key**: `player_id` (AUTOINCREMENT)
- **Unique Constraint**: `player_name` + `date_of_birth` (composite unique key)
- **Why**: Handles players with same names (e.g., multiple "Josh Smith" players)
- **Implementation**: Check for existing player by (name, DOB) before inserting

### 2. Team Movement Tracking
- **Table**: `player_team_history`
- **Fields**: `player_id`, `team_id`, `start_date`, `end_date`, `is_current`
- **Purpose**: Track when players switch teams between seasons
- **Logic**: When inserting stats, check if player's team changed since last game

### 3. Data Insertion Order
1. **teams** (no dependencies)
2. **venues** (no dependencies)
3. **players** (no dependencies, but check for duplicates)
4. **games** (requires teams and venues)
5. **player_game_stats** (requires players, games, teams)
6. **player_team_history** (requires players and teams)

## Scraping Strategy

### Phase 1: Master Data (One-Time Setup)

#### 1.1 Teams
- **Source**: AFL official website or Wikipedia
- **Data Needed**:
  - Team name (e.g., "Collingwood")
  - Team abbreviation (e.g., "COLL")
  - Is active (boolean)
- **Action**: Insert all 18 current teams + any historical teams

#### 1.2 Venues
- **Source**: AFL fixtures/results pages
- **Data Needed**:
  - Venue name (e.g., "MCG", "Marvel Stadium")
- **Action**: Extract unique venues from game data

#### 1.3 Players
- **Source**: AFL player profiles, match reports, or official stats sites
- **Data Needed**:
  - Full name (e.g., "Scott Pendlebury")
  - First name, Last name (if available)
  - Date of birth (CRITICAL for duplicate handling)
  - Debut year
- **Duplicate Handling**:
  ```python
  # Pseudo-code
  def get_or_create_player(name, dob):
      existing = db.query("SELECT player_id FROM players WHERE player_name = ? AND date_of_birth = ?", name, dob)
      if existing:
          return existing.player_id
      else:
          return db.insert("INSERT INTO players (player_name, date_of_birth) VALUES (?, ?)", name, dob)
  ```

### Phase 2: Game Data (Historical + Ongoing)

#### 2.1 Games
- **Source**: AFL fixtures/results pages (e.g., afl.com.au, footywire.com)
- **Data Needed**:
  - Season year
  - Round number (NULL for finals)
  - Game type ('Pre-Season', 'Regular Season', 'Finals')
  - Game date
  - Game time
  - Venue ID (lookup or create)
  - Home team ID
  - Away team ID
- **Deduplication**: Check by (season_year, round_number, game_date, home_team_id, away_team_id)

#### 2.2 Player Game Stats
- **Source**: Match reports, player stats pages
- **Data Needed**:
  - Player ID (lookup by name + DOB)
  - Game ID (lookup by game details)
  - Team ID (team player played for)
  - Opponent team ID (other team in the game)
  - Venue ID (from game)
  - Location ('Home' or 'Away')
  - Game time ('Day', 'Twilight', 'Night')
  - Disposals
  - Goals
- **Team Assignment Logic**:
  ```python
  # Determine which team player was on
  if player_name in home_team_lineup:
      team_id = home_team_id
      opponent_team_id = away_team_id
      location = 'Home'
  else:
      team_id = away_team_id
      opponent_team_id = home_team_id
      location = 'Away'
  ```

### Phase 3: Team Movement Detection

#### 3.1 Detecting Team Changes
When inserting player stats, check if team changed:

```python
def insert_player_stats(player_id, game_id, team_id, game_date):
    # Get player's last game
    last_game = db.query("""
        SELECT team_id, game_date 
        FROM player_game_stats 
        WHERE player_id = ? 
        ORDER BY game_date DESC 
        LIMIT 1
    """, player_id)
    
    if last_game and last_game.team_id != team_id:
        # Team changed! Update player_team_history
        # End previous team assignment
        db.update("""
            UPDATE player_team_history 
            SET end_date = ?, is_current = 0 
            WHERE player_id = ? AND is_current = 1
        """, game_date, player_id)
        
        # Start new team assignment
        db.insert("""
            INSERT INTO player_team_history (player_id, team_id, start_date, is_current)
            VALUES (?, ?, ?, 1)
        """, player_id, team_id, game_date)
    
    # Insert the stats
    db.insert("INSERT INTO player_game_stats ...")
```

#### 3.2 Initial Team Assignment
For a player's first game:
```python
# When inserting first stats for a player
db.insert("""
    INSERT INTO player_team_history (player_id, team_id, start_date, is_current)
    VALUES (?, ?, ?, 1)
""", player_id, team_id, game_date)
```

## Data Sources to Consider

### Option 1: API-Sports.io AFL API ⭐ RECOMMENDED
- **URL**: https://api-sports.io/documentation/afl/v1
- **Pros**: 
  - Structured JSON data (no HTML parsing)
  - Reliable and maintained
  - Likely includes player DOB
  - Official data source
- **Cons**: 
  - Requires API key (may have free tier)
  - Rate limits based on subscription
  - May not have all historical data
- **Access**: REST API calls
- **Guide**: See `API_SPORTS_IO_GUIDE.md`
- **Test Script**: `scripts/test_api_sports.py`

### Option 2: AFL Official Website (afl.com.au)
- **Pros**: Official, reliable, comprehensive
- **Cons**: May have rate limiting, structure may change
- **Access**: Check for API or scrape HTML

### Option 3: FootyWire (footywire.com)
- **Pros**: Well-structured, historical data, player profiles
- **Cons**: May have terms of service restrictions
- **Access**: HTML scraping

### Option 4: AFL Tables (afltables.com)
- **Pros**: Comprehensive historical data, well-organized
- **Cons**: HTML scraping required
- **Access**: HTML scraping

## Implementation Plan

### Step 1: Create Scraping Module Structure
```
BetChecker-BackEnd/
├── scrapers/
│   ├── __init__.py
│   ├── base_scraper.py      # Base class with common utilities
│   ├── teams_scraper.py     # Scrape teams
│   ├── venues_scraper.py    # Scrape venues
│   ├── players_scraper.py   # Scrape player info
│   ├── games_scraper.py     # Scrape game data
│   └── stats_scraper.py    # Scrape player stats
├── database/
│   ├── __init__.py
│   ├── db_manager.py        # Database operations
│   └── models.py           # Data models
└── scripts/
    ├── scrape_all.py       # Main scraping script
    └── update_team_history.py  # Update team movements
```

### Step 2: Database Manager
Create a `db_manager.py` with helper functions:
- `get_or_create_team(name)` - Returns team_id
- `get_or_create_venue(name)` - Returns venue_id
- `get_or_create_player(name, dob)` - Returns player_id (handles duplicates)
- `get_or_create_game(...)` - Returns game_id
- `insert_player_stats(...)` - Inserts stats + handles team history
- `update_days_since_last_game()` - Calculate rest days

### Step 3: Scraper Base Class
```python
class BaseScraper:
    def __init__(self, db_manager):
        self.db = db_manager
        self.session = requests.Session()
        self.session.headers.update({
            'User-Agent': 'BetChecker/1.0'
        })
    
    def fetch_page(self, url):
        # Rate limiting, retries, error handling
        pass
    
    def parse_html(self, html):
        # Common HTML parsing utilities
        pass
```

### Step 4: Player Scraper (Critical for Duplicates)
```python
class PlayerScraper(BaseScraper):
    def scrape_player_profile(self, player_url):
        # Extract: name, DOB, debut year
        pass
    
    def get_or_create_player(self, name, dob, debut_year=None):
        # Check for existing player by (name, DOB)
        # If exists, return existing player_id
        # If not, create new player
        pass
```

### Step 5: Stats Scraper (Handles Team Movement)
```python
class StatsScraper(BaseScraper):
    def scrape_game_stats(self, game_url):
        # Extract all player stats for a game
        # For each player:
        #   1. Get/create player (by name + DOB)
        #   2. Determine which team they played for
        #   3. Check if team changed (update player_team_history)
        #   4. Insert stats
        pass
```

## Handling Edge Cases

### 1. Players with Same Name
- **Solution**: Always use (name + DOB) as unique identifier
- **Example**: Two "Josh Smith" players with different DOBs
- **Implementation**: 
  ```sql
  CREATE UNIQUE INDEX idx_player_name_dob ON players(player_name, date_of_birth);
  ```

### 2. Missing Date of Birth
- **Strategy**: 
  - Try to find DOB from player profile pages
  - If unavailable, use name + debut_year as fallback
  - Log warnings for manual review

### 3. Team Changes Mid-Season
- **Scenario**: Player traded mid-season
- **Solution**: `player_team_history` tracks exact dates
- **Logic**: When inserting stats, check if team_id differs from last game

### 4. Retired Players Returning
- **Scenario**: Player retires, then comes back
- **Solution**: Same player_id, new entry in `player_team_history`

### 5. Name Variations
- **Issue**: "Scott Pendlebury" vs "S. Pendlebury" vs "S Pendlebury"
- **Solution**: 
  - Normalize names (strip, title case)
  - Match by first_name + last_name if available
  - Use fuzzy matching as fallback

## Data Quality Checks

### Validation Rules
1. **Player Stats**: 
   - Disposals >= 0
   - Goals >= 0
   - Player must exist in players table
   - Game must exist in games table

2. **Team Assignment**:
   - Player's team must be either home_team or away_team
   - Opponent must be the other team

3. **Game Consistency**:
   - Venue in stats must match venue in game
   - Date in stats must match date in game

### Deduplication
- **Games**: Check by (season_year, round_number, game_date, home_team_id, away_team_id)
- **Player Stats**: UNIQUE constraint on (player_id, game_id)
- **Players**: Check by (player_name, date_of_birth)

## Rate Limiting & Ethics

### Best Practices
1. **Respect robots.txt**: Check before scraping
2. **Rate Limiting**: Add delays between requests (1-2 seconds)
3. **User-Agent**: Identify your scraper
4. **Caching**: Cache pages to avoid re-scraping
5. **Error Handling**: Retry with exponential backoff

### Legal Considerations
- Review terms of service for each site
- Consider contacting site owners for permission
- Use official APIs if available

## Testing Strategy

### Unit Tests
- Test duplicate player detection
- Test team change detection
- Test data validation

### Integration Tests
- Test full scraping workflow
- Test database insertion order
- Test team history updates

### Data Validation
- Compare scraped data with known values
- Check for missing games/stats
- Verify team assignments

## Next Steps

1. **Choose Data Source**: Evaluate options, check availability
2. **Create Database Manager**: Implement helper functions
3. **Build Base Scraper**: Common utilities and error handling
4. **Implement Team Scraper**: Start with simple, static data
5. **Implement Player Scraper**: Focus on name + DOB extraction
6. **Implement Game Scraper**: Extract game metadata
7. **Implement Stats Scraper**: Extract player stats + handle team changes
8. **Add Team History Logic**: Track team movements
9. **Test with Sample Data**: Validate against known results
10. **Scale Up**: Run for historical seasons

## Questions to Answer

1. **What data sources are available?** (Need to research)
2. **Do sources have DOB information?** (Critical for duplicate handling)
3. **How far back should we scrape?** (2006+ per schema)
4. **How often to update?** (Weekly during season? Daily?)
5. **How to handle missing data?** (Log and flag for manual review)

## Notes

- **Player ID is AUTOINCREMENT**: Don't manually set it
- **Use transactions**: Wrap inserts in transactions for data integrity
- **Logging**: Log all inserts, updates, and errors
- **Backup**: Backup database before bulk inserts
- **Incremental Updates**: Track last scrape date to avoid re-scraping

