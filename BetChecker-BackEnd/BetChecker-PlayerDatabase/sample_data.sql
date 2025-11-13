-- Sample data for AFL Statistics Database
-- This file demonstrates how to insert data into the database

-- ============================================================================
-- INSERT TEAMS
-- ============================================================================

INSERT INTO teams (team_name, is_active) VALUES
('Collingwood', 1),
('Richmond', 1),
('Geelong', 1),
('Carlton', 1),
('Essendon', 1),
('Hawthorn', 1),
('Melbourne', 1),
('Sydney', 1),
('West Coast Eagles', 1),
('Brisbane Lions', 1),
('Adelaide', 1),
('Fremantle', 1),
('Port Adelaide', 1),
('Western Bulldogs', 1),
('North Melbourne', 1),
('St Kilda', 1),
('Gold Coast', 1),
('Greater Western Sydney', 1);

-- ============================================================================
-- INSERT VENUES
-- ============================================================================

INSERT INTO venues (venue_name) VALUES
('MCG'),
('Marvel Stadium'),
('Adelaide Oval'),
('SCG'),
('Gabba'),
('Optus Stadium'),
('GMHBA Stadium'),
('Giants Stadium'),
('Metricon Stadium'),
('TIO Stadium'),
('Bellerive Oval'),
('Manuka Oval');

-- ============================================================================
-- INSERT SAMPLE PLAYERS
-- ============================================================================

INSERT INTO players (player_name, first_name, last_name, date_of_birth, debut_year) VALUES
('Scott Pendlebury', 'Scott', 'Pendlebury', '1988-01-07', 2006),
('Steele Sidebottom', 'Steele', 'Sidebottom', '1991-01-02', 2009),
('Dane Swan', 'Dane', 'Swan', '1984-02-25', 2003),
('Dustin Martin', 'Dustin', 'Martin', '1991-06-26', 2010),
('Patrick Dangerfield', 'Patrick', 'Dangerfield', '1990-04-05', 2008),
('Joel Selwood', 'Joel', 'Selwood', '1988-05-26', 2007),
('Lance Franklin', 'Lance', 'Franklin', '1987-01-30', 2005),
('Marcus Bontempelli', 'Marcus', 'Bontempelli', '1995-11-24', 2014);

-- ============================================================================
-- INSERT SAMPLE GAMES
-- ============================================================================

-- Round 1, 2023 - Collingwood vs Carlton at MCG
INSERT INTO games (season_year, round_number, game_type, game_date, game_time, venue_id, home_team_id, away_team_id)
VALUES (2023, 1, 'Regular Season', '2023-03-16', '19:20', 1, 1, 4);

-- Round 1, 2023 - Richmond vs Geelong at MCG
INSERT INTO games (season_year, round_number, game_type, game_date, game_time, venue_id, home_team_id, away_team_id)
VALUES (2023, 1, 'Regular Season', '2023-03-17', '19:20', 1, 2, 3);

-- Round 2, 2023 - Collingwood vs Melbourne at MCG
INSERT INTO games (season_year, round_number, game_type, game_date, game_time, venue_id, home_team_id, away_team_id)
VALUES (2023, 2, 'Regular Season', '2023-03-24', '19:20', 1, 1, 7);

-- ============================================================================
-- INSERT SAMPLE PLAYER GAME STATS
-- ============================================================================

-- Scott Pendlebury - Round 1, 2023 vs Carlton at MCG (Night game)
INSERT INTO player_game_stats (player_id, game_id, team_id, opponent_team_id, venue_id, location, game_time, disposals, goals)
VALUES (1, 1, 1, 4, 1, 'Home', 'Night', 32, 1);

-- Steele Sidebottom - Round 1, 2023 vs Carlton at MCG (Night game)
INSERT INTO player_game_stats (player_id, game_id, team_id, opponent_team_id, venue_id, location, game_time, disposals, goals)
VALUES (2, 1, 1, 4, 1, 'Home', 'Night', 28, 0);

-- Dustin Martin - Round 1, 2023 vs Geelong at MCG (Night game)
INSERT INTO player_game_stats (player_id, game_id, team_id, opponent_team_id, venue_id, location, game_time, disposals, goals)
VALUES (4, 2, 2, 3, 1, 'Home', 'Night', 25, 2);

-- Patrick Dangerfield - Round 1, 2023 vs Richmond at MCG (Night game, Away)
INSERT INTO player_game_stats (player_id, game_id, team_id, opponent_team_id, venue_id, location, game_time, disposals, goals)
VALUES (5, 2, 3, 2, 1, 'Away', 'Night', 31, 3);

-- Scott Pendlebury - Round 2, 2023 vs Melbourne at MCG (Night game)
INSERT INTO player_game_stats (player_id, game_id, team_id, opponent_team_id, venue_id, location, game_time, disposals, goals, days_since_last_game)
VALUES (1, 3, 1, 7, 1, 'Home', 'Night', 29, 0, 8);

-- ============================================================================
-- INSERT PLAYER TEAM HISTORY
-- ============================================================================

INSERT INTO player_team_history (player_id, team_id, start_date, end_date, is_current) VALUES
(1, 1, '2006-05-05', NULL, 1),  -- Scott Pendlebury - Collingwood (current)
(2, 1, '2009-04-09', NULL, 1),  -- Steele Sidebottom - Collingwood (current)
(3, 1, '2003-05-09', '2016-09-03', 0),  -- Dane Swan - Collingwood (retired)
(4, 2, '2010-04-01', NULL, 1),  -- Dustin Martin - Richmond (current)
(5, 11, '2008-05-10', '2015-10-31', 0),  -- Patrick Dangerfield - Adelaide
(5, 3, '2016-03-26', NULL, 1),  -- Patrick Dangerfield - Geelong (current)
(6, 3, '2007-04-22', '2022-08-06', 0),  -- Joel Selwood - Geelong (retired)
(7, 6, '2005-03-26', '2013-10-13', 0),  -- Lance Franklin - Hawthorn
(7, 8, '2014-03-22', NULL, 1),  -- Lance Franklin - Sydney (current)
(8, 14, '2014-03-30', NULL, 1);  -- Marcus Bontempelli - Western Bulldogs (current)

-- ============================================================================
-- CALCULATE DAYS SINCE LAST GAME
-- ============================================================================

-- This query calculates the days_since_last_game field for all stats
-- Run this after inserting new data

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
)
WHERE stat_id IN (SELECT stat_id FROM ranked_games WHERE prev_game_date IS NOT NULL);

