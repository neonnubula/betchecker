# API ID Implementation Guide

## Overview

We've updated the system to use API-Sports.io player IDs and game IDs as primary identifiers. This solves the duplicate name problem without requiring date of birth.

## Changes Made

### 1. Database Schema Updates

**Migration Script**: `BetChecker-PlayerDatabase/add_api_ids_migration.sql`

Adds:
- `api_player_id` to `players` table (UNIQUE)
- `api_game_id` to `games` table (UNIQUE)
- Indexes for fast lookups

**To apply:**
```bash
cd BetChecker-BackEnd/BetChecker-PlayerDatabase
sqlite3 afl_stats.db < add_api_ids_migration.sql
```

### 2. Updated Database Manager

**New File**: `database/db_manager_api.py`

**Key Changes:**
- `get_or_create_player()` now requires `api_player_id` parameter
- Uses API ID as primary identifier (not name + DOB)
- Warns if same name found with different API ID (potential duplicate)

**Usage:**
```python
from database.db_manager_api import DatabaseManager

db = DatabaseManager('BetChecker-PlayerDatabase/afl_stats.db')

# Create/get player using API ID
player_id = db.get_or_create_player(
    player_name="Scott Pendlebury",
    api_player_id=156,  # ⭐ Required - from API
    date_of_birth=None,  # Optional - can add later if available
    debut_year=2006
)
```

### 3. Duplicate Detection Test

**New File**: `scripts/test_duplicate_players.py`

**Purpose**: Find players with same name but different API IDs for manual review.

**To run:**
```bash
cd BetChecker-BackEnd
python scripts/test_duplicate_players.py
```

**Output:**
- Lists all players with same name but different API IDs
- Shows which teams they played for
- Shows game date ranges
- Helps determine if they're the same person or different people

### 4. SQL Queries for Manual Review

**File**: `BetChecker-PlayerDatabase/find_potential_duplicates.sql`

Contains SQL queries to:
- Find same name, different API IDs
- Find same API ID, different names (shouldn't happen)
- Get detailed comparison data

## How It Works

### Player Identification Flow

1. **API provides**: `{id: 156, name: "Scott Pendlebury"}`
2. **We check**: Does `api_player_id = 156` exist in database?
3. **If yes**: Return existing `player_id`
4. **If no**: Create new player with `api_player_id = 156`
5. **If name matches but API ID different**: Warn and create new (for manual review)

### Handling Duplicates

**Scenario**: Two players named "Josh Smith" with different API IDs

**What happens:**
1. First "Josh Smith" (API ID 100) → Creates player record
2. Second "Josh Smith" (API ID 200) → Creates separate player record
3. Test script flags this as potential duplicate
4. Manual review determines if they're the same person
5. If same: Merge records (update stats, delete duplicate)
6. If different: No action needed (legitimate duplicates)

## Benefits

✅ **No DOB required** - Works with API data as-is
✅ **Stable identifiers** - API IDs persist across seasons
✅ **Fast lookups** - Direct ID matching vs name + DOB parsing
✅ **Duplicate detection** - Easy to find cases needing review
✅ **Manual control** - You decide which duplicates to merge

## Migration Steps

### Step 1: Apply Database Migration
```bash
cd BetChecker-BackEnd/BetChecker-PlayerDatabase
sqlite3 afl_stats.db < add_api_ids_migration.sql
```

### Step 2: Update Existing Code
Replace imports:
```python
# Old
from database.db_manager import DatabaseManager

# New
from database.db_manager_api import DatabaseManager
```

Update player creation calls:
```python
# Old
player_id = db.get_or_create_player(
    player_name="Scott Pendlebury",
    date_of_birth=date(1988, 1, 7)
)

# New
player_id = db.get_or_create_player(
    player_name="Scott Pendlebury",
    api_player_id=156  # ⭐ Required
)
```

### Step 3: Test Duplicate Detection
```bash
python scripts/test_duplicate_players.py
```

## Example: Scraping Players from API

```python
from database.db_manager_api import DatabaseManager
import requests

db = DatabaseManager('BetChecker-PlayerDatabase/afl_stats.db')

# API call
response = requests.get(
    'https://v1.afl.api-sports.io/players',
    headers={'x-rapidapi-key': 'YOUR_KEY'},
    params={'team': 4, 'season': 2023}
)

players = response.json()['response']

for player_data in players:
    player_id = db.get_or_create_player(
        player_name=player_data['name'],
        api_player_id=player_data['id']  # ⭐ Use API ID
    )
    print(f"Player: {player_data['name']} → ID: {player_id}")
```

## Manual Duplicate Review Process

### When Test Finds Duplicates

1. **Run test**: `python scripts/test_duplicate_players.py`

2. **Review each case**:
   - Check if API IDs refer to same person
   - Look at teams they played for
   - Check game date ranges (overlapping = different people)

3. **If same person** (rare):
   ```sql
   -- Keep player_id with more games, merge the other
   UPDATE player_game_stats SET player_id = <keep_id> WHERE player_id = <duplicate_id>;
   UPDATE player_team_history SET player_id = <keep_id> WHERE player_id = <duplicate_id>;
   DELETE FROM players WHERE player_id = <duplicate_id>;
   ```

4. **If different people** (common):
   - No action needed
   - They're legitimately different people with same name

## Validation

### Test 1: No Duplicate API IDs
```sql
SELECT api_player_id, COUNT(*) 
FROM players 
WHERE api_player_id IS NOT NULL
GROUP BY api_player_id 
HAVING COUNT(*) > 1;
```
**Expected**: 0 rows

### Test 2: Potential Duplicates (Manual Review)
```bash
python scripts/test_duplicate_players.py
```
**Expected**: 0 rows ideally, but manual review if found

### Test 3: All Players Have API IDs
```sql
SELECT COUNT(*) 
FROM players 
WHERE api_player_id IS NULL;
```
**Expected**: 0 rows (after scraping from API)

## Next Steps

1. ✅ Apply migration script
2. ✅ Update scrapers to use `db_manager_api.py`
3. ✅ Scrape sample data
4. ✅ Run duplicate detection test
5. ✅ Review any duplicates found
6. ✅ Scale up to full dataset

## Summary

- **Primary Identifier**: API player ID (not name + DOB)
- **Duplicate Handling**: Manual review of same-name cases
- **Benefits**: Works with API data, stable IDs, fast lookups
- **Trade-off**: Occasional manual review needed (should be rare)

This approach is practical and works with the API data we actually have!

