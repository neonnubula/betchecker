# Database Table Relationships

## Entity Relationship Diagram (Text Format)

```
┌─────────────────┐
│    PLAYERS      │
│─────────────────│
│ player_id (PK)  │◄────────┐
│ player_name     │         │
│ first_name      │         │
│ last_name       │         │
│ date_of_birth   │         │
│ debut_date      │         │
└─────────────────┘         │
                            │
┌─────────────────┐         │
│     TEAMS       │         │
│─────────────────│         │
│ team_id (PK)    │◄────┐   │
│ team_name       │     │   │
│ team_abbrev     │     │   │
│ team_nickname   │     │   │
└─────────────────┘     │   │
                        │   │
┌─────────────────┐     │   │
│    VENUES       │     │   │
│─────────────────│     │   │
│ venue_id (PK)   │◄──┐ │   │
│ venue_name      │   │ │   │
│ city            │   │ │   │
│ state           │   │ │   │
│ capacity        │   │ │   │
└─────────────────┘   │ │   │
                      │ │   │
┌──────────────────────┐ │   │
│       GAMES          │ │   │
│──────────────────────│ │   │
│ game_id (PK)         │◄┼───┼─────────┐
│ season_year          │ │   │         │
│ round_number         │ │   │         │
│ round_name           │ │   │         │
│ game_type            │ │   │         │
│ game_date            │ │   │         │
│ venue_id (FK)        ├─┘   │         │
│ home_team_id (FK)    ├─────┘         │
│ away_team_id (FK)    ├─────┐         │
│ home_score           │     │         │
│ away_score           │     │         │
│ attendance           │     │         │
└──────────────────────┘     │         │
                             │         │
                             │         │
┌────────────────────────────┼─────────┼────────────────┐
│      PLAYER_GAME_STATS     │         │                │
│────────────────────────────│         │                │
│ stat_id (PK)               │         │                │
│ player_id (FK)             ├─────────┘                │
│ game_id (FK)               ├──────────────────────────┘
│ team_id (FK)               ├──────────┐
│ location                   │          │
│ disposals                  │          │
│ kicks                      │          │
│ handballs                  │          │
│ goals                      │          │
│ behinds                    │          │
│ contested_possessions      │          │
│ uncontested_possessions    │          │
│ marks                      │          │
│ contested_marks            │          │
│ marks_inside_50            │          │
│ tackles                    │          │
│ clearances                 │          │
│ inside_50s                 │          │
│ rebound_50s                │          │
│ clangers                   │          │
│ turnovers                  │          │
│ intercepts                 │          │
│ score_involvements         │          │
│ goal_assists               │          │
│ free_kicks_for             │          │
│ free_kicks_against         │          │
│ hitouts                    │          │
│ hitouts_to_advantage       │          │
│ time_on_ground_percentage  │          │
│ days_since_last_game       │          │
└────────────────────────────┘          │
                                        │
┌────────────────────────┐              │
│ PLAYER_TEAM_HISTORY    │              │
│────────────────────────│              │
│ history_id (PK)        │              │
│ player_id (FK)         ├──────────────┤
│ team_id (FK)           ├──────────────┘
│ start_date             │
│ end_date               │
│ is_current             │
└────────────────────────┘
```

## Relationship Summary

### 1. GAMES Table (Central Hub)
**Links to:**
- `venues` (game location)
- `teams` (home team)
- `teams` (away team)

**Relationships:**
- Each game has ONE venue
- Each game has ONE home team
- Each game has ONE away team
- Home team ≠ Away team (enforced by CHECK constraint)

### 2. PLAYER_GAME_STATS Table (Main Data Table) ⭐
**Links to:**
- `players` (who played)
- `games` (which game)
- `teams` (which team they played for)

**Relationships:**
- Each stat entry belongs to ONE player
- Each stat entry belongs to ONE game
- Each stat entry belongs to ONE team
- **UNIQUE constraint:** One player can only have one stat entry per game

**Usage:**
- This is your primary analysis table
- Each row = one player's performance in one specific game
- All your queries will primarily use this table

### 3. PLAYERS Table
**Referenced by:**
- `player_game_stats` (many stats per player)
- `player_team_history` (track team changes)

**Purpose:**
- Master list of all players
- Handles duplicate names via `player_id`
- One player → Many game stats

### 4. TEAMS Table
**Referenced by:**
- `games` (as home or away team)
- `player_game_stats` (team player belonged to)
- `player_team_history` (track transfers)

**Purpose:**
- Master list of AFL teams
- One team → Many games (home and away)
- One team → Many players

### 5. VENUES Table
**Referenced by:**
- `games` (where game was played)

**Purpose:**
- Master list of stadiums
- One venue → Many games

### 6. PLAYER_TEAM_HISTORY Table
**Links to:**
- `players` (which player)
- `teams` (which team)

**Purpose:**
- Track when players change teams
- Support historical queries
- One player → Multiple team stints

## Key Design Patterns

### 1. Foreign Keys (Referential Integrity)
All relationships use foreign keys:
```sql
FOREIGN KEY (player_id) REFERENCES players(player_id)
FOREIGN KEY (game_id) REFERENCES games(game_id)
FOREIGN KEY (team_id) REFERENCES teams(team_id)
```

### 2. Unique Constraints
```sql
-- One stat entry per player per game
UNIQUE(player_id, game_id)

-- Team names and abbreviations must be unique
UNIQUE(team_name)
UNIQUE(team_abbrev)
```

### 3. Check Constraints
```sql
-- Ensure valid game types
CHECK (game_type IN ('Pre-Season', 'Regular Season', 'Finals'))

-- Ensure home and away teams are different
CHECK (home_team_id != away_team_id)

-- Ensure valid location
CHECK (location IN ('Home', 'Away'))
```

### 4. Indexes for Performance
Strategic indexes on commonly queried columns:
```sql
-- Player lookups
CREATE INDEX idx_players_name ON players(player_name);

-- Date-based queries
CREATE INDEX idx_games_date ON games(game_date);

-- Stats by player
CREATE INDEX idx_pgs_player ON player_game_stats(player_id);

-- Stats by game
CREATE INDEX idx_pgs_game ON player_game_stats(game_id);
```

## Query Patterns

### Pattern 1: Single Player Analysis
```sql
-- Uses: player_game_stats → games → players → teams → venues
SELECT * FROM vw_complete_game_stats
WHERE player_name = 'Scott Pendlebury';
```

### Pattern 2: Team Analysis
```sql
-- Uses: player_game_stats → teams
SELECT * FROM vw_complete_game_stats
WHERE team_name = 'Collingwood';
```

### Pattern 3: Venue Analysis
```sql
-- Uses: games → venues → player_game_stats
SELECT * FROM vw_complete_game_stats
WHERE venue_name = 'MCG';
```

### Pattern 4: Teammate Comparison
```sql
-- Uses: player_game_stats (joined to itself)
-- Same game_id, same team_id, different player_id
FROM player_game_stats p1
JOIN player_game_stats p2 
  ON p1.game_id = p2.game_id 
  AND p1.team_id = p2.team_id
  AND p1.player_id != p2.player_id
```

### Pattern 5: Opponent Analysis
```sql
-- Uses: games to determine opponent
-- If player's location = 'Home', opponent = away_team
-- If player's location = 'Away', opponent = home_team
-- (Already handled in vw_complete_game_stats view)
```

## Data Integrity Rules

1. **Cannot delete a player if they have stats recorded**
   - Foreign key constraint prevents orphaned records

2. **Cannot delete a game if stats are recorded for it**
   - Foreign key constraint prevents orphaned records

3. **Cannot add stats for non-existent player/game/team**
   - Foreign key constraint enforces valid references

4. **Each player can only have one stat record per game**
   - UNIQUE constraint on (player_id, game_id)

5. **Home and away teams must be different**
   - CHECK constraint enforces this rule

## Insert Order (Important!)

Always insert data in this order to satisfy foreign keys:

1. ✅ **teams** (no dependencies)
2. ✅ **venues** (no dependencies)
3. ✅ **players** (no dependencies)
4. ✅ **games** (requires teams and venues)
5. ✅ **player_game_stats** (requires players, games, and teams)
6. ✅ **player_team_history** (requires players and teams)

## View: vw_complete_game_stats

This view joins all tables together:

```
player_game_stats
  ├── JOIN players (get player name)
  ├── JOIN games (get game details)
  │     ├── JOIN venues (get venue details)
  │     ├── JOIN teams AS home_team (get home team)
  │     └── JOIN teams AS away_team (get away team)
  └── JOIN teams (get player's team)
```

**Result:** All data in one convenient view for easy querying!

## Scalability

The design supports:
- ✅ Millions of stat entries
- ✅ 20+ years of data
- ✅ 800+ players
- ✅ 18 teams
- ✅ Hundreds of venues
- ✅ Fast queries with proper indexes

## Future Extensions

Easy to add:
- Weather tracking (already in games table)
- Umpire tables
- Injury tracking
- Quarter-by-quarter stats
- Coach information
- Fantasy scores
- Brownlow votes

