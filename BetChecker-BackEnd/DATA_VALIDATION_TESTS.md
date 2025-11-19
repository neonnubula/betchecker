# Data Validation Tests

This document provides SQL queries and Python scripts to validate data quality, detect duplicates, and test edge cases as you scrape from different sources.

## Purpose

Use these tests to:
- **Evaluate data sources**: Compare quality across different websites
- **Detect data issues**: Find duplicates, missing data, inconsistencies
- **Validate scraping logic**: Ensure your scrapers handle edge cases correctly
- **Monitor data quality**: Run periodically to catch issues early

---

## Test 1: Duplicate Players (Same API ID) ⭐ UPDATED

### What It Tests
Detects if the same API player ID was inserted multiple times. This should NEVER happen - each API ID should map to one player record.

### SQL Query
```sql
-- Find duplicate API player IDs
SELECT 
    api_player_id,
    COUNT(*) as duplicate_count,
    GROUP_CONCAT(player_id) as player_ids,
    GROUP_CONCAT(player_name) as names
FROM players
WHERE api_player_id IS NOT NULL
GROUP BY api_player_id
HAVING COUNT(*) > 1
ORDER BY duplicate_count DESC;
```

### Expected Result
**Should return 0 rows** - Each API ID should be unique

### If Issues Found
- Check if unique constraint was applied: `SELECT name FROM sqlite_master WHERE type='index' AND name='idx_players_api_id';`
- Review scraper logic - should check for existing api_player_id before inserting

---

## Test 1b: Duplicate Players (Same Name + DOB) - Legacy Test

### What It Tests
Detects if the same player (same name + DOB) was inserted multiple times. This should NEVER happen if the unique constraint is working.

### SQL Query
```sql
-- Find duplicate players with same name AND DOB
SELECT 
    player_name,
    date_of_birth,
    COUNT(*) as duplicate_count,
    GROUP_CONCAT(player_id) as player_ids
FROM players
WHERE date_of_birth IS NOT NULL
GROUP BY player_name, date_of_birth
HAVING COUNT(*) > 1
ORDER BY duplicate_count DESC;
```

### Expected Result
**Should return 0 rows** - No duplicates allowed

### If Issues Found
- Check if unique constraint was applied: `SELECT name FROM sqlite_master WHERE type='index' AND name='idx_player_name_dob';`
- Review scraper logic - should use `get_or_create_player()` not `insert()`

---

## Test 2: Potential Duplicate Players (Same Name, Different API IDs) ⭐ NEW

### What It Tests
Finds players with the same name but different API player IDs. These need manual review to determine if they're actually the same person or different people with the same name.

### SQL Query
```sql
-- Find players with same name but different API IDs
SELECT 
    player_name,
    COUNT(DISTINCT api_player_id) as different_api_ids,
    COUNT(*) as total_records,
    GROUP_CONCAT(DISTINCT api_player_id) as api_ids,
    GROUP_CONCAT(DISTINCT player_id) as our_ids,
    GROUP_CONCAT(DISTINCT date_of_birth) as birth_dates
FROM players
WHERE api_player_id IS NOT NULL
GROUP BY player_name
HAVING COUNT(DISTINCT api_player_id) > 1
ORDER BY different_api_ids DESC, player_name;
```

### Expected Result
**Should return 0 rows ideally** - But if found, these are candidates for manual review

### If Issues Found
- **Review manually** - Check if API IDs refer to same person
- **If same person**: Merge records (keep one player_id, update all stats to point to it)
- **If different people**: No action needed (legitimate duplicates)

### Python Test Script
```bash
python scripts/test_duplicate_players.py
```

### Manual Review Process
1. For each duplicate case, check:
   - Do the API IDs refer to the same person?
   - Check teams they played for (same teams = likely same person)
   - Check game date ranges (overlapping = likely different people)
2. If same person:
   ```sql
   -- Merge: Update all stats to point to one player_id
   UPDATE player_game_stats SET player_id = <keep_id> WHERE player_id = <duplicate_id>;
   -- Delete duplicate
   DELETE FROM players WHERE player_id = <duplicate_id>;
   ```
3. If different people: No action needed

---

## Test 2: Same Name, Different DOB (Valid Duplicates)

### What It Tests
Verifies that players with the same name but different DOB are correctly stored as separate players. This is EXPECTED and CORRECT.

### SQL Query
```sql
-- Find players with same name but different DOB
SELECT 
    player_name,
    COUNT(DISTINCT date_of_birth) as different_dobs,
    COUNT(*) as total_players,
    GROUP_CONCAT(DISTINCT date_of_birth) as birth_dates,
    GROUP_CONCAT(player_id) as player_ids
FROM players
WHERE date_of_birth IS NOT NULL
GROUP BY player_name
HAVING COUNT(DISTINCT date_of_birth) > 1
ORDER BY different_dobs DESC, player_name;
```

### Expected Result
**Should return rows** - These are valid duplicates (different people, same name)

### Example Output
```
player_name    | different_dobs | total_players | birth_dates           | player_ids
Josh Smith     | 2              | 2            | 1990-01-15,1992-03-20 | 45, 123
```

### Validation
- Check that each `player_id` has different `date_of_birth`
- Verify these are actually different people (check their teams/games)

---

## Test 3: Same Name, Missing DOB (Potential Issues)

### What It Tests
Finds players with same name but NULL DOB. These are risky because we can't distinguish if they're the same person or different people.

### SQL Query
```sql
-- Find players with same name but NULL DOB
SELECT 
    player_name,
    COUNT(*) as count_without_dob,
    GROUP_CONCAT(player_id) as player_ids,
    GROUP_CONCAT(debut_year) as debut_years
FROM players
WHERE date_of_birth IS NULL
GROUP BY player_name
HAVING COUNT(*) > 1
ORDER BY count_without_dob DESC;
```

### Expected Result
**Ideally 0 rows** - All players should have DOB

### If Issues Found
- These need manual review
- Try to find DOB from other sources
- Consider using `debut_year` as additional identifier if DOB unavailable

---

## Test 4: Player Name Variations (Potential Duplicates)

### What It Tests
Finds players with similar names that might be the same person (e.g., "Scott Pendlebury" vs "S. Pendlebury" vs "S Pendlebury").

### SQL Query
```sql
-- Find potential name variations
-- This uses SQLite's LIKE operator for pattern matching
SELECT 
    p1.player_id as id1,
    p1.player_name as name1,
    p1.date_of_birth as dob1,
    p2.player_id as id2,
    p2.player_name as name2,
    p2.date_of_birth as dob2
FROM players p1
JOIN players p2 ON p1.player_id < p2.player_id
WHERE 
    -- Same last name
    p1.last_name = p2.last_name
    AND p1.last_name IS NOT NULL
    -- First name starts with same letter (potential abbreviation)
    AND (
        SUBSTR(p1.first_name, 1, 1) = SUBSTR(p2.first_name, 1, 1)
        OR p1.first_name LIKE SUBSTR(p2.first_name, 1, 1) || '.%'
        OR p2.first_name LIKE SUBSTR(p1.first_name, 1, 1) || '.%'
    )
    -- Different player_id (not same record)
    AND (
        -- Same DOB (likely same person)
        (p1.date_of_birth = p2.date_of_birth AND p1.date_of_birth IS NOT NULL)
        -- OR both missing DOB (need manual check)
        OR (p1.date_of_birth IS NULL AND p2.date_of_birth IS NULL)
    )
ORDER BY p1.last_name, p1.first_name;
```

### Expected Result
**Review manually** - These might be the same person with name variations

### Manual Validation Steps
1. Check if DOB matches (if both have DOB)
2. Check if they played for same teams
3. Check if game dates overlap (same person can't play for two teams simultaneously)
4. If same person: Keep one, merge stats, delete duplicate

---

## Test 5: Players Without DOB

### What It Tests
Counts how many players are missing DOB. Lower is better.

### SQL Query
```sql
-- Count players without DOB
SELECT 
    COUNT(*) as players_without_dob,
    ROUND(100.0 * COUNT(*) / (SELECT COUNT(*) FROM players), 2) as percentage
FROM players
WHERE date_of_birth IS NULL;
```

### Expected Result
**As low as possible** - Ideally < 5% of players

### Quality Thresholds
- **Excellent**: < 1% missing DOB
- **Good**: < 5% missing DOB
- **Acceptable**: < 10% missing DOB
- **Poor**: > 10% missing DOB (need better data source)

---

## Test 6: Players Without Games (Orphaned Players)

### What It Tests
Finds players that were added but have no game stats. Might indicate scraper issues.

### SQL Query
```sql
-- Find players with no game stats
SELECT 
    p.player_id,
    p.player_name,
    p.date_of_birth,
    p.debut_year,
    COUNT(pgs.stat_id) as game_count
FROM players p
LEFT JOIN player_game_stats pgs ON p.player_id = pgs.player_id
GROUP BY p.player_id
HAVING game_count = 0
ORDER BY p.player_name;
```

### Expected Result
**Review manually** - Might be legitimate (newly added player) or scraper issue

---

## Test 7: Duplicate Game Stats (Same Player, Same Game)

### What It Tests
Detects if the same player has multiple stat entries for the same game. This violates the UNIQUE constraint.

### SQL Query
```sql
-- Find duplicate stats (same player, same game)
SELECT 
    player_id,
    game_id,
    COUNT(*) as duplicate_count,
    GROUP_CONCAT(stat_id) as stat_ids
FROM player_game_stats
GROUP BY player_id, game_id
HAVING COUNT(*) > 1;
```

### Expected Result
**Should return 0 rows** - UNIQUE constraint prevents this

### If Issues Found
- Database constraint might be missing
- Scraper might be inserting without checking
- Fix: Add `UNIQUE(player_id, game_id)` constraint

---

## Test 8: Team Assignment Validation

### What It Tests
Verifies that each player's team_id matches either the home_team or away_team for that game.

### SQL Query
```sql
-- Find stats where player's team doesn't match game teams
SELECT 
    pgs.stat_id,
    p.player_name,
    g.game_date,
    pgs.team_id as player_team_id,
    t.team_name as player_team_name,
    g.home_team_id,
    ht.team_name as home_team_name,
    g.away_team_id,
    at.team_name as away_team_name
FROM player_game_stats pgs
JOIN players p ON pgs.player_id = p.player_id
JOIN games g ON pgs.game_id = g.game_id
JOIN teams t ON pgs.team_id = t.team_id
JOIN teams ht ON g.home_team_id = ht.team_id
JOIN teams at ON g.away_team_id = at.team_id
WHERE pgs.team_id NOT IN (g.home_team_id, g.away_team_id);
```

### Expected Result
**Should return 0 rows** - Player must be on one of the two teams

### If Issues Found
- Scraper logic error in team assignment
- Data source has incorrect team information
- Fix: Review team assignment logic in scraper

---

## Test 9: Opponent Team Validation

### What It Tests
Verifies that opponent_team_id is the OTHER team (not the player's own team).

### SQL Query
```sql
-- Find stats where opponent is same as player's team
SELECT 
    pgs.stat_id,
    p.player_name,
    g.game_date,
    pgs.team_id as player_team_id,
    t.team_name as player_team_name,
    pgs.opponent_team_id,
    ot.team_name as opponent_team_name
FROM player_game_stats pgs
JOIN players p ON pgs.player_id = p.player_id
JOIN games g ON pgs.game_id = g.game_id
JOIN teams t ON pgs.team_id = t.team_id
JOIN teams ot ON pgs.opponent_team_id = ot.team_id
WHERE pgs.team_id = pgs.opponent_team_id;
```

### Expected Result
**Should return 0 rows** - Player can't play against their own team

### If Issues Found
- Scraper logic error in opponent assignment
- Fix: Ensure opponent is the OTHER team from the game

---

## Test 10: Venue Consistency

### What It Tests
Verifies that venue_id in player_game_stats matches venue_id in games table.

### SQL Query
```sql
-- Find stats where venue doesn't match game venue
SELECT 
    pgs.stat_id,
    p.player_name,
    g.game_date,
    pgs.venue_id as stat_venue_id,
    v1.venue_name as stat_venue_name,
    g.venue_id as game_venue_id,
    v2.venue_name as game_venue_name
FROM player_game_stats pgs
JOIN players p ON pgs.player_id = p.player_id
JOIN games g ON pgs.game_id = g.game_id
JOIN venues v1 ON pgs.venue_id = v1.venue_id
JOIN venues v2 ON g.venue_id = v2.venue_id
WHERE pgs.venue_id != g.venue_id;
```

### Expected Result
**Should return 0 rows** - Venue should match (it's the same game)

### If Issues Found
- Data inconsistency
- Fix: Use venue from games table, don't duplicate in stats

---

## Test 11: Team History Validation

### What It Tests
Checks that team history entries are valid (no overlapping dates, proper start/end dates).

### SQL Query
```sql
-- Find overlapping team history entries for same player
SELECT 
    pth1.history_id as id1,
    pth1.player_id,
    p.player_name,
    pth1.team_id as team1_id,
    t1.team_name as team1_name,
    pth1.start_date as start1,
    pth1.end_date as end1,
    pth2.history_id as id2,
    pth2.team_id as team2_id,
    t2.team_name as team2_name,
    pth2.start_date as start2,
    pth2.end_date as end2
FROM player_team_history pth1
JOIN player_team_history pth2 ON pth1.player_id = pth2.player_id
JOIN players p ON pth1.player_id = p.player_id
JOIN teams t1 ON pth1.team_id = t1.team_id
JOIN teams t2 ON pth2.team_id = t2.team_id
WHERE pth1.history_id < pth2.history_id
AND (
    -- Overlapping dates
    (pth1.start_date <= COALESCE(pth2.end_date, '9999-12-31')
     AND COALESCE(pth1.end_date, '9999-12-31') >= pth2.start_date)
);
```

### Expected Result
**Should return 0 rows** - No overlapping team assignments

### If Issues Found
- Team change detection logic error
- Fix: Review team history update logic

---

## Test 12: Multiple Current Teams

### What It Tests
Finds players with multiple "current" team assignments (should only have one).

### SQL Query
```sql
-- Find players with multiple current teams
SELECT 
    player_id,
    p.player_name,
    COUNT(*) as current_team_count,
    GROUP_CONCAT(team_id) as team_ids,
    GROUP_CONCAT(t.team_name) as team_names
FROM player_team_history pth
JOIN players p ON pth.player_id = p.player_id
JOIN teams t ON pth.team_id = t.team_id
WHERE is_current = 1
GROUP BY player_id
HAVING COUNT(*) > 1;
```

### Expected Result
**Should return 0 rows** - Player can only have one current team

### If Issues Found
- Team history update logic error
- Fix: Ensure only one `is_current = 1` per player

---

## Test 13: Data Completeness Score

### What It Tests
Overall data quality metrics to compare across data sources.

### SQL Query
```sql
-- Data completeness report
SELECT 
    'Players' as metric,
    COUNT(*) as total,
    COUNT(date_of_birth) as with_dob,
    ROUND(100.0 * COUNT(date_of_birth) / COUNT(*), 2) as completeness_pct
FROM players

UNION ALL

SELECT 
    'Games' as metric,
    COUNT(*) as total,
    COUNT(game_time) as with_time,
    ROUND(100.0 * COUNT(game_time) / COUNT(*), 2) as completeness_pct
FROM games

UNION ALL

SELECT 
    'Player Stats' as metric,
    COUNT(*) as total,
    COUNT(days_since_last_game) as with_rest_days,
    ROUND(100.0 * COUNT(days_since_last_game) / COUNT(*), 2) as completeness_pct
FROM player_game_stats;
```

### Expected Result
**Higher percentages = better data quality**

### Quality Thresholds
- **DOB completeness**: > 95% = Excellent, > 90% = Good, < 90% = Needs improvement
- **Game time completeness**: > 80% = Good
- **Rest days completeness**: > 90% = Good (calculated field)

---

## Test 14: Statistical Outliers (Data Sanity Checks)

### What It Tests
Finds unrealistic stat values that might indicate scraping errors.

### SQL Query
```sql
-- Find unrealistic stat values
SELECT 
    p.player_name,
    g.game_date,
    pgs.disposals,
    pgs.goals,
    CASE 
        WHEN pgs.disposals > 50 THEN 'High disposals'
        WHEN pgs.goals > 10 THEN 'High goals'
        WHEN pgs.disposals < 0 THEN 'Negative disposals'
        WHEN pgs.goals < 0 THEN 'Negative goals'
    END as issue_type
FROM player_game_stats pgs
JOIN players p ON pgs.player_id = p.player_id
JOIN games g ON pgs.game_id = g.game_id
WHERE 
    pgs.disposals > 50  -- Very high (possible but rare)
    OR pgs.goals > 10    -- Very high (possible but rare)
    OR pgs.disposals < 0 -- Invalid
    OR pgs.goals < 0     -- Invalid
ORDER BY issue_type, pgs.disposals DESC, pgs.goals DESC;
```

### Expected Result
**Review manually** - Some might be legitimate records (except negatives)

### Validation
- Check if high values are real (look up game results)
- Negative values are always errors

---

## Test 15: Game Date Consistency

### What It Tests
Verifies that game dates are reasonable (not in future, not too old).

### SQL Query
```sql
-- Find games with suspicious dates
SELECT 
    game_id,
    game_date,
    season_year,
    round_number,
    CASE 
        WHEN game_date > DATE('now') THEN 'Future date'
        WHEN game_date < '2000-01-01' THEN 'Very old date'
        WHEN CAST(strftime('%Y', game_date) AS INTEGER) != season_year THEN 'Year mismatch'
    END as issue_type
FROM games
WHERE 
    game_date > DATE('now')
    OR game_date < '2000-01-01'
    OR CAST(strftime('%Y', game_date) AS INTEGER) != season_year
ORDER BY game_date DESC;
```

### Expected Result
**Should return 0 rows** (or only legitimate old games)

---

## Python Test Script

Create `BetChecker-BackEnd/scripts/run_validation_tests.py`:

```python
#!/usr/bin/env python3
"""
Run all data validation tests and generate a report.
"""

import sqlite3
import sys
from pathlib import Path

# Add parent directory to path
sys.path.insert(0, str(Path(__file__).parent.parent))

class ValidationTester:
    def __init__(self, db_path: str):
        self.db_path = db_path
        self.conn = sqlite3.connect(db_path)
        self.conn.row_factory = sqlite3.Row
        self.results = []
    
    def run_test(self, test_name: str, query: str, expected: str):
        """Run a test and record results"""
        try:
            cursor = self.conn.execute(query)
            rows = cursor.fetchall()
            passed = len(rows) == 0 if expected == "0 rows" else True
            
            self.results.append({
                'test': test_name,
                'passed': passed,
                'row_count': len(rows),
                'expected': expected,
                'sample_rows': rows[:3]  # First 3 rows for inspection
            })
        except Exception as e:
            self.results.append({
                'test': test_name,
                'passed': False,
                'error': str(e)
            })
    
    def run_all_tests(self):
        """Run all validation tests"""
        
        # Test 1: Duplicate players (same name + DOB)
        self.run_test(
            "Duplicate Players (Same Name + DOB)",
            """
            SELECT player_name, date_of_birth, COUNT(*) as count
            FROM players
            WHERE date_of_birth IS NOT NULL
            GROUP BY player_name, date_of_birth
            HAVING COUNT(*) > 1
            """,
            "0 rows"
        )
        
        # Test 2: Duplicate game stats
        self.run_test(
            "Duplicate Game Stats",
            """
            SELECT player_id, game_id, COUNT(*) as count
            FROM player_game_stats
            GROUP BY player_id, game_id
            HAVING COUNT(*) > 1
            """,
            "0 rows"
        )
        
        # Test 3: Team assignment validation
        self.run_test(
            "Invalid Team Assignments",
            """
            SELECT pgs.stat_id
            FROM player_game_stats pgs
            JOIN games g ON pgs.game_id = g.game_id
            WHERE pgs.team_id NOT IN (g.home_team_id, g.away_team_id)
            """,
            "0 rows"
        )
        
        # Test 4: Opponent validation
        self.run_test(
            "Invalid Opponent Teams",
            """
            SELECT stat_id
            FROM player_game_stats
            WHERE team_id = opponent_team_id
            """,
            "0 rows"
        )
        
        # Test 5: Multiple current teams
        self.run_test(
            "Multiple Current Teams",
            """
            SELECT player_id, COUNT(*) as count
            FROM player_team_history
            WHERE is_current = 1
            GROUP BY player_id
            HAVING COUNT(*) > 1
            """,
            "0 rows"
        )
        
        # Test 6: Players without DOB (count only)
        cursor = self.conn.execute("""
            SELECT COUNT(*) as count
            FROM players
            WHERE date_of_birth IS NULL
        """)
        missing_dob = cursor.fetchone()['count']
        self.results.append({
            'test': "Players Without DOB",
            'passed': missing_dob < 100,  # Adjust threshold
            'row_count': missing_dob,
            'expected': "< 100 players"
        })
    
    def print_report(self):
        """Print test results report"""
        print("=" * 80)
        print("DATA VALIDATION TEST REPORT")
        print("=" * 80)
        print()
        
        passed = sum(1 for r in self.results if r.get('passed', False))
        total = len(self.results)
        
        for result in self.results:
            status = "✅ PASS" if result.get('passed', False) else "❌ FAIL"
            print(f"{status} - {result['test']}")
            
            if 'error' in result:
                print(f"   Error: {result['error']}")
            elif 'row_count' in result:
                print(f"   Found: {result['row_count']} rows (Expected: {result['expected']})")
                if result['row_count'] > 0 and result.get('sample_rows'):
                    print("   Sample rows:")
                    for row in result['sample_rows']:
                        print(f"     {dict(row)}")
            print()
        
        print("=" * 80)
        print(f"Summary: {passed}/{total} tests passed")
        print("=" * 80)
    
    def close(self):
        self.conn.close()

if __name__ == "__main__":
    db_path = "BetChecker-PlayerDatabase/afl_stats.db"
    
    if not Path(db_path).exists():
        print(f"Error: Database not found at {db_path}")
        sys.exit(1)
    
    tester = ValidationTester(db_path)
    tester.run_all_tests()
    tester.print_report()
    tester.close()
```

---

## Usage Instructions

### Run Individual Tests
```bash
cd BetChecker-BackEnd/BetChecker-PlayerDatabase
sqlite3 afl_stats.db < test_query.sql
```

### Run All Tests (Python)
```bash
cd BetChecker-BackEnd
python scripts/run_validation_tests.py
```

### Compare Data Sources
1. Scrape sample data from Source A
2. Run validation tests → Record results
3. Clear database
4. Scrape same sample from Source B
5. Run validation tests → Compare results
6. Choose source with better quality scores

---

## Quality Scoring System

Rate each data source on:

| Test | Weight | Excellent | Good | Poor |
|------|--------|-----------|------|------|
| Duplicate Players | High | 0 | 0 | >0 |
| Missing DOB | High | <1% | <5% | >10% |
| Team Assignment Errors | High | 0 | 0 | >0 |
| Opponent Errors | Medium | 0 | 0 | >0 |
| Statistical Outliers | Medium | <1% | <5% | >10% |
| Data Completeness | Low | >95% | >90% | <90% |

**Scoring**: Excellent = 3 points, Good = 2 points, Poor = 1 point
**Total**: Weighted average across all tests

---

## Next Steps

1. **Before scraping**: Review this document, understand each test
2. **During scraping**: Run tests after each batch of data
3. **After scraping**: Run full validation suite
4. **Compare sources**: Use tests to evaluate which source is best
5. **Fix issues**: Address any failures before scaling up

