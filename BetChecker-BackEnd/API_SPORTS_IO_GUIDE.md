# API-Sports.io AFL API Integration Guide

## Overview

[API-Sports.io](https://api-sports.io/documentation/afl/v1) provides a comprehensive AFL (Australian Football League) API that can be used to fetch player statistics, game data, teams, and more.

## Authentication

API-Sports.io requires an API key for access:

1. **Sign up**: Create an account at [api-sports.io](https://api-sports.io)
2. **Get API Key**: Navigate to your dashboard to get your API key
3. **Rate Limits**: Check your subscription tier for rate limits
   - Free tier: Limited requests per day
   - Paid tiers: Higher limits

## Base URL

```
https://v1.afl.api-sports.io
```

## Authentication Header

All requests require the API key in headers:

```python
headers = {
    'x-rapidapi-key': 'YOUR_API_KEY',
    'x-rapidapi-host': 'v1.afl.api-sports.io'
}
```

## Key Endpoints (Typical Structure)

Based on API-Sports.io's standard structure, the AFL API likely includes:

### 1. Players Endpoint
```
GET /players
GET /players/{id}
GET /players/search?name={name}
```

**Expected Response:**
```json
{
  "player": {
    "id": 123,
    "name": "Scott Pendlebury",
    "firstname": "Scott",
    "lastname": "Pendlebury",
    "birth": {
      "date": "1988-01-07",
      "place": "Adelaide, Australia"
    },
    "nationality": "Australia",
    "height": "191 cm",
    "weight": "91 kg",
    "injured": false,
    "photo": "https://..."
  }
}
```

### 2. Teams Endpoint
```
GET /teams
GET /teams/{id}
GET /teams/{id}/players
```

### 3. Games/Fixtures Endpoint
```
GET /fixtures
GET /fixtures/{id}
GET /fixtures?season={year}
GET /fixtures?team={team_id}
```

**Expected Response:**
```json
{
  "fixture": {
    "id": 12345,
    "date": "2024-03-15T19:20:00+00:00",
    "venue": {
      "id": 1,
      "name": "MCG",
      "city": "Melbourne"
    },
    "teams": {
      "home": {
        "id": 1,
        "name": "Collingwood",
        "winner": true
      },
      "away": {
        "id": 2,
        "name": "Carlton",
        "winner": false
      }
    },
    "score": {
      "home": 95,
      "away": 78
    }
  }
}
```

### 4. Player Statistics Endpoint
```
GET /players/{id}/statistics
GET /players/{id}/statistics?season={year}
GET /players/{id}/statistics?fixture={fixture_id}
```

**Expected Response:**
```json
{
  "player": {
    "id": 123,
    "name": "Scott Pendlebury"
  },
  "statistics": [
    {
      "team": {
        "id": 1,
        "name": "Collingwood"
      },
      "games": {
        "appearences": 25,
        "lineups": 25,
        "minutes": 2250,
        "position": "Midfielder",
        "rating": "8.5",
        "captain": false
      },
      "shots": {
        "total": 45,
        "on": 30
      },
      "goals": {
        "total": 12,
        "conceded": 0,
        "assists": 8,
        "saves": null
      },
      "passes": {
        "total": 650,
        "key": 120,
        "accuracy": 85
      },
      "tackles": {
        "total": 95,
        "blocks": 12,
        "interceptions": 25
      },
      "duels": {
        "total": 180,
        "won": 110
      },
      "dribbles": {
        "attempts": 45,
        "success": 35,
        "past": null
      },
      "fouls": {
        "drawn": 20,
        "committed": 15
      },
      "cards": {
        "yellow": 2,
        "red": 0
      },
      "penalty": {
        "won": null,
        "commited": null,
        "scored": 0,
        "missed": 0,
        "saved": null
      }
    }
  ]
}
```

### 5. Standings/League Table
```
GET /standings?season={year}
GET /standings?league={league_id}
```

## Implementation Example

### Python Client

```python
import requests
import os
from typing import Optional, Dict, List
from datetime import date

class APISportsAFLClient:
    def __init__(self, api_key: str):
        self.api_key = api_key
        self.base_url = "https://v1.afl.api-sports.io"
        self.headers = {
            'x-rapidapi-key': api_key,
            'x-rapidapi-host': 'v1.afl.api-sports.io'
        }
    
    def _request(self, endpoint: str, params: Optional[Dict] = None) -> Optional[Dict]:
        """Make API request with error handling"""
        url = f"{self.base_url}{endpoint}"
        try:
            response = requests.get(url, headers=self.headers, params=params, timeout=10)
            response.raise_for_status()
            return response.json()
        except requests.RequestException as e:
            print(f"Error fetching {endpoint}: {e}")
            return None
    
    def get_player_by_id(self, player_id: int) -> Optional[Dict]:
        """Get player details by ID"""
        data = self._request(f"/players/{player_id}")
        return data.get('player') if data else None
    
    def search_players(self, name: str) -> List[Dict]:
        """Search for players by name"""
        data = self._request("/players/search", params={'name': name})
        return data.get('players', []) if data else []
    
    def get_player_statistics(
        self, 
        player_id: int, 
        season: Optional[int] = None,
        fixture_id: Optional[int] = None
    ) -> List[Dict]:
        """Get player statistics"""
        params = {}
        if season:
            params['season'] = season
        if fixture_id:
            params['fixture'] = fixture_id
        
        data = self._request(f"/players/{player_id}/statistics", params=params)
        return data.get('statistics', []) if data else []
    
    def get_fixtures(
        self,
        season: Optional[int] = None,
        team_id: Optional[int] = None,
        date: Optional[str] = None
    ) -> List[Dict]:
        """Get fixtures/games"""
        params = {}
        if season:
            params['season'] = season
        if team_id:
            params['team'] = team_id
        if date:
            params['date'] = date
        
        data = self._request("/fixtures", params=params)
        return data.get('fixtures', []) if data else []
    
    def get_teams(self) -> List[Dict]:
        """Get all teams"""
        data = self._request("/teams")
        return data.get('teams', []) if data else []
```

### Integration with Database Manager

```python
from database.db_manager import DatabaseManager
from datetime import datetime

def scrape_player_from_api_sports(
    client: APISportsAFLClient,
    db: DatabaseManager,
    player_id: int
):
    """Scrape a player from API-Sports and add to database"""
    
    # Get player data
    player_data = client.get_player_by_id(player_id)
    if not player_data:
        return None
    
    # Extract DOB
    dob = None
    if player_data.get('birth') and player_data['birth'].get('date'):
        try:
            dob = datetime.strptime(player_data['birth']['date'], '%Y-%m-%d').date()
        except:
            pass
    
    # Get or create player in database
    player_db_id = db.get_or_create_player(
        player_name=player_data.get('name', ''),
        date_of_birth=dob,
        first_name=player_data.get('firstname'),
        last_name=player_data.get('lastname')
    )
    
    return player_db_id

def scrape_player_stats_from_api_sports(
    client: APISportsAFLClient,
    db: DatabaseManager,
    player_id: int,
    season: int
):
    """Scrape player statistics for a season"""
    
    # Get player statistics
    stats_list = client.get_player_statistics(player_id, season=season)
    
    for stat_entry in stats_list:
        # Get team
        team_name = stat_entry.get('team', {}).get('name')
        if not team_name:
            continue
        
        team_id = db.get_or_create_team(team_name)
        
        # Get fixtures for this season to match stats to games
        fixtures = client.get_fixtures(season=season)
        
        # Process each game's stats
        # Note: API structure may vary - adjust based on actual response
        # ...
```

## Data Mapping to Our Schema

### Player Data
- **API**: `player.name`, `player.birth.date`
- **Our Schema**: `players.player_name`, `players.date_of_birth`

### Team Data
- **API**: `team.name`, `team.id`
- **Our Schema**: `teams.team_name`

### Game Data
- **API**: `fixture.date`, `fixture.venue`, `fixture.teams`
- **Our Schema**: `games.game_date`, `games.venue_id`, `games.home_team_id`, `games.away_team_id`

### Player Stats
- **API**: `statistics.goals.total`, `statistics.passes.total` (disposals)
- **Our Schema**: `player_game_stats.goals`, `player_game_stats.disposals`

## Rate Limiting

API-Sports.io has rate limits based on subscription:
- **Free tier**: ~100 requests/day
- **Basic tier**: ~500 requests/day
- **Pro tier**: Higher limits

**Best Practices:**
1. Cache responses locally
2. Batch requests when possible
3. Add delays between requests
4. Monitor your usage

## Error Handling

```python
def safe_request(client, endpoint, max_retries=3):
    """Request with retry logic"""
    for attempt in range(max_retries):
        try:
            return client._request(endpoint)
        except requests.HTTPError as e:
            if e.response.status_code == 429:  # Rate limit
                time.sleep(60)  # Wait 1 minute
                continue
            elif e.response.status_code == 404:
                return None  # Not found
            else:
                raise
    return None
```

## Next Steps

1. **Sign up for API-Sports.io account**
2. **Get your API key**
3. **Test the API** with a few sample requests
4. **Inspect the actual response structure** (may differ from examples)
5. **Map the response fields** to our database schema
6. **Build the scraper** using the DatabaseManager
7. **Handle rate limits** appropriately
8. **Test with validation suite**

## Important Notes

- **Verify the actual API structure** - The examples above are based on typical API-Sports.io patterns, but the actual AFL API structure may differ
- **Check for DOB availability** - Verify that player birth dates are included in responses
- **Test rate limits** - Understand your subscription limits before bulk scraping
- **Handle missing data** - Some fields may be optional or missing

## Resources

- [API-Sports.io AFL Documentation](https://api-sports.io/documentation/afl/v1)
- [API-Sports.io Dashboard](https://dashboard.api-sports.io)
- [API-Sports.io Support](https://api-sports.io/support)

## Comparison with Web Scraping

**Advantages of API:**
- ✅ Structured data (JSON)
- ✅ No HTML parsing needed
- ✅ More reliable (less likely to break)
- ✅ Official data source
- ✅ Rate limits are clear

**Disadvantages:**
- ❌ May require paid subscription
- ❌ Rate limits may be restrictive
- ❌ May not have all historical data
- ❌ Dependent on third-party service

**Recommendation:**
- Use API for current/recent seasons
- Use web scraping for historical data if API doesn't cover it
- Combine both approaches if needed

