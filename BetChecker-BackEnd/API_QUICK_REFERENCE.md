# API Quick Reference - What We Need to Know

## Critical Information (Must Have)

### 1. Player Date of Birth
**Question**: Does the API return player date of birth?
- **Why Critical**: We use name + DOB to handle duplicate names
- **If Missing**: We'll need alternative strategy (use API player_id if stable)

**What to look for in docs:**
- Field names: `birth`, `date_of_birth`, `dob`, `birthdate`
- Format: Usually ISO date string like `"1988-01-07"`

### 2. Player Endpoints
**What we need:**
- Get player by ID: `GET /players/{id}`
- Search players: `GET /players/search?name={name}`
- Get all players: `GET /players` (if available)

**Response should include:**
- Player name (full, first, last)
- Date of birth ⭐
- Player ID (stable across seasons?)

### 3. Statistics Endpoints
**What we need:**
- Get player stats per game: `GET /players/{id}/statistics?fixture={game_id}`
- Get player stats per season: `GET /players/{id}/statistics?season={year}`
- Or: `GET /fixtures/{id}/players` (stats for all players in a game)

**Response should include:**
- Disposals (field name?)
- Goals (field name?)
- Which team the player was on ⭐

### 4. Games/Fixtures Endpoints
**What we need:**
- Get games by season: `GET /fixtures?season={year}`
- Get game by ID: `GET /fixtures/{id}`

**Response should include:**
- Game date
- Venue
- Home team
- Away team
- Round number
- Season year

### 5. Team Assignment
**Critical Question**: How do we know which team a player was on?
- Option A: Included in statistics response
- Option B: Need to match player with fixture team lists
- Option C: Need separate endpoint

## Nice to Have

- Historical data availability (how far back?)
- Rate limits (requests per day/minute)
- Team endpoints (get all teams)
- Venue endpoints (get all venues)

## Quick Checklist

When reviewing the API docs, check:

- [ ] Base URL
- [ ] Authentication method (header name)
- [ ] Players endpoint URL
- [ ] Player response includes DOB
- [ ] Games/Fixtures endpoint URL
- [ ] Statistics endpoint URL
- [ ] Statistics include disposals
- [ ] Statistics include goals
- [ ] Team assignment method
- [ ] Rate limits

## Field Name Variations to Check

The API might use different field names. Look for:

**Disposals:**
- `disposals`, `disposal`, `possessions`, `touches`, `touches_total`

**Goals:**
- `goals`, `goal`, `goals_scored`, `goals_total`

**Date of Birth:**
- `birth.date`, `date_of_birth`, `dob`, `birthdate`, `birth_date`

**Team:**
- `team.id`, `team_id`, `teamName`, `team_name`

## Example Response Structures

Once you have the docs, we'll map:

```json
// Player response (what we expect)
{
  "player": {
    "id": 123,
    "name": "Scott Pendlebury",
    "birth": { "date": "1988-01-07" }  // ← Need this!
  }
}

// Statistics response (what we expect)
{
  "statistics": [{
    "team": { "id": 1, "name": "Collingwood" },  // ← Need this!
    "games": { "appearences": 25 },
    "goals": { "total": 12 },  // ← Field name?
    "passes": { "total": 650 }  // ← Is this disposals?
  }]
}

// Fixture response (what we expect)
{
  "fixture": {
    "id": 12345,
    "date": "2024-03-15",
    "venue": { "name": "MCG" },
    "teams": {
      "home": { "id": 1, "name": "Collingwood" },
      "away": { "id": 2, "name": "Carlton" }
    }
  }
}
```

## Next Action

1. Review the PDF documentation
2. Fill in the checklist above
3. Share the key findings
4. We'll update all code accordingly!

