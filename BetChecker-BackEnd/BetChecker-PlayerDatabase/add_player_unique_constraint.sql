-- Migration: Add unique constraint on player_name + date_of_birth
-- This prevents duplicate players with the same name and DOB
-- Run this before starting to scrape data

-- First, check for any existing duplicates
SELECT 
    player_name, 
    date_of_birth, 
    COUNT(*) as count 
FROM players 
WHERE date_of_birth IS NOT NULL
GROUP BY player_name, date_of_birth 
HAVING COUNT(*) > 1;

-- If duplicates exist, you'll need to resolve them first
-- Then add the unique index:

CREATE UNIQUE INDEX IF NOT EXISTS idx_player_name_dob ON players(player_name, date_of_birth);

-- Note: This will allow NULL date_of_birth values to have duplicates
-- If you want to prevent that, you can add a partial unique index:
-- CREATE UNIQUE INDEX idx_player_name_dob_not_null 
-- ON players(player_name, date_of_birth) 
-- WHERE date_of_birth IS NOT NULL;

