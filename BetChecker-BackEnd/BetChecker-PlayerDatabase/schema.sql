-- AFL Player Statistics Database Schema
-- Designed for tracking player performance and running statistical analysis
-- Time period: From Scott Pendlebury era (2006+) onwards

-- ============================================================================
-- MASTER DATA TABLES
-- ============================================================================

-- Players table: Master list of all AFL players
CREATE TABLE players (
    player_id INTEGER PRIMARY KEY AUTOINCREMENT,
    player_name TEXT NOT NULL,
    first_name TEXT,
    last_name TEXT,
    date_of_birth DATE,
    debut_year INTEGER,             -- Year player debuted (e.g., 2006)
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

CREATE INDEX idx_players_name ON players(player_name);
CREATE INDEX idx_players_last_name ON players(last_name);

-- Teams table: AFL teams (current and historical)
CREATE TABLE teams (
    team_id INTEGER PRIMARY KEY AUTOINCREMENT,
    team_name TEXT NOT NULL UNIQUE,
    is_active BOOLEAN DEFAULT 1,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- Venues table: Stadiums and grounds
CREATE TABLE venues (
    venue_id INTEGER PRIMARY KEY AUTOINCREMENT,
    venue_name TEXT NOT NULL UNIQUE,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

CREATE INDEX idx_venues_name ON venues(venue_name);

-- ============================================================================
-- GAMES TABLE
-- ============================================================================

-- Games table: Master list of all games
CREATE TABLE games (
    game_id INTEGER PRIMARY KEY AUTOINCREMENT,
    season_year INTEGER NOT NULL,
    round_number INTEGER,              -- NULL for finals
    game_type TEXT NOT NULL,           -- 'Pre-Season', 'Regular Season', 'Finals'
    game_date DATE NOT NULL,
    game_time TIME,
    venue_id INTEGER NOT NULL,
    home_team_id INTEGER NOT NULL,
    away_team_id INTEGER NOT NULL,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    
    FOREIGN KEY (venue_id) REFERENCES venues(venue_id),
    FOREIGN KEY (home_team_id) REFERENCES teams(team_id),
    FOREIGN KEY (away_team_id) REFERENCES teams(team_id),
    
    CHECK (game_type IN ('Pre-Season', 'Regular Season', 'Finals')),
    CHECK (home_team_id != away_team_id)
);

CREATE INDEX idx_games_date ON games(game_date);
CREATE INDEX idx_games_season ON games(season_year);
CREATE INDEX idx_games_home_team ON games(home_team_id);
CREATE INDEX idx_games_away_team ON games(away_team_id);
CREATE INDEX idx_games_venue ON games(venue_id);
CREATE INDEX idx_games_type ON games(game_type);

-- ============================================================================
-- PLAYER GAME STATS TABLE (Main table for analysis)
-- ============================================================================

-- Player Game Stats: Individual player statistics for each game
CREATE TABLE player_game_stats (
    stat_id INTEGER PRIMARY KEY AUTOINCREMENT,
    player_id INTEGER NOT NULL,
    game_id INTEGER NOT NULL,
    team_id INTEGER NOT NULL,          -- Team they played for in this game
    opponent_team_id INTEGER NOT NULL, -- Team they played against
    venue_id INTEGER NOT NULL,         -- Where the game was played
    location TEXT NOT NULL,            -- 'Home' or 'Away'
    game_time TEXT,                    -- 'Day', 'Twilight', or 'Night' (based on your time boundaries)
    
    -- Core statistics (simplified - only disposals and goals)
    disposals INTEGER DEFAULT 0,
    goals INTEGER DEFAULT 0,
    
    -- Derived/calculated fields
    days_since_last_game INTEGER,      -- Days since this player's previous game
    
    -- Metadata
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    
    FOREIGN KEY (player_id) REFERENCES players(player_id),
    FOREIGN KEY (game_id) REFERENCES games(game_id),
    FOREIGN KEY (team_id) REFERENCES teams(team_id),
    FOREIGN KEY (opponent_team_id) REFERENCES teams(team_id),
    FOREIGN KEY (venue_id) REFERENCES venues(venue_id),
    
    CHECK (location IN ('Home', 'Away')),
    CHECK (game_time IS NULL OR game_time IN ('Day', 'Twilight', 'Night')),
    
    -- Ensure one stat entry per player per game
    UNIQUE(player_id, game_id)
);

CREATE INDEX idx_pgs_player ON player_game_stats(player_id);
CREATE INDEX idx_pgs_game ON player_game_stats(game_id);
CREATE INDEX idx_pgs_team ON player_game_stats(team_id);
CREATE INDEX idx_pgs_opponent ON player_game_stats(opponent_team_id);
CREATE INDEX idx_pgs_venue ON player_game_stats(venue_id);
CREATE INDEX idx_pgs_location ON player_game_stats(location);
CREATE INDEX idx_pgs_game_time ON player_game_stats(game_time);
CREATE INDEX idx_pgs_player_date ON player_game_stats(player_id, game_id);

-- ============================================================================
-- PLAYER TEAM HISTORY (Track team changes over time)
-- ============================================================================

-- Player Team History: Track when players switch teams
CREATE TABLE player_team_history (
    history_id INTEGER PRIMARY KEY AUTOINCREMENT,
    player_id INTEGER NOT NULL,
    team_id INTEGER NOT NULL,
    start_date DATE NOT NULL,
    end_date DATE,                     -- NULL if currently with team
    is_current BOOLEAN DEFAULT 0,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    
    FOREIGN KEY (player_id) REFERENCES players(player_id),
    FOREIGN KEY (team_id) REFERENCES teams(team_id)
);

CREATE INDEX idx_pth_player ON player_team_history(player_id);
CREATE INDEX idx_pth_team ON player_team_history(team_id);
CREATE INDEX idx_pth_current ON player_team_history(is_current);

-- ============================================================================
-- VIEWS FOR COMMON QUERIES
-- ============================================================================

-- Complete game stats view: Joins all relevant information for easy querying
CREATE VIEW vw_complete_game_stats AS
SELECT 
    pgs.stat_id,
    pgs.player_id,
    p.player_name,
    p.first_name,
    p.last_name,
    pgs.game_id,
    g.game_date,
    g.season_year,
    g.round_number,
    g.game_type,
    pgs.team_id,
    t.team_name,
    pgs.opponent_team_id,
    opponent.team_name AS opponent_name,
    pgs.venue_id,
    v.venue_name,
    pgs.location,
    pgs.game_time,
    -- Player stats
    pgs.disposals,
    pgs.goals,
    pgs.days_since_last_game
FROM player_game_stats pgs
JOIN players p ON pgs.player_id = p.player_id
JOIN games g ON pgs.game_id = g.game_id
JOIN teams t ON pgs.team_id = t.team_id
JOIN teams opponent ON pgs.opponent_team_id = opponent.team_id
JOIN venues v ON pgs.venue_id = v.venue_id;

-- ============================================================================
-- HELPER FUNCTIONS / TRIGGERS
-- ============================================================================

-- Trigger to update the 'updated_at' timestamp on player_game_stats
CREATE TRIGGER update_player_game_stats_timestamp 
AFTER UPDATE ON player_game_stats
BEGIN
    UPDATE player_game_stats 
    SET updated_at = CURRENT_TIMESTAMP 
    WHERE stat_id = NEW.stat_id;
END;

-- Trigger to update the 'updated_at' timestamp on games
CREATE TRIGGER update_games_timestamp 
AFTER UPDATE ON games
BEGIN
    UPDATE games 
    SET updated_at = CURRENT_TIMESTAMP 
    WHERE game_id = NEW.game_id;
END;

-- Trigger to update the 'updated_at' timestamp on players
CREATE TRIGGER update_players_timestamp 
AFTER UPDATE ON players
BEGIN
    UPDATE players 
    SET updated_at = CURRENT_TIMESTAMP 
    WHERE player_id = NEW.player_id;
END;

-- ============================================================================
-- SAMPLE QUERIES (commented out)
-- ============================================================================

/*
-- Example 1: Get all games for a specific player
SELECT * FROM vw_complete_game_stats 
WHERE player_name = 'Scott Pendlebury' 
ORDER BY game_date;

-- Example 2: Find percentage of games where player had 30+ disposals
SELECT 
    player_name,
    COUNT(*) as total_games,
    SUM(CASE WHEN disposals >= 30 THEN 1 ELSE 0 END) as games_30_plus,
    ROUND(100.0 * SUM(CASE WHEN disposals >= 30 THEN 1 ELSE 0 END) / COUNT(*), 2) as percentage
FROM vw_complete_game_stats
WHERE player_name = 'Scott Pendlebury'
GROUP BY player_name;

-- Example 3: Home vs Away performance
SELECT 
    player_name,
    location,
    COUNT(*) as games,
    ROUND(AVG(disposals), 2) as avg_disposals,
    ROUND(AVG(goals), 2) as avg_goals
FROM vw_complete_game_stats
WHERE player_name = 'Scott Pendlebury'
GROUP BY player_name, location;

-- Example 4: Performance at specific venues
SELECT 
    venue_name,
    COUNT(*) as games_played,
    ROUND(AVG(disposals), 2) as avg_disposals,
    ROUND(AVG(goals), 2) as avg_goals
FROM vw_complete_game_stats
WHERE player_name = 'Scott Pendlebury'
GROUP BY venue_name
HAVING games_played >= 5
ORDER BY games_played DESC;

-- Example 5: Performance by game type
SELECT 
    game_type,
    COUNT(*) as games,
    ROUND(AVG(disposals), 2) as avg_disposals,
    ROUND(AVG(contested_possessions), 2) as avg_contested
FROM vw_complete_game_stats
WHERE player_name = 'Scott Pendlebury'
GROUP BY game_type;

-- Example 6: Find games where player kicked 3+ goals
SELECT 
    game_date,
    round_name,
    opponent_name,
    location,
    goals,
    disposals
FROM vw_complete_game_stats
WHERE player_name = 'Scott Pendlebury' AND goals >= 3
ORDER BY game_date DESC;

-- Example 7: Calculate days since last game (to be run after inserting stats)
WITH ranked_games AS (
    SELECT 
        pgs.stat_id,
        pgs.player_id,
        pgs.game_id,
        g.game_date,
        LAG(g.game_date) OVER (PARTITION BY pgs.player_id ORDER BY g.game_date) as prev_game_date
    FROM player_game_stats pgs
    JOIN games g ON pgs.game_id = g.game_id
)
UPDATE player_game_stats
SET days_since_last_game = (
    SELECT JULIANDAY(rg.game_date) - JULIANDAY(rg.prev_game_date)
    FROM ranked_games rg
    WHERE rg.stat_id = player_game_stats.stat_id
);

-- Example 8: Performance when days rest > 7 vs <= 7
SELECT 
    CASE 
        WHEN days_since_last_game > 7 THEN 'Extended Rest (>7 days)'
        WHEN days_since_last_game IS NULL THEN 'First Game'
        ELSE 'Normal Rest (<=7 days)'
    END as rest_category,
    COUNT(*) as games,
    ROUND(AVG(disposals), 2) as avg_disposals,
    ROUND(AVG(contested_possessions), 2) as avg_contested
FROM vw_complete_game_stats
WHERE player_name = 'Scott Pendlebury'
GROUP BY rest_category;

-- Example 9: Teammate comparison in same game
SELECT 
    g.game_date,
    g.round_name,
    p1.player_name as player1,
    p1.disposals as player1_disposals,
    p2.player_name as player2,
    p2.disposals as player2_disposals
FROM player_game_stats pgs1
JOIN vw_complete_game_stats p1 ON pgs1.stat_id = p1.stat_id
JOIN player_game_stats pgs2 ON pgs1.game_id = pgs2.game_id 
    AND pgs1.team_id = pgs2.team_id 
    AND pgs1.player_id != pgs2.player_id
JOIN vw_complete_game_stats p2 ON pgs2.stat_id = p2.stat_id
JOIN games g ON pgs1.game_id = g.game_id
WHERE p1.player_name = 'Scott Pendlebury'
    AND p2.player_name = 'Steele Sidebottom'
ORDER BY g.game_date;

-- Example 10: Percentage of games with stats above/below thresholds
SELECT 
    player_name,
    COUNT(*) as total_games,
    ROUND(100.0 * SUM(CASE WHEN disposals >= 25 THEN 1 ELSE 0 END) / COUNT(*), 2) as pct_25_plus_disposals,
    ROUND(100.0 * SUM(CASE WHEN tackles >= 5 THEN 1 ELSE 0 END) / COUNT(*), 2) as pct_5_plus_tackles,
    ROUND(100.0 * SUM(CASE WHEN goals >= 2 THEN 1 ELSE 0 END) / COUNT(*), 2) as pct_2_plus_goals
FROM vw_complete_game_stats
WHERE player_name = 'Scott Pendlebury';
*/

