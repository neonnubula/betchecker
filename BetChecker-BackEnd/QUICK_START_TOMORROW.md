# Quick Start Guide - Tomorrow

## 🎯 Goal
Build scraper functions to populate database from API-Sports.io

---

## 📋 Pre-Flight Checklist

### 1. Database Setup
```bash
cd BetChecker-BackEnd/BetChecker-PlayerDatabase
sqlite3 afl_stats.db < add_api_ids_migration.sql
```

### 2. Verify Migration
```sql
-- Check columns exist
.schema players
.schema games
-- Should see api_player_id and api_game_id
```

### 3. Test Database Manager
```bash
cd BetChecker-BackEnd
python scripts/test_duplicate_players.py
```

---

## 🚀 First Steps Tomorrow

### Step 1: Create API Client
Create `scrapers/api_client.py`:
- Base URL: `https://v1.afl.api-sports.io`
- Headers: `x-rapidapi-key`, `x-rapidapi-host`
- Rate limiting: 6+ seconds between requests
- Error handling

### Step 2: Build Scraper Functions
Start with simple ones:
1. `scrape_teams()` - 1 request, no dependencies
2. `scrape_players(team_id, season)` - Test with one team
3. `scrape_games(season)` - Test with 2023
4. `scrape_game_statistics(game_id)` - Test with one game

### Step 3: Test Incrementally
- Test each function individually
- Verify data in database
- Run validation tests

---

## 📚 Key Files to Reference

**ETL Logic**: `ETL_PLAN.md`  
**Scraping Strategy**: `FULL_DATA_SCRAPING_PLAN.md`  
**API Endpoints**: `GAME_STATISTICS_ENDPOINT.md`  
**Database Manager**: `database/db_manager_api.py`  
**Schema**: `BetChecker-PlayerDatabase/schema.sql`

---

## 🔑 Key Points to Remember

1. **API IDs are primary identifiers** - Use for lookups
2. **Rate limit**: 100 requests/day, 10/minute
3. **Skip duplicates**: Check API IDs before inserting
4. **Start small**: Test with 2023 season first
5. **Idempotent**: Can re-run scrapers safely

---

## 📊 Request Budget

**Today's goal**: Test with sample data
- Teams: 1 request
- Players: ~18 requests (one team, one season)
- Games: 1 request (one season)
- Game Stats: ~1 request (one game)
- **Total**: ~21 requests (well under limit!)

---

## ✅ Success Criteria

After today, you should have:
- ✅ Teams table populated
- ✅ Sample players in database
- ✅ Sample games in database
- ✅ Sample player stats in database
- ✅ Validation tests passing

---

**Ready to go!** 🚀

