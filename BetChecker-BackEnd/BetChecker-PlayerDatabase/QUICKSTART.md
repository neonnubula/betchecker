# Quick Start Guide - AFL Player Stats Database

## What You Have

✅ **Complete database schema** for tracking AFL player statistics  
✅ **Normalized table structure** with proper relationships  
✅ **Sample data** loaded and ready to query  
✅ **100+ example queries** for various analysis types  
✅ **Working SQLite database** (afl_stats.db)

## Database Overview

### Main Tables
1. **players** - All AFL players
2. **teams** - All AFL teams
3. **venues** - All stadiums/grounds
4. **games** - All matches
5. **player_game_stats** ⭐ - Main table (each row = player's stats in one game)

### Key Features
- Unique IDs for everything (players, games, teams, stats)
- Handles players with same names (player_id)
- Tracks home/away performance
- Calculates days since last game
- Supports teammate comparisons
- Optimized with indexes for fast queries

## Files in This Folder

| File | Purpose |
|------|---------|
| `schema.sql` | Database table definitions |
| `sample_data.sql` | Example data (2023 Round 1-2) |
| `example_queries.sql` | 30+ ready-to-use SQL queries |
| `init_database.sh` | Script to create fresh database |
| `afl_stats.db` | Your SQLite database (ready to use!) |
| `README.md` | Full documentation |

## Quick Commands

### View Data
```bash
# Open database
sqlite3 afl_stats.db

# Inside SQLite:
.headers on
.mode column

# See all tables
.tables

# See a table structure
.schema player_game_stats

# Run a query
SELECT * FROM vw_complete_game_stats WHERE player_name = 'Scott Pendlebury';

# Exit
.quit
```

### Common Queries

**1. Player's all games:**
```sql
SELECT game_date, round_name, opponent_name, location, disposals, goals, tackles, result
FROM vw_complete_game_stats
WHERE player_name = 'Scott Pendlebury'
ORDER BY game_date DESC;
```

**2. What % of games had 30+ disposals?**
```sql
SELECT 
    player_name,
    COUNT(*) as total_games,
    ROUND(100.0 * SUM(CASE WHEN disposals >= 30 THEN 1 ELSE 0 END) / COUNT(*), 2) as pct_30_plus
FROM vw_complete_game_stats
WHERE player_name = 'Scott Pendlebury';
```

**3. Home vs Away performance:**
```sql
SELECT 
    location,
    COUNT(*) as games,
    ROUND(AVG(disposals), 2) as avg_disposals,
    ROUND(AVG(goals), 2) as avg_goals
FROM vw_complete_game_stats
WHERE player_name = 'Scott Pendlebury'
GROUP BY location;
```

**4. Performance by venue:**
```sql
SELECT 
    venue_name,
    COUNT(*) as games,
    ROUND(AVG(disposals), 2) as avg_disposals
FROM vw_complete_game_stats
WHERE player_name = 'Scott Pendlebury'
GROUP BY venue_name
HAVING games >= 3
ORDER BY games DESC;
```

**5. Export to CSV:**
```bash
sqlite3 -header -csv afl_stats.db "SELECT * FROM vw_complete_game_stats WHERE player_name = 'Scott Pendlebury';" > pendlebury.csv
```

## Next Steps

### 1. Get Your Data
You need to populate the database with real AFL stats. Options:
- **AFL API** - If available (check AFL website/apps)
- **Web scraping** - From AFL stats websites
- **CSV files** - If you have existing data
- **Manual entry** - For small datasets

### 2. Import Data Order
Always import in this order:
```sql
-- 1. Teams
INSERT INTO teams (team_name, team_abbrev, team_nickname) VALUES (...);

-- 2. Venues  
INSERT INTO venues (venue_name, city, state) VALUES (...);

-- 3. Players
INSERT INTO players (player_name, first_name, last_name) VALUES (...);

-- 4. Games
INSERT INTO games (season_year, round_name, game_type, game_date, venue_id, home_team_id, away_team_id) VALUES (...);

-- 5. Player Stats
INSERT INTO player_game_stats (player_id, game_id, team_id, location, disposals, goals, ...) VALUES (...);

-- 6. Calculate rest days
-- Run the query from sample_data.sql
```

### 3. Modify Schema as Needed
The current schema includes common stats, but you might want to add:
- More stat categories (pressure acts, metres gained, etc.)
- Weather impact fields
- Umpire information
- Brownlow votes
- Fantasy scores
- Quarter-by-quarter breakdowns

To add a column:
```sql
ALTER TABLE player_game_stats ADD COLUMN pressure_acts INTEGER DEFAULT 0;
```

## Example Analysis Workflow

```bash
# 1. Open database
sqlite3 afl_stats.db

# 2. Enable nice formatting
.headers on
.mode column

# 3. Run analysis
SELECT 
    player_name,
    COUNT(*) as games,
    ROUND(AVG(disposals), 2) as avg_disp,
    ROUND(100.0 * SUM(CASE WHEN disposals >= 25 THEN 1 ELSE 0 END) / COUNT(*), 1) as pct_25_plus
FROM vw_complete_game_stats
WHERE team_name = 'Collingwood'
GROUP BY player_name
HAVING games >= 5
ORDER BY avg_disp DESC;

# 4. Export results
.output results.csv
.mode csv
-- Run your query again
.output stdout
```

## Testing the Database

Run these queries to verify everything works:

```sql
-- Check sample data loaded
SELECT COUNT(*) FROM players;          -- Should be 8
SELECT COUNT(*) FROM teams;            -- Should be 18
SELECT COUNT(*) FROM games;            -- Should be 3
SELECT COUNT(*) FROM player_game_stats; -- Should be 5

-- Test the view
SELECT * FROM vw_complete_game_stats;

-- Test a percentage query
SELECT 
    player_name,
    COUNT(*) as games,
    ROUND(100.0 * SUM(CASE WHEN goals >= 2 THEN 1 ELSE 0 END) / COUNT(*), 2) as pct_2_plus_goals
FROM vw_complete_game_stats
GROUP BY player_name;
```

## Tips for Your Analysis

1. **Use the view** - `vw_complete_game_stats` has everything joined already
2. **Percentage queries** - Use `SUM(CASE WHEN ... THEN 1 ELSE 0 END) / COUNT(*)`
3. **Grouping** - GROUP BY for comparing categories (home/away, venues, opponents)
4. **Filtering** - WHERE clause for specific players/teams/dates
5. **Thresholds** - HAVING clause to filter aggregated results
6. **Export** - Always export results to CSV for further analysis

## Need Help?

- Check `example_queries.sql` for 30+ query templates
- Read `README.md` for full documentation
- View `schema.sql` to understand table structure
- Look at `sample_data.sql` to see data format

## Database is Ready!

Your database is already created with sample data. You can:
1. Query it right now
2. Add more data following the examples
3. Modify the schema as your needs evolve
4. Run the example queries to learn

**Start querying:**
```bash
sqlite3 afl_stats.db
```

Enjoy your AFL stats analysis! 🏈📊

