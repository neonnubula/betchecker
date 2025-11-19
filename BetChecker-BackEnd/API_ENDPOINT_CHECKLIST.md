# API Endpoint Checklist

## ✅ Endpoints We've Confirmed Work

### API-Sports Base URL: `https://v1.afl.api-sports.io`

1. **Teams**: `GET /teams`
   - Returns: All 18 teams with IDs, names, logos
   - Requests: 1 (one-time)

2. **Players**: `GET /players`
   - Parameters: `team` + `season` OR `id` OR `name` + `season`
   - Returns: Player ID and name
   - Requests: ~18 per season (one per team)

3. **Games**: `GET /games`
   - Parameters: `season` + `league` (league=1 for AFL)
   - Returns: Complete game data (date, venue, teams, scores)
   - Requests: 1 per season

4. **Player Statistics (Season)**: `GET /players/statistics`
   - Parameters: `id` (player_id) + `season`
   - Returns: Season aggregates (totals and averages)
   - Requests: 1 per player per season
   - ⚠️ **Not per-game stats**

### RapidAPI Base URL: `https://api-afl.p.rapidapi.com`
- Headers: `X-RapidAPI-Key` and `X-RapidAPI-Host: api-afl.p.rapidapi.com`
- **Not tested yet** - may have different endpoints

## ❓ Endpoint We Need to Find

### Game Player Statistics (Per-Game)
**Documentation says**: "games > players statistics"
**Parameters**: `id` (game id), `ids` (multiple), `date`
**What we need**: Per-game player statistics

**Tested (not found)**:
- `/games-players-statistics` ❌
- `/games/players-statistics` ❌ (404 on RapidAPI)
- `/games/players/statistics` ❌
- Various parameter combinations ❌

## 📋 What to Check in PDF

Please look for:
1. **Exact endpoint path** - What's the URL?
2. **Which base URL** - RapidAPI or API-Sports?
3. **Example request** - Any curl examples?
4. **Response structure** - What does it return?
5. **Plan requirements** - Free plan or paid?

## 💡 Current Status

**We can scrape**:
- ✅ Teams (complete)
- ✅ Players (IDs and names)
- ✅ Games (complete game data)
- ✅ Season player statistics (aggregates)

**We cannot scrape yet**:
- ❌ Per-game player statistics (need exact endpoint)

**Daily Request Budget** (100 requests):
- Teams: 1 (one-time)
- Players: 18 per season
- Games: 1 per season
- **Remaining: ~80 for statistics**

Once we find the game statistics endpoint, we can plan how to use those 80 requests efficiently!

