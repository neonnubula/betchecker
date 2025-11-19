# Schema Review & ETL Summary

## Do We Need to Change Our Schema?

### ✅ Already Compatible (via migrations)
- ✅ `players.api_player_id` - Added ✓
- ✅ `games.api_game_id` - Added ✓
- ✅ Teams can use API IDs directly as `team_id` (they match)

### 🤔 Optional Enhancement
- Consider adding `teams.api_team_id` for consistency (but not required since API IDs match our team_id)

### ❓ Decision: Additional Stats Fields

**Current Schema**: Only stores `disposals` and `goals`  
**API Provides**: disposals, goals, kicks, handballs, marks, tackles, clearances, hitouts, behinds, free_kicks, assists

**Recommendation**: 
- **Start with current schema** (disposals + goals only)
- **Add more stats later** if needed for analysis
- Reason: Simpler to start, can extend later

---

## ETL Plan Summary

### ✅ EXTRACT (Getting Data from API)

1. **Teams**: `GET /teams` → 1 request
2. **Seasons**: `GET /seasons` → 1 request (reference)
3. **Players**: `GET /players?team={id}&season={year}` → ~270 requests
4. **Games**: `GET /games?season={year}&league=1` → 15 requests
5. **Game Stats**: `GET /games/statistics/players?id={game_id}` → ~3,240 requests ⭐

### ✅ TRANSFORM (Mapping to Our Schema)

**Teams**:
- API `id` → Our `team_id` (direct match)
- API `name` → Our `team_name`

**Players**:
- API `id` → Our `api_player_id` (lookup/create)
- API `name` → Our `player_name`

**Venues**:
- Extract from games → Create by name

**Games**:
- API `game.id` → Our `api_game_id`
- API `league.season` → Our `season_year`
- API `week` → Our `round_number`
- API `round` → Our `game_type` ("Regular Season" or "Finals")
- Parse ISO date → Our `game_date`
- API `time` → Our `game_time`
- API `venue` → Lookup/create → Our `venue_id`
- API `teams.home.id` → Our `home_team_id`
- API `teams.away.id` → Our `away_team_id`

**Player Game Stats** ⭐:
- API `player.id` → Lookup → Our `player_id`
- API `game.id` → Lookup → Our `game_id`
- API `team.id` → Our `team_id`
- Calculate → Our `opponent_team_id` (other team in game)
- From game → Our `venue_id`
- Compare team_id to home/away → Our `location` ("Home" or "Away")
- Parse time → Our `game_time` ("Day", "Twilight", or "Night")
- API `disposals` → Our `disposals`
- API `goals.total` → Our `goals`

### ✅ LOAD (Inserting into Database)

**Strategy**:
1. Use `get_or_create` pattern for all entities
2. Check by API ID before inserting
3. Skip duplicates (idempotent)
4. Handle foreign key dependencies

**Order**:
1. Teams (no dependencies)
2. Players (no dependencies)
3. Games (needs teams, venues)
4. Game Statistics (needs games, players, teams)

---

## Key Transformations

### Date Parsing
```python
# API: "2023-03-16T19:20:00+00:00"
# Our: "2023-03-16" (DATE)
parse_date(iso_string) → date
```

### Game Type Parsing
```python
# API: "Regular Season" or "Finals"
# Our: "Regular Season" or "Finals" (same)
parse_game_type(round_text) → game_type
```

### Location Determination
```python
# Compare team_id to game's home_team_id/away_team_id
if team_id == home_team_id:
    return "Home"
else:
    return "Away"
```

### Game Time Classification
```python
# API: "19:20"
# Our: "Night" (based on hour)
if hour < 15: "Day"
elif hour < 18: "Twilight"
else: "Night"
```

---

## Schema Compatibility Check

### ✅ Fully Compatible
- Teams: Direct match ✓
- Players: API ID stored, name stored ✓
- Venues: Name-based lookup ✓
- Games: All fields mappable ✓
- Player Stats: Core fields (disposals, goals) available ✓

### ⚠️ Optional Enhancements
- Add more stats fields (kicks, marks, tackles, etc.) - **Not required for MVP**
- Add `teams.api_team_id` - **Not required** (can use team_id directly)

---

## Conclusion

**Schema Changes Needed**: ✅ **NONE** (already compatible!)

**ETL Plan**: ✅ **Complete** (Extract → Transform → Load all documented)

**Ready to Build**: ✅ **Yes** - Can start implementing scraper functions now!

---

## Next Steps

1. ✅ Schema review - **Complete** (no changes needed)
2. ✅ ETL plan - **Complete** (all transformations documented)
3. ⏭️ Build scraper functions
4. ⏭️ Test with sample data
5. ⏭️ Scale up to full dataset

