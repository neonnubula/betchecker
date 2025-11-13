# Frontend API Integration Instructions

## API Base URL

**Development:**
```
http://localhost:8000
```

**Production:**
```
[Your production URL]
```

## Endpoint: Player Over/Under Statistics

### GET `/search/over-under`

Fetches over/under game counts for a player's statistic across their full career history.

### Request Parameters

| Parameter | Type | Required | Description |
|-----------|------|----------|-------------|
| `player_name` | string | Yes* | Player's full name (e.g., "Scott Pendlebury") |
| `player_id` | integer | Yes* | Player ID number |
| `stat` | string | Yes | Statistic type: `"disposals"` or `"goals"` |
| `threshold` | number | Yes | The threshold value (e.g., 23.5) |
| `strict_over` | boolean | No | Default: `false`. If `true`: over uses `>`, under uses `<=`. If `false`: over uses `>=`, under uses `<` |

*Exactly one of `player_name` or `player_id` must be provided.

### Response Format

**Success (200 OK):**
```json
{
  "over": 150,
  "under": 50
}
```

**Error Responses:**
- `400 Bad Request` - Invalid parameters
  ```json
  { "detail": "Provide exactly one of player_id or player_name" }
  ```
- `404 Not Found` - Player not found
  ```json
  { "detail": "Player not found" }
  ```
- `500 Internal Server Error` - Server error
  ```json
  { "detail": "Database connection error: ..." }
  ```

### Example Usage

#### JavaScript/TypeScript (fetch)
```javascript
async function getPlayerStats(playerName, stat, threshold) {
  const params = new URLSearchParams({
    player_name: playerName,
    stat: stat,
    threshold: threshold.toString()
  });
  
  const response = await fetch(`http://localhost:8000/search/over-under?${params}`);
  
  if (!response.ok) {
    const error = await response.json();
    throw new Error(error.detail || 'Request failed');
  }
  
  return await response.json();
}

// Usage
const stats = await getPlayerStats('Scott Pendlebury', 'disposals', 23.5);
console.log(`Over: ${stats.over}, Under: ${stats.under}`);
```

#### JavaScript/TypeScript (axios)
```javascript
import axios from 'axios';

async function getPlayerStats(playerName, stat, threshold) {
  try {
    const response = await axios.get('http://localhost:8000/search/over-under', {
      params: {
        player_name: playerName,
        stat: stat,
        threshold: threshold
      }
    });
    return response.data;
  } catch (error) {
    if (error.response) {
      throw new Error(error.response.data.detail || 'Request failed');
    }
    throw error;
  }
}
```

#### React Hook Example
```javascript
import { useState, useEffect } from 'react';

function usePlayerStats(playerName, stat, threshold) {
  const [stats, setStats] = useState({ over: 0, under: 0 });
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState(null);

  useEffect(() => {
    if (!playerName || !stat || !threshold) return;

    setLoading(true);
    setError(null);

    const params = new URLSearchParams({
      player_name: playerName,
      stat: stat,
      threshold: threshold.toString()
    });

    fetch(`http://localhost:8000/search/over-under?${params}`)
      .then(res => {
        if (!res.ok) {
          return res.json().then(err => Promise.reject(err));
        }
        return res.json();
      })
      .then(data => {
        setStats(data);
        setLoading(false);
      })
      .catch(err => {
        setError(err.detail || err.message);
        setLoading(false);
      });
  }, [playerName, stat, threshold]);

  return { stats, loading, error };
}

// Usage in component
function PlayerStatsComponent() {
  const { stats, loading, error } = usePlayerStats('Scott Pendlebury', 'disposals', 23.5);

  if (loading) return <div>Loading...</div>;
  if (error) return <div>Error: {error}</div>;

  return (
    <div>
      <p>Over: {stats.over} games</p>
      <p>Under: {stats.under} games</p>
      <p>Total: {stats.over + stats.under} games</p>
    </div>
  );
}
```

### CORS Configuration

The API server has CORS enabled for all origins by default. In production, you may want to restrict this to your frontend domain.

### Testing the API

You can test the API directly using:
- **Interactive Docs**: http://localhost:8000/docs (Swagger UI)
- **Alternative Docs**: http://localhost:8000/redoc
- **cURL**:
  ```bash
  curl "http://localhost:8000/search/over-under?player_name=Scott%20Pendlebury&stat=disposals&threshold=23.5"
  ```

### Available Stats

Currently supported statistics:
- `disposals` - Total disposals per game
- `goals` - Total goals per game

### Notes

- The API returns statistics for the player's **full career history** (all games in the database)
- Threshold values can be decimals (e.g., 23.5)
- Player names are case-sensitive and should match exactly as stored in the database
- The `over` and `under` counts always sum to the total number of games in the database for that player

