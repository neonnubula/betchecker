# Scraping Summary & Next Steps

## What We've Planned

### ✅ Database Schema Review
- **Players Table**: Uses `player_id` (AUTOINCREMENT) + `player_name` + `date_of_birth`
- **Unique Constraint Needed**: Add `(player_name, date_of_birth)` to prevent duplicates
- **Team History Table**: `player_team_history` tracks team movements over time

### ✅ Key Requirements Identified

1. **Player Duplicate Handling**
   - Use `(player_name + date_of_birth)` as unique identifier
   - Always check for existing player before inserting
   - Migration script created: `add_player_unique_constraint.sql`

2. **Team Movement Tracking**
   - Detect when player's team changes between games
   - Update `player_team_history` automatically
   - Logic: Compare current team_id with last game's team_id

3. **Data Insertion Order**
   - Teams → Venues → Players → Games → Player Stats → Team History

## Files Created

1. **SCRAPING_PLAN.md** - Comprehensive strategy document
2. **SCRAPING_IMPLEMENTATION.md** - Code examples and implementation guide
3. **add_player_unique_constraint.sql** - Database migration for unique constraint

## What You Need to Do Next

### Step 1: Choose Data Sources
Research and identify which websites have:
- ✅ Player names + dates of birth
- ✅ Game results and fixtures
- ✅ Player statistics per game
- ✅ Team lineups (to determine which team a player was on)

**Potential Sources:**
- AFL.com.au (official site)
- FootyWire.com
- AFLTables.com
- AFL API (if available)

### Step 2: Apply Database Migration
```bash
cd BetChecker-BackEnd/BetChecker-PlayerDatabase
sqlite3 afl_stats.db < add_player_unique_constraint.sql
```

### Step 3: Inspect Target Websites
For each potential data source:
1. Open browser DevTools (F12)
2. Navigate to a player profile page
3. Find where DOB is displayed
4. Note the HTML structure/CSS selectors
5. Navigate to a game results page
6. Find where player stats are displayed
7. Note the HTML structure

### Step 4: Create Directory Structure
```bash
cd BetChecker-BackEnd
mkdir -p scrapers database scripts
touch scrapers/__init__.py database/__init__.py scripts/__init__.py
```

### Step 5: Implement Database Manager
Copy the code from `SCRAPING_IMPLEMENTATION.md` into:
- `database/db_manager.py`

### Step 6: Implement Base Scraper
Copy the code from `SCRAPING_IMPLEMENTATION.md` into:
- `scrapers/base_scraper.py`

### Step 7: Build Specific Scrapers
Start with one data source and build:
- `scrapers/teams_scraper.py` - Scrape team list
- `scrapers/players_scraper.py` - Scrape player profiles (name + DOB)
- `scrapers/games_scraper.py` - Scrape game fixtures
- `scrapers/stats_scraper.py` - Scrape player stats per game

### Step 8: Test with Sample Data
1. Scrape 1-2 players
2. Scrape 1-2 games
3. Verify data in database
4. Check team history updates work

### Step 9: Scale Up
Once tested, run for:
- All teams
- All venues
- Historical seasons (2006+)
- All players and games

## Critical Implementation Points

### Player Identification
```python
# ALWAYS use name + DOB
player_id = db.get_or_create_player(
    player_name="Scott Pendlebury",
    date_of_birth=date(1988, 1, 7)  # CRITICAL!
)
```

### Team Change Detection
```python
# Automatically handled in insert_player_stats()
# Checks if team_id changed from last game
# Updates player_team_history automatically
```

### Data Validation
- Verify player's team is either home_team or away_team
- Verify opponent is the other team
- Verify venue matches game venue
- Check for duplicate stats (player_id + game_id)

## Questions to Answer Before Starting

1. **Which website(s) will you scrape?**
   - Need to research availability and structure

2. **Do they have DOB information?**
   - Critical for duplicate handling
   - If not, need alternative strategy

3. **What's the HTML structure?**
   - Need to inspect and identify CSS selectors

4. **Are there rate limits?**
   - Need to respect robots.txt
   - Add appropriate delays

5. **How far back to scrape?**
   - Schema supports 2006+
   - Start with recent seasons for testing?

## Testing Checklist

- [ ] Database migration applied successfully
- [ ] Can insert teams without duplicates
- [ ] Can insert players with same name but different DOB
- [ ] Can detect team changes
- [ ] Can insert game stats correctly
- [ ] Team history updates automatically
- [ ] Days since last game calculates correctly

## Resources

- **Schema Documentation**: `BetChecker-PlayerDatabase/SCHEMA_EXPLAINED_SIMPLY.md`
- **Example Queries**: `BetChecker-PlayerDatabase/example_queries.sql`
- **Table Relationships**: `BetChecker-PlayerDatabase/TABLE_RELATIONSHIPS.md`
- **Scraping Plan**: `SCRAPING_PLAN.md`
- **Implementation Guide**: `SCRAPING_IMPLEMENTATION.md`

## Need Help?

When you're ready to start implementing:
1. Share the data source URLs you want to scrape
2. Share example HTML from player profile pages
3. Share example HTML from game results pages
4. I can help write the specific scraper code!

