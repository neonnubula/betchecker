-- Query to find potential duplicate players (same name, different API IDs)
-- Run this periodically to flag players that might be duplicates for manual review

-- Find players with same name but different API IDs
-- These are candidates for manual review to see if they're actually the same person
SELECT 
    p1.player_id as id1,
    p1.api_player_id as api_id1,
    p1.player_name as name1,
    p1.first_name as first_name1,
    p1.last_name as last_name1,
    p1.date_of_birth as dob1,
    p1.debut_year as debut1,
    COUNT(DISTINCT pgs1.game_id) as games1,
    p2.player_id as id2,
    p2.api_player_id as api_id2,
    p2.player_name as name2,
    p2.first_name as first_name2,
    p2.last_name as last_name2,
    p2.date_of_birth as dob2,
    p2.debut_year as debut2,
    COUNT(DISTINCT pgs2.game_id) as games2,
    -- Check if they played for same teams
    GROUP_CONCAT(DISTINCT t1.team_name) as teams1,
    GROUP_CONCAT(DISTINCT t2.team_name) as teams2,
    -- Check if game dates overlap (same person can't play for two teams simultaneously)
    MIN(pgs1_game.game_date) as first_game1,
    MAX(pgs1_game.game_date) as last_game1,
    MIN(pgs2_game.game_date) as first_game2,
    MAX(pgs2_game.game_date) as last_game2,
    CASE 
        WHEN MIN(pgs1_game.game_date) <= MAX(pgs2_game.game_date) 
         AND MAX(pgs1_game.game_date) >= MIN(pgs2_game.game_date)
        THEN 'OVERLAP - Likely different people'
        ELSE 'NO OVERLAP - Could be same person'
    END as date_overlap_analysis
FROM players p1
JOIN players p2 ON p1.player_name = p2.player_name 
    AND p1.player_id < p2.player_id  -- Avoid duplicates in results
    AND p1.api_player_id IS NOT NULL
    AND p2.api_player_id IS NOT NULL
    AND p1.api_player_id != p2.api_player_id  -- Different API IDs
LEFT JOIN player_game_stats pgs1 ON p1.player_id = pgs1.player_id
LEFT JOIN games pgs1_game ON pgs1.game_id = pgs1_game.game_id
LEFT JOIN teams t1 ON pgs1.team_id = t1.team_id
LEFT JOIN player_game_stats pgs2 ON p2.player_id = pgs2.player_id
LEFT JOIN games pgs2_game ON pgs2.game_id = pgs2_game.game_id
LEFT JOIN teams t2 ON pgs2.team_id = t2.team_id
GROUP BY p1.player_id, p2.player_id
ORDER BY p1.player_name, p1.api_player_id;

-- Simpler version: Just find same names with different API IDs
-- Use this for quick checks
SELECT 
    player_name,
    COUNT(DISTINCT api_player_id) as different_api_ids,
    COUNT(*) as total_records,
    GROUP_CONCAT(DISTINCT api_player_id) as api_ids,
    GROUP_CONCAT(DISTINCT player_id) as our_ids
FROM players
WHERE api_player_id IS NOT NULL
GROUP BY player_name
HAVING COUNT(DISTINCT api_player_id) > 1
ORDER BY different_api_ids DESC, player_name;

-- Find players with same API ID but different names
-- This shouldn't happen, but worth checking
SELECT 
    api_player_id,
    COUNT(DISTINCT player_name) as different_names,
    COUNT(*) as total_records,
    GROUP_CONCAT(DISTINCT player_name) as names,
    GROUP_CONCAT(DISTINCT player_id) as our_ids
FROM players
WHERE api_player_id IS NOT NULL
GROUP BY api_player_id
HAVING COUNT(DISTINCT player_name) > 1
ORDER BY different_names DESC;

