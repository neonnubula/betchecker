# Schema Changes v2 - Further Simplification + Game Time Analysis

## Summary of Changes

We've further streamlined the database and added game time tracking for better analysis.

---

## 1. PLAYERS Table - Simplified Debut Tracking

### Changed:
```sql
-- Before
debut_date DATE  -- Full date like '2006-05-05'

-- After
debut_year INTEGER  -- Just the year like 2006
```

### Why?
- You likely only need to know what year a player started, not the exact date
- Simpler to work with and remember
- Easier queries: "Show me all players who debuted in 2006"
- Less data to store

### Example:
```sql
-- Old way
INSERT INTO players (player_name, debut_date) VALUES ('Scott Pendlebury', '2006-05-05');

-- New way
INSERT INTO players (player_name, debut_year) VALUES ('Scott Pendlebury', 2006);
```

---

## 2. TEAMS Table - Maximum Simplification

### Removed:
- ❌ `team_abbrev` (COLL, RICH, etc.)
- ❌ `team_nickname` (Magpies, Tigers, etc.)
- ❌ `founded_year` (1892, etc.)

### Kept:
- ✅ `team_id` (unique identifier)
- ✅ `team_name` (Collingwood, Richmond, etc.)
- ✅ `is_active` (for historical teams)

### Why?
- You only need the full team name
- Abbreviations aren't necessary for queries
- Nicknames and founding years are trivia, not analysis data
- **Result:** Super clean, minimal table

### Example:
```sql
-- Old way
INSERT INTO teams (team_name, team_abbrev, team_nickname, founded_year) 
VALUES ('Collingwood', 'COLL', 'Magpies', 1892);

-- New way
INSERT INTO teams (team_name) VALUES ('Collingwood');
```

---

## 3. GAMES Table - Removed Round Names

### Removed:
- ❌ `round_name` ('Round 1', 'Qualifying Final', etc.)

### Kept:
- ✅ `round_number` (1, 2, 3, etc.)
- ✅ `game_type` ('Regular Season', 'Finals', 'Pre-Season')

### Why?
- Round number is sufficient for identification
- Round name is just a text label that can be generated if needed
- You can determine if it's "Round 1" or "Final" from round_number + game_type
- Less redundant data

### Example:
```sql
-- You can still identify everything:
round_number = 1, game_type = 'Regular Season' → It's Round 1
round_number = NULL, game_type = 'Finals' → It's a final
```

---

## 4. PLAYER_GAME_STATS Table - Added Game Time! ⭐

### Added:
```sql
game_time TEXT  -- 'Day', 'Twilight', or 'Night'
```

### Why This Is Important:
Players often perform differently based on game time:
- **Day games** - Better visibility, different conditions
- **Twilight games** - Mixed lighting, transitional
- **Night games** - Under lights, different feel

### How It Works:
You set the time boundaries yourself based on start time:
- Day: Games starting before 2:00 PM (or your preference)
- Twilight: Games starting 2:00 PM - 5:00 PM
- Night: Games starting after 5:00 PM

**Example classification:**
```
Game start time: 14:30 (2:30 PM) → game_time = 'Twilight'
Game start time: 19:20 (7:20 PM) → game_time = 'Night'
Game start time: 13:10 (1:10 PM) → game_time = 'Day'
```

### Analysis Power:
Now you can ask questions like:
- "What % of times did Pendlebury get 30+ disposals in night games?"
- "Does he perform better during day or night games?"
- "Home night games vs away night games?"
- "Performance at MCG in night games vs day games?"

### Database Enforcement:
We added a CHECK constraint to ensure only valid values:
```sql
CHECK (game_time IS NULL OR game_time IN ('Day', 'Twilight', 'Night'))
```

This prevents typos like 'Nite' or 'Evening' - only the three official values work!

### Added Index:
```sql
CREATE INDEX idx_pgs_game_time ON player_game_stats(game_time);
```
**Result:** Lightning-fast filtering by game time! ⚡

---

## Updated View

The `vw_complete_game_stats` view now includes:
- ✅ `game_time` field
- ✅ No more `round_name` 
- ✅ No more `team_abbrev` or `opponent_abbrev`

**Cleaner and includes everything you need for analysis!**

---

## Example Queries with New Features

### Query 1: Performance by Game Time
```sql
SELECT 
    player_name,
    game_time,
    COUNT(*) as games,
    ROUND(AVG(disposals), 1) as avg_disposals,
    ROUND(AVG(goals), 1) as avg_goals,
    ROUND(100.0 * SUM(CASE WHEN disposals >= 30 THEN 1 ELSE 0 END) / COUNT(*), 1) as pct_30_plus
FROM vw_complete_game_stats
WHERE player_name = 'Scott Pendlebury'
GROUP BY player_name, game_time;
```

### Query 2: Night Games at Specific Venue
```sql
SELECT 
    player_name,
    venue_name,
    game_time,
    COUNT(*) as games,
    ROUND(AVG(disposals), 1) as avg_disp
FROM vw_complete_game_stats
WHERE venue_name = 'MCG' 
  AND game_time = 'Night'
GROUP BY player_name, venue_name, game_time
ORDER BY avg_disp DESC;
```

### Query 3: Home Night Games vs Away Night Games
```sql
SELECT 
    player_name,
    location,
    game_time,
    COUNT(*) as games,
    ROUND(AVG(disposals), 1) as avg_disp
FROM vw_complete_game_stats
WHERE player_name = 'Scott Pendlebury'
  AND game_time = 'Night'
GROUP BY player_name, location, game_time;
```

### Query 4: Complex Multi-Filter Query
```sql
-- Pendlebury in night games at MCG vs Carlton when playing at home
SELECT 
    COUNT(*) as games,
    ROUND(AVG(disposals), 1) as avg_disp,
    ROUND(100.0 * SUM(CASE WHEN disposals >= 30 THEN 1 ELSE 0 END) / COUNT(*), 1) as pct_30_plus
FROM vw_complete_game_stats
WHERE player_name = 'Scott Pendlebury'
  AND venue_name = 'MCG'
  AND opponent_name = 'Carlton'
  AND location = 'Home'
  AND game_time = 'Night';
```

**All these filters use indexes = INSTANT results!** ⚡

---

## Data Entry Changes

### When adding new player stats:

```sql
-- Now include game_time
INSERT INTO player_game_stats (
    player_id, game_id, team_id, opponent_team_id, venue_id, 
    location, game_time,  -- NEW!
    disposals, goals
) VALUES (
    1, 100, 1, 4, 1, 
    'Home', 'Night',  -- Specify Day, Twilight, or Night
    32, 1
);
```

### When adding new players:

```sql
-- Use debut_year instead of debut_date
INSERT INTO players (player_name, first_name, last_name, debut_year)
VALUES ('Nick Daicos', 'Nick', 'Daicos', 2022);  -- Just the year!
```

### When adding new teams:

```sql
-- Super simple now
INSERT INTO teams (team_name) VALUES ('Tasmania');
```

---

## Benefits Summary

### 1. Simpler Data Entry
- Less fields to populate
- Fewer chances for errors
- Faster to add new records

### 2. Cleaner Database
- No redundant information
- Only essential data stored
- Easier to understand structure

### 3. New Analysis Power
- **Game time analysis** - Understand day/twilight/night performance differences
- Still all the speed from previous optimizations
- Can combine game_time with all other filters

### 4. Still Fast
- All indexes still in place
- Direct access to venue, opponent still works
- New game_time index added for speed

---

## Database Statistics

**Current table structure:**

| Table | Fields | Complexity |
|-------|--------|------------|
| players | 8 | Minimal |
| teams | 4 | Minimal |
| venues | 3 | Minimal |
| games | 11 | Streamlined |
| player_game_stats | 13 | Optimized |
| player_team_history | 6 | Minimal |

**Total:** 6 tables, perfectly balanced for speed and simplicity!

---

## What You Can Analyze Now

✅ **Player performance metrics** (disposals, goals)  
✅ **Home vs Away** comparisons  
✅ **Venue-specific** performance  
✅ **Opponent-specific** performance  
✅ **Rest days** impact (days since last game)  
✅ **Game type** (Pre-Season, Regular, Finals)  
✅ **Season trends** over years  
✅ **Game time** performance (Day/Twilight/Night) ⭐ NEW!  
✅ **Combined filters** - Mix any of the above!  

---

## Testing Results ✅

All queries tested and working perfectly:

```bash
✅ Player queries work
✅ Game time filtering works
✅ Multi-filter combinations work
✅ Percentage calculations work
✅ Aggregations work
✅ View works perfectly
✅ Indexes being used
✅ Check constraints enforced
```

---

## Migration Notes

If you have existing data:
1. Convert `debut_date` to `debut_year` (extract year from date)
2. Drop `team_abbrev`, `team_nickname`, `founded_year` columns
3. Drop `round_name` from games
4. Add `game_time` to player_game_stats
5. Populate game_time based on your time boundaries

Or just use the new schema from scratch! ✨

---

## Bottom Line

We made the database:
1. **Even simpler** - Removed unnecessary fields
2. **More powerful** - Added game time analysis
3. **Still fast** - All optimizations intact
4. **Easier to use** - Less data to manage

**Perfect for your AFL betting analysis needs!** 🎯🏈

