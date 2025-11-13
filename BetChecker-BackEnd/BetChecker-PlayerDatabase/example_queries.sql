-- Example Queries for AFL Player Statistics Analysis
-- Copy and paste these into sqlite3 to run

-- ============================================================================
-- BASIC PLAYER QUERIES
-- ============================================================================

-- Get all games for a specific player
SELECT 
    game_date,
    round_name,
    opponent_name,
    location,
    result,
    disposals,
    goals,
    tackles
FROM vw_complete_game_stats
WHERE player_name = 'Scott Pendlebury'
ORDER BY game_date DESC;

-- Player career averages
SELECT 
    player_name,
    COUNT(*) as games_played,
    ROUND(AVG(disposals), 2) as avg_disposals,
    ROUND(AVG(goals), 2) as avg_goals
FROM vw_complete_game_stats
WHERE player_name = 'Scott Pendlebury';

-- ============================================================================
-- PERCENTAGE-BASED QUERIES (Your Main Use Case)
-- ============================================================================

-- What percentage of games did player have 30+ disposals?
SELECT 
    player_name,
    COUNT(*) as total_games,
    SUM(CASE WHEN disposals >= 30 THEN 1 ELSE 0 END) as games_30_plus_disposals,
    ROUND(100.0 * SUM(CASE WHEN disposals >= 30 THEN 1 ELSE 0 END) / COUNT(*), 2) as percentage
FROM vw_complete_game_stats
WHERE player_name = 'Scott Pendlebury'
GROUP BY player_name;

-- Multiple thresholds analysis
SELECT 
    player_name,
    COUNT(*) as total_games,
    -- Disposals thresholds
    ROUND(100.0 * SUM(CASE WHEN disposals >= 35 THEN 1 ELSE 0 END) / COUNT(*), 1) as pct_35_plus_disp,
    ROUND(100.0 * SUM(CASE WHEN disposals >= 30 THEN 1 ELSE 0 END) / COUNT(*), 1) as pct_30_plus_disp,
    ROUND(100.0 * SUM(CASE WHEN disposals >= 25 THEN 1 ELSE 0 END) / COUNT(*), 1) as pct_25_plus_disp,
    ROUND(100.0 * SUM(CASE WHEN disposals >= 20 THEN 1 ELSE 0 END) / COUNT(*), 1) as pct_20_plus_disp,
    -- Goals thresholds
    ROUND(100.0 * SUM(CASE WHEN goals >= 3 THEN 1 ELSE 0 END) / COUNT(*), 1) as pct_3_plus_goals,
    ROUND(100.0 * SUM(CASE WHEN goals >= 2 THEN 1 ELSE 0 END) / COUNT(*), 1) as pct_2_plus_goals,
    ROUND(100.0 * SUM(CASE WHEN goals >= 1 THEN 1 ELSE 0 END) / COUNT(*), 1) as pct_1_plus_goals
FROM vw_complete_game_stats
WHERE player_name = 'Scott Pendlebury'
GROUP BY player_name;

-- Percentage with combined conditions (e.g., 25+ disposals AND 2+ goals)
SELECT 
    player_name,
    COUNT(*) as total_games,
    SUM(CASE WHEN disposals >= 25 AND goals >= 2 THEN 1 ELSE 0 END) as games_meeting_both,
    ROUND(100.0 * SUM(CASE WHEN disposals >= 25 AND goals >= 2 THEN 1 ELSE 0 END) / COUNT(*), 2) as percentage
FROM vw_complete_game_stats
WHERE player_name = 'Scott Pendlebury'
GROUP BY player_name;

-- ============================================================================
-- HOME VS AWAY ANALYSIS
-- ============================================================================

-- Compare home vs away performance
SELECT 
    player_name,
    location,
    COUNT(*) as games,
    ROUND(AVG(disposals), 2) as avg_disposals,
    ROUND(AVG(goals), 2) as avg_goals,
    -- Percentages at each location
    ROUND(100.0 * SUM(CASE WHEN disposals >= 30 THEN 1 ELSE 0 END) / COUNT(*), 1) as pct_30_plus_disp,
    ROUND(100.0 * SUM(CASE WHEN goals >= 2 THEN 1 ELSE 0 END) / COUNT(*), 1) as pct_2_plus_goals
FROM vw_complete_game_stats
WHERE player_name = 'Scott Pendlebury'
GROUP BY player_name, location;

-- ============================================================================
-- VENUE ANALYSIS
-- ============================================================================

-- Performance at different venues
SELECT 
    venue_name,
    venue_state,
    COUNT(*) as games_played,
    ROUND(AVG(disposals), 2) as avg_disposals,
    ROUND(AVG(goals), 2) as avg_goals,
    ROUND(100.0 * SUM(CASE WHEN disposals >= 30 THEN 1 ELSE 0 END) / COUNT(*), 1) as pct_30_plus_disp,
    ROUND(100.0 * SUM(CASE WHEN goals >= 2 THEN 1 ELSE 0 END) / COUNT(*), 1) as pct_2_plus_goals
FROM vw_complete_game_stats
WHERE player_name = 'Scott Pendlebury'
GROUP BY venue_name, venue_state
HAVING games_played >= 3  -- Only venues with 3+ games
ORDER BY games_played DESC;

-- Interstate vs home state analysis (for Victorian players)
SELECT 
    CASE WHEN venue_state = 'VIC' THEN 'Victoria' ELSE 'Interstate' END as location_type,
    COUNT(*) as games,
    ROUND(AVG(disposals), 2) as avg_disposals,
    ROUND(AVG(goals), 2) as avg_goals,
    ROUND(100.0 * SUM(CASE WHEN disposals >= 30 THEN 1 ELSE 0 END) / COUNT(*), 1) as pct_30_plus_disp
FROM vw_complete_game_stats
WHERE player_name = 'Scott Pendlebury'
GROUP BY location_type;

-- ============================================================================
-- GAME TYPE ANALYSIS
-- ============================================================================

-- Regular season vs finals performance
SELECT 
    game_type,
    COUNT(*) as games,
    ROUND(AVG(disposals), 2) as avg_disposals,
    ROUND(AVG(goals), 2) as avg_goals,
    ROUND(AVG(tackles), 2) as avg_tackles,
    ROUND(AVG(contested_possessions), 2) as avg_contested
FROM vw_complete_game_stats
WHERE player_name = 'Scott Pendlebury'
GROUP BY game_type;

-- ============================================================================
-- OPPONENT ANALYSIS
-- ============================================================================

-- Performance against specific opponents
SELECT 
    opponent_name,
    COUNT(*) as games,
    ROUND(AVG(disposals), 2) as avg_disposals,
    ROUND(AVG(goals), 2) as avg_goals,
    ROUND(AVG(tackles), 2) as avg_tackles,
    SUM(CASE WHEN result = 'Win' THEN 1 ELSE 0 END) as wins,
    SUM(CASE WHEN result = 'Loss' THEN 1 ELSE 0 END) as losses
FROM vw_complete_game_stats
WHERE player_name = 'Scott Pendlebury'
GROUP BY opponent_name
HAVING games >= 3  -- Opponents faced at least 3 times
ORDER BY games DESC;

-- Best games against each opponent
SELECT 
    opponent_name,
    game_date,
    round_name,
    location,
    disposals,
    goals,
    tackles,
    result
FROM vw_complete_game_stats
WHERE player_name = 'Scott Pendlebury'
ORDER BY opponent_name, disposals DESC;

-- ============================================================================
-- DAYS SINCE LAST GAME ANALYSIS
-- ============================================================================

-- Performance based on rest days
SELECT 
    CASE 
        WHEN days_since_last_game IS NULL THEN 'First Game'
        WHEN days_since_last_game <= 6 THEN 'Short Rest (≤6 days)'
        WHEN days_since_last_game = 7 THEN 'Normal Rest (7 days)'
        WHEN days_since_last_game BETWEEN 8 AND 14 THEN 'Extended Rest (8-14 days)'
        ELSE 'Long Break (>14 days)'
    END as rest_category,
    COUNT(*) as games,
    ROUND(AVG(disposals), 2) as avg_disposals,
    ROUND(AVG(contested_possessions), 2) as avg_contested,
    ROUND(AVG(tackles), 2) as avg_tackles
FROM vw_complete_game_stats
WHERE player_name = 'Scott Pendlebury'
GROUP BY rest_category
ORDER BY 
    CASE rest_category
        WHEN 'First Game' THEN 0
        WHEN 'Short Rest (≤6 days)' THEN 1
        WHEN 'Normal Rest (7 days)' THEN 2
        WHEN 'Extended Rest (8-14 days)' THEN 3
        WHEN 'Long Break (>14 days)' THEN 4
    END;

-- ============================================================================
-- SEASON PROGRESSION
-- ============================================================================

-- Performance by season
SELECT 
    season_year,
    COUNT(*) as games,
    ROUND(AVG(disposals), 2) as avg_disposals,
    ROUND(AVG(goals), 2) as avg_goals,
    ROUND(AVG(tackles), 2) as avg_tackles,
    MAX(disposals) as best_disposals,
    MAX(goals) as best_goals
FROM vw_complete_game_stats
WHERE player_name = 'Scott Pendlebury'
GROUP BY season_year
ORDER BY season_year;

-- ============================================================================
-- TEAMMATE COMPARISONS
-- ============================================================================

-- Compare two teammates in games they played together
SELECT 
    g.game_date,
    g.round_name,
    vw1.opponent_name,
    vw1.location,
    vw1.player_name as player1,
    vw1.disposals as p1_disp,
    vw1.goals as p1_goals,
    vw1.tackles as p1_tackles,
    vw2.player_name as player2,
    vw2.disposals as p2_disp,
    vw2.goals as p2_goals,
    vw2.tackles as p2_tackles,
    vw1.result
FROM player_game_stats pgs1
JOIN vw_complete_game_stats vw1 ON pgs1.stat_id = vw1.stat_id
JOIN player_game_stats pgs2 ON pgs1.game_id = pgs2.game_id 
    AND pgs1.team_id = pgs2.team_id 
    AND pgs1.player_id < pgs2.player_id  -- Prevent duplicates
JOIN vw_complete_game_stats vw2 ON pgs2.stat_id = vw2.stat_id
JOIN games g ON pgs1.game_id = g.game_id
WHERE vw1.player_name = 'Scott Pendlebury'
    AND vw2.player_name = 'Steele Sidebottom'
ORDER BY g.game_date;

-- Team stats summary for a specific game
SELECT 
    player_name,
    disposals,
    goals,
    tackles,
    contested_possessions,
    clearances
FROM vw_complete_game_stats
WHERE game_id = 1  -- Change to specific game ID
ORDER BY disposals DESC;

-- ============================================================================
-- WIN/LOSS ANALYSIS
-- ============================================================================

-- Performance in wins vs losses
SELECT 
    result,
    COUNT(*) as games,
    ROUND(AVG(disposals), 2) as avg_disposals,
    ROUND(AVG(goals), 2) as avg_goals,
    ROUND(AVG(tackles), 2) as avg_tackles,
    ROUND(AVG(contested_possessions), 2) as avg_contested
FROM vw_complete_game_stats
WHERE player_name = 'Scott Pendlebury'
GROUP BY result;

-- Games where player had great stats but team lost
SELECT 
    game_date,
    round_name,
    opponent_name,
    location,
    disposals,
    goals,
    tackles,
    contested_possessions
FROM vw_complete_game_stats
WHERE player_name = 'Scott Pendlebury'
    AND result = 'Loss'
    AND disposals >= 30  -- Had 30+ disposals but still lost
ORDER BY disposals DESC;

-- ============================================================================
-- FORM/TREND ANALYSIS
-- ============================================================================

-- Last N games performance
SELECT 
    game_date,
    round_name,
    opponent_name,
    disposals,
    goals,
    tackles,
    result
FROM vw_complete_game_stats
WHERE player_name = 'Scott Pendlebury'
ORDER BY game_date DESC
LIMIT 10;  -- Last 10 games

-- Moving average (last 5 games)
WITH numbered_games AS (
    SELECT 
        game_date,
        round_name,
        disposals,
        goals,
        tackles,
        ROW_NUMBER() OVER (ORDER BY game_date DESC) as game_num
    FROM vw_complete_game_stats
    WHERE player_name = 'Scott Pendlebury'
)
SELECT 
    game_date,
    round_name,
    disposals,
    ROUND(AVG(disposals) OVER (ORDER BY game_num DESC ROWS BETWEEN CURRENT ROW AND 4 FOLLOWING), 2) as last_5_avg_disp,
    goals,
    ROUND(AVG(goals) OVER (ORDER BY game_num DESC ROWS BETWEEN CURRENT ROW AND 4 FOLLOWING), 2) as last_5_avg_goals,
    tackles,
    ROUND(AVG(tackles) OVER (ORDER BY game_num DESC ROWS BETWEEN CURRENT ROW AND 4 FOLLOWING), 2) as last_5_avg_tackles
FROM numbered_games
ORDER BY game_date DESC
LIMIT 10;

-- ============================================================================
-- COMPARING MULTIPLE PLAYERS
-- ============================================================================

-- Compare multiple players' career averages
SELECT 
    player_name,
    COUNT(*) as games,
    ROUND(AVG(disposals), 2) as avg_disposals,
    ROUND(AVG(goals), 2) as avg_goals,
    ROUND(AVG(tackles), 2) as avg_tackles,
    ROUND(AVG(contested_possessions), 2) as avg_contested,
    ROUND(100.0 * SUM(CASE WHEN disposals >= 30 THEN 1 ELSE 0 END) / COUNT(*), 1) as pct_30_plus_disp
FROM vw_complete_game_stats
WHERE player_name IN ('Scott Pendlebury', 'Patrick Dangerfield', 'Dustin Martin')
GROUP BY player_name
ORDER BY avg_disposals DESC;

-- ============================================================================
-- FINDING OUTLIER GAMES
-- ============================================================================

-- Best disposal games
SELECT 
    player_name,
    game_date,
    round_name,
    opponent_name,
    location,
    disposals,
    goals,
    tackles,
    result
FROM vw_complete_game_stats
WHERE player_name = 'Scott Pendlebury'
ORDER BY disposals DESC
LIMIT 10;

-- Best goal-kicking games
SELECT 
    player_name,
    game_date,
    round_name,
    opponent_name,
    location,
    goals,
    disposals,
    score_involvements,
    result
FROM vw_complete_game_stats
WHERE player_name = 'Scott Pendlebury'
ORDER BY goals DESC
LIMIT 10;

-- Best all-around games (high disposals + goals + tackles)
SELECT 
    player_name,
    game_date,
    round_name,
    opponent_name,
    disposals,
    goals,
    tackles,
    contested_possessions,
    (disposals + (goals * 6) + (tackles * 3)) as combined_score,
    result
FROM vw_complete_game_stats
WHERE player_name = 'Scott Pendlebury'
ORDER BY combined_score DESC
LIMIT 10;

