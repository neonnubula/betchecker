# AFL Player Statistics Database

A comprehensive SQLite database for tracking and analyzing AFL player statistics from the Scott Pendlebury era (2006+) onwards.

## Database Structure

### Core Tables

1. **players** - Master list of all AFL players
   - Tracks player names, DOB, debut dates
   - Uses `player_id` to handle players with same names

2. **teams** - AFL teams (current and historical)
   - Team names, abbreviations, nicknames
   - Tracks active/inactive teams

3. **venues** - Stadiums and grounds
   - Venue details including capacity, location
   - City and state information

4. **games** - Master list of all AFL games
   - Links home/away teams and venues
   - Tracks game type (Pre-Season, Regular Season, Finals)
   - Includes scores, attendance, weather

5. **player_game_stats** - Main statistics table ⭐
   - **Each row = one player's stats in one game**
   - Links to player, game, and team
   - Tracks location (Home/Away)
   - Contains all statistical categories
   - Includes `days_since_last_game` field

6. **player_team_history** - Track player transfers
   - Useful for queries about players changing teams

### Statistics Tracked

The `player_game_stats` table includes:

**Core Stats:**
- **Disposals** - Total possessions
- **Goals** - Goals kicked

**Additional Fields:**
- Days since last game (for rest analysis)
- Location (Home/Away)
- Game time (Day/Twilight/Night)
- Venue and opponent (direct access for fast queries)
- Game, player, and team IDs

### Key Features

✅ **Unique IDs** - Every table has proper primary keys  
✅ **Player ID** - Handles players with same names  
✅ **Game ID** - Links all stats to specific games  
✅ **Team ID** - Supports teammate and team-based searches  
✅ **Days Since Last Game** - Built-in field for rest analysis  
✅ **Foreign Keys** - Proper relationships between tables  
✅ **Indexes** - Optimized for common queries  
✅ **View** - `vw_complete_game_stats` joins everything for easy analysis

## Setup

### Create the Database

```bash
# Navigate to the directory
cd /Users/d/BetChecker-PlayerDatabase

# Create the database
sqlite3 afl_stats.db < schema.sql
```

### Verify Setup

```bash
sqlite3 afl_stats.db

# Inside SQLite shell:
.tables                    # List all tables
.schema player_game_stats  # View specific table structure
```

## Common Analysis Queries

### 1. Percentage of Games Above/Below Threshold

```sql
-- What % of games did a player have 30+ disposals?
SELECT 
    player_name,
    COUNT(*) as total_games,
    SUM(CASE WHEN disposals >= 30 THEN 1 ELSE 0 END) as games_30_plus,
    ROUND(100.0 * SUM(CASE WHEN disposals >= 30 THEN 1 ELSE 0 END) / COUNT(*), 2) as percentage
FROM vw_complete_game_stats
WHERE player_name = 'Scott Pendlebury'
GROUP BY player_name;
```

### 2. Home vs Away Performance

```sql
SELECT 
    player_name,
    location,
    COUNT(*) as games,
    ROUND(AVG(disposals), 2) as avg_disposals,
    ROUND(AVG(goals), 2) as avg_goals
FROM vw_complete_game_stats
WHERE player_name = 'Scott Pendlebury'
GROUP BY player_name, location;
```

### 3. Venue-Based Analysis

```sql
-- Performance at specific venues
SELECT 
    venue_name,
    venue_state,
    COUNT(*) as games_played,
    ROUND(AVG(disposals), 2) as avg_disposals,
    ROUND(AVG(goals), 2) as avg_goals
FROM vw_complete_game_stats
WHERE player_name = 'Scott Pendlebury'
GROUP BY venue_name, venue_state
HAVING games_played >= 5
ORDER BY games_played DESC;
```

### 4. Rest Days Analysis

```sql
-- Performance based on days rest
SELECT 
    CASE 
        WHEN days_since_last_game > 7 THEN 'Extended Rest (>7 days)'
        WHEN days_since_last_game IS NULL THEN 'First Game'
        ELSE 'Normal Rest (<=7 days)'
    END as rest_category,
    COUNT(*) as games,
    ROUND(AVG(disposals), 2) as avg_disposals,
    ROUND(AVG(goals), 2) as avg_goals
FROM vw_complete_game_stats
WHERE player_name = 'Scott Pendlebury'
GROUP BY rest_category;
```

### 5. Game Type Comparison

```sql
-- Pre-Season vs Regular Season vs Finals
SELECT 
    game_type,
    COUNT(*) as games,
    ROUND(AVG(disposals), 2) as avg_disposals,
    ROUND(AVG(goals), 2) as avg_goals
FROM vw_complete_game_stats
WHERE player_name = 'Scott Pendlebury'
GROUP BY game_type;
```

### 6. Game Time Analysis

```sql
-- Performance by game time (Day/Twilight/Night)
SELECT 
    game_time,
    COUNT(*) as games,
    ROUND(AVG(disposals), 2) as avg_disposals,
    ROUND(AVG(goals), 2) as avg_goals
FROM vw_complete_game_stats
WHERE player_name = 'Scott Pendlebury'
GROUP BY game_time;
```

### 7. Teammate Comparisons

```sql
-- Compare two teammates in same games
SELECT 
    g.game_date,
    g.round_name,
    g.game_type,
    p1.player_name as player1,
    p1.disposals as p1_disposals,
    p1.goals as p1_goals,
    p2.player_name as player2,
    p2.disposals as p2_disposals,
    p2.goals as p2_goals
FROM player_game_stats pgs1
JOIN vw_complete_game_stats p1 ON pgs1.stat_id = p1.stat_id
JOIN player_game_stats pgs2 ON pgs1.game_id = pgs2.game_id 
    AND pgs1.team_id = pgs2.team_id 
    AND pgs1.player_id != pgs2.player_id
JOIN vw_complete_game_stats p2 ON pgs2.stat_id = p2.stat_id
JOIN games g ON pgs1.game_id = g.game_id
WHERE p1.player_name = 'Scott Pendlebury'
    AND p2.player_name = 'Steele Sidebottom'
ORDER BY g.game_date;
```

## Calculating Days Since Last Game

After inserting new stats, run this query to calculate rest days:

```sql
WITH ranked_games AS (
    SELECT 
        pgs.stat_id,
        pgs.player_id,
        pgs.game_id,
        g.game_date,
        LAG(g.game_date) OVER (PARTITION BY pgs.player_id ORDER BY g.game_date) as prev_game_date
    FROM player_game_stats pgs
    JOIN games g ON pgs.game_id = g.game_id
)
UPDATE player_game_stats
SET days_since_last_game = (
    SELECT JULIANDAY(rg.game_date) - JULIANDAY(rg.prev_game_date)
    FROM ranked_games rg
    WHERE rg.stat_id = player_game_stats.stat_id
);
```

## Data Import Notes

When importing data, follow this order:
1. **teams** - Load all teams first
2. **venues** - Load all venues
3. **players** - Load all players
4. **games** - Load game data (references teams and venues)
5. **player_game_stats** - Load individual stats (references players and games)
6. Run the "days since last game" calculation

## Future Enhancements

Consider adding:
- **Opposition team stats** - Track opponent averages
- **Weather conditions** - Already in games table, can analyze impact
- **Umpire data** - Track umpire tendencies
- **Brownlow votes** - For awards tracking
- **Fantasy scores** - If relevant for analysis
- **Quarter-by-quarter stats** - More granular analysis
- **Position data** - Track what position players played

## SQLite Tips

```bash
# Export query results to CSV
sqlite3 -header -csv afl_stats.db "SELECT * FROM vw_complete_game_stats WHERE player_name = 'Scott Pendlebury';" > pendlebury_stats.csv

# Enable column headers and formatting
sqlite3 afl_stats.db
.headers on
.mode column
SELECT * FROM vw_complete_game_stats LIMIT 5;

# Import CSV data
.mode csv
.import teams.csv teams
```

## Next Steps

1. ✅ Schema created
2. ⏳ Decide on data source (AFL API, web scraping, CSV files)
3. ⏳ Import historical data
4. ⏳ Test queries and validate results
5. ⏳ Build additional views/queries as needed

