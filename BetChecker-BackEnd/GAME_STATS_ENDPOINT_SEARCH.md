# Game Player Statistics Endpoint Search

## Documentation Says

**Location**: "games > players statistics"  
**Parameters**: 
- `id` - The id of the game (integer)
- `ids` - Maximum of 10 games ids (string, format: "id-id-id")
- `date` - A valid date (string, format: "YYYY-MM-DD")
- `timezone` - A valid timezone (string, optional)

**Update Frequency**: Every 30 seconds

## What We've Tested

### ❌ Endpoints That Don't Exist
- `/games-players-statistics`
- `/games_players_statistics`
- `/games/players-statistics`
- `/games/players/statistics`
- `/games-players/statistics`
- `/players-statistics-games`
- `/players/games-statistics`
- `/players/games/statistics`
- `/games/{id}/players/statistics`
- `/games/{id}/players-statistics`

### ⚠️ Endpoints That Exist But Wrong Parameters
- `/players/statistics` - Exists but `id` parameter refers to player ID, not game ID
- `/players/statistics` with `game` parameter - Parameter doesn't exist
- `/players/statistics` with `games` parameter - Parameter doesn't exist

### ✅ What We Know Works
- `/players/statistics?id={player_id}&season={year}` - Returns season aggregates for a player
- `/games?season={year}&league=1` - Returns games
- `/players?team={team_id}&season={year}` - Returns players

## Questions

1. **What is the exact endpoint URL?**
   - The documentation says "games > players statistics" but what's the actual URL?
   - Is it `/games-players-statistics`? `/games/players-statistics`? Something else?

2. **Does it require a paid plan?**
   - The `ids` parameter on `/players/statistics` requires paid plan
   - Maybe this endpoint also requires paid plan?

3. **Is there a different base URL?**
   - Maybe it's on a different API version or base URL?

## Next Steps

**Please check the PDF documentation and provide:**
1. The exact endpoint URL/path
2. Any example requests shown
3. Whether it requires a specific API plan/tier
4. Any additional parameters or requirements

Once we have the exact endpoint, we can test it and integrate it into our scraper!

