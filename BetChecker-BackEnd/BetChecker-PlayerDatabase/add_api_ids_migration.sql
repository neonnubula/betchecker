-- Migration: Add API IDs to support API-Sports.io integration
-- Run this before starting to scrape from the API

-- Add api_player_id to players table
ALTER TABLE players ADD COLUMN api_player_id INTEGER;
CREATE UNIQUE INDEX IF NOT EXISTS idx_players_api_id ON players(api_player_id);

-- Add api_game_id to games table  
ALTER TABLE games ADD COLUMN api_game_id INTEGER;
CREATE UNIQUE INDEX IF NOT EXISTS idx_games_api_id ON games(api_game_id);

-- Note: Teams already use IDs that match API team IDs, so no change needed
-- But we can add api_team_id for consistency if desired:
-- ALTER TABLE teams ADD COLUMN api_team_id INTEGER;
-- CREATE UNIQUE INDEX IF NOT EXISTS idx_teams_api_id ON teams(api_team_id);

-- Update existing data (if any) - set api_player_id = player_id for existing records
-- This assumes existing player_ids might match API IDs
-- UPDATE players SET api_player_id = player_id WHERE api_player_id IS NULL;

