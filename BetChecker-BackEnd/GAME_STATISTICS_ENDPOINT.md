# Game Player Statistics Endpoint - FOUND! ✅

## Endpoint Details

**URL**: `GET /games/statistics/players`  
**Base URL**: `https://v1.afl.api-sports.io`  
**Headers**:
```
x-rapidapi-key: YOUR_API_KEY
x-rapidapi-host: v1.afl.api-sports.io
```

**Parameters**:
- `id` - Game ID (integer, required)
- `ids` - Multiple game IDs (string, format: "id-id-id", max 10, requires paid plan)
- `date` - Date filter (string, format: "YYYY-MM-DD")

**Documentation**: https://api-sports.io/documentation/afl/v1#tag/Games/operation/get-games-statistics-players

---

## Response Structure

```json
{
  "get": "games/statistics/players",
  "parameters": {"id": "2524"},
  "results": 1,
  "response": [
    {
      "game": {
        "id": 2524
      },
      "teams": [
        {
          "team": {
            "id": 3
          },
          "players": [
            {
              "player": {
                "id": 7,
                "number": 35
              },
              "goals": {
                "total": 0,
                "assists": 2
              },
              "behinds": 0,
              "disposals": 14,
              "kicks": 12,
              "handballs": 2,
              "marks": 6,
              "tackles": 4,
              "hitouts": 0,
              "clearances": 1,
              "free_kicks": {
                "for": 0,
                "against": 0
              }
            }
            // ... more players
          ]
        },
        {
          "team": {
            "id": 12
          },
          "players": [
            // ... players for second team
          ]
        }
      ]
    }
  ]
}
```

---

## Available Statistics Per Player

- ✅ **disposals** - Total disposals
- ✅ **goals** - Goals (total) and assists
- ✅ **behinds** - Behinds
- ✅ **kicks** - Kicks
- ✅ **handballs** - Handballs
- ✅ **marks** - Marks
- ✅ **tackles** - Tackles
- ✅ **hitouts** - Hitouts
- ✅ **clearances** - Clearances
- ✅ **free_kicks** - Free kicks for/against

---

## Data Mapping to Our Schema

### For `player_game_stats` table:

```python
# From response structure:
game_data = response['response'][0]
game_id = game_data['game']['id']

for team_data in game_data['teams']:
    team_id = team_data['team']['id']
    
    # Find opponent team
    opponent_team_id = [t['team']['id'] for t in game_data['teams'] if t['team']['id'] != team_id][0]
    
    for player_stat in team_data['players']:
        api_player_id = player_stat['player']['id']
        player_number = player_stat['player'].get('number')
        
        # Map to our database
        stats = {
            'player_id': get_player_id_by_api_id(api_player_id),  # Lookup in our DB
            'game_id': get_game_id_by_api_id(game_id),  # Lookup in our DB
            'team_id': team_id,  # Use API team ID directly
            'opponent_team_id': opponent_team_id,
            'disposals': player_stat['disposals'],
            'goals': player_stat['goals']['total'],
            # ... other stats
        }
```

---

## Request Budget

**Free Plan**: 100 requests/day

**Per Game**: 1 request per game
- **2023 Season**: ~216 games = 216 requests
- **2024 Season**: ~216 games = 216 requests
- **Full season scraping**: Would take ~2-3 days on free plan

**Optimization Options**:
1. Use `ids` parameter (paid plan) - Get up to 10 games per request
2. Scrape incrementally - Add new games as they're played
3. Prioritize recent seasons first

---

## Example Usage

```python
import requests

api_key = 'YOUR_API_KEY'
base_url = 'https://v1.afl.api-sports.io'

headers = {
    'x-rapidapi-key': api_key,
    'x-rapidapi-host': 'v1.afl.api-sports.io'
}

# Get player statistics for a game
game_id = 2524
response = requests.get(
    f'{base_url}/games/statistics/players',
    headers=headers,
    params={'id': game_id}
)

if response.status_code == 200:
    data = response.json()
    game_stats = data['response'][0]
    
    # Process each team
    for team_data in game_stats['teams']:
        team_id = team_data['team']['id']
        for player_stat in team_data['players']:
            api_player_id = player_stat['player']['id']
            disposals = player_stat['disposals']
            goals = player_stat['goals']['total']
            # ... process stats
```

---

## Next Steps

1. ✅ Endpoint found and tested
2. ✅ Response structure documented
3. ⏭️ Build scraper function to process this data
4. ⏭️ Map to our database schema
5. ⏭️ Handle rate limiting (100 requests/day)
6. ⏭️ Test with sample games

---

## Summary

**We can now get per-game player statistics!** 🎉

The endpoint `/games/statistics/players?id={game_id}` returns:
- All players who played in the game
- Their team assignment
- Complete statistics (disposals, goals, kicks, etc.)

This is exactly what we need to populate our `player_game_stats` table!

