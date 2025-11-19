"""
Database Manager updated for API-Sports.io integration.
Uses API IDs as primary identifiers instead of name + DOB.
"""

import sqlite3
from typing import Optional, Tuple
from datetime import date, datetime

class DatabaseManager:
    def __init__(self, db_path: str):
        self.db_path = db_path
        self.conn = sqlite3.connect(db_path)
        self.conn.row_factory = sqlite3.Row
    
    def get_or_create_team(self, team_name: str, api_team_id: Optional[int] = None) -> int:
        """
        Get team_id, create if doesn't exist.
        If api_team_id provided, use it to match existing teams.
        """
        # First try to find by API ID if provided
        if api_team_id:
            cur = self.conn.execute(
                "SELECT team_id FROM teams WHERE api_team_id = ?",
                (api_team_id,)
            )
            row = cur.fetchone()
            if row:
                return row['team_id']
        
        # Fallback to name matching
        cur = self.conn.execute(
            "SELECT team_id FROM teams WHERE team_name = ?",
            (team_name,)
        )
        row = cur.fetchone()
        if row:
            # Update with API ID if we have it
            if api_team_id:
                self.conn.execute(
                    "UPDATE teams SET api_team_id = ? WHERE team_id = ?",
                    (api_team_id, row['team_id'])
                )
                self.conn.commit()
            return row['team_id']
        
        # Create new team
        cur = self.conn.execute(
            "INSERT INTO teams (team_name, api_team_id, is_active) VALUES (?, ?, 1) RETURNING team_id",
            (team_name, api_team_id)
        )
        self.conn.commit()
        return cur.fetchone()['team_id']
    
    def get_or_create_venue(self, venue_name: str) -> int:
        """Get venue_id, create if doesn't exist"""
        cur = self.conn.execute(
            "SELECT venue_id FROM venues WHERE venue_name = ?",
            (venue_name,)
        )
        row = cur.fetchone()
        if row:
            return row['venue_id']
        
        cur = self.conn.execute(
            "INSERT INTO venues (venue_name) VALUES (?) RETURNING venue_id",
            (venue_name,)
        )
        self.conn.commit()
        return cur.fetchone()['venue_id']
    
    def get_or_create_player(
        self, 
        player_name: str,
        api_player_id: int,  # ⭐ REQUIRED - API player ID
        date_of_birth: Optional[date] = None,
        first_name: Optional[str] = None,
        last_name: Optional[str] = None,
        debut_year: Optional[int] = None
    ) -> int:
        """
        Get player_id by API player ID, create if doesn't exist.
        Uses API ID as primary identifier to handle duplicate names.
        """
        # First check by API ID (primary method)
        cur = self.conn.execute(
            "SELECT player_id FROM players WHERE api_player_id = ?",
            (api_player_id,)
        )
        row = cur.fetchone()
        if row:
            # Update name if it changed (shouldn't happen, but just in case)
            self.conn.execute(
                "UPDATE players SET player_name = ? WHERE player_id = ?",
                (player_name, row['player_id'])
            )
            self.conn.commit()
            return row['player_id']
        
        # Check if name already exists with different API ID (potential duplicate)
        cur = self.conn.execute(
            "SELECT player_id, api_player_id FROM players WHERE player_name = ? AND api_player_id IS NOT NULL",
            (player_name,)
        )
        existing = cur.fetchone()
        if existing and existing['api_player_id'] != api_player_id:
            # Same name, different API ID - potential duplicate
            # Log this for manual review, but still create new player
            print(f"⚠️  WARNING: Player '{player_name}' already exists with API ID {existing['api_player_id']}, "
                  f"but new record has API ID {api_player_id}. Creating new player for manual review.")
        
        # Create new player
        cur = self.conn.execute(
            """INSERT INTO players 
               (player_name, api_player_id, first_name, last_name, date_of_birth, debut_year) 
               VALUES (?, ?, ?, ?, ?, ?) 
               RETURNING player_id""",
            (player_name, api_player_id, first_name, last_name, date_of_birth, debut_year)
        )
        self.conn.commit()
        return cur.fetchone()['player_id']
    
    def get_or_create_game(
        self,
        api_game_id: int,  # ⭐ REQUIRED - API game ID
        season_year: int,
        round_number: Optional[int],
        game_type: str,
        game_date: date,
        game_time: Optional[str],
        venue_id: int,
        home_team_id: int,
        away_team_id: int
    ) -> int:
        """Get game_id by API game ID, create if doesn't exist"""
        # Check by API game ID first
        cur = self.conn.execute(
            "SELECT game_id FROM games WHERE api_game_id = ?",
            (api_game_id,)
        )
        row = cur.fetchone()
        if row:
            return row['game_id']
        
        # Fallback: check by date + teams (in case API ID missing)
        cur = self.conn.execute(
            """SELECT game_id FROM games 
               WHERE season_year = ? 
               AND round_number IS ? 
               AND game_date = ? 
               AND home_team_id = ? 
               AND away_team_id = ?""",
            (season_year, round_number, game_date, home_team_id, away_team_id)
        )
        row = cur.fetchone()
        if row:
            # Update with API ID
            self.conn.execute(
                "UPDATE games SET api_game_id = ? WHERE game_id = ?",
                (api_game_id, row['game_id'])
            )
            self.conn.commit()
            return row['game_id']
        
        # Create new game
        cur = self.conn.execute(
            """INSERT INTO games 
               (api_game_id, season_year, round_number, game_type, game_date, game_time, 
                venue_id, home_team_id, away_team_id) 
               VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?) 
               RETURNING game_id""",
            (api_game_id, season_year, round_number, game_type, game_date, game_time,
             venue_id, home_team_id, away_team_id)
        )
        self.conn.commit()
        return cur.fetchone()['game_id']
    
    def insert_player_stats(
        self,
        player_id: int,
        game_id: int,
        team_id: int,
        opponent_team_id: int,
        venue_id: int,
        location: str,
        game_time: Optional[str],
        disposals: int,
        goals: int
    ) -> int:
        """
        Insert player stats and handle team history updates.
        Returns stat_id.
        """
        # Check if stats already exist
        cur = self.conn.execute(
            "SELECT stat_id FROM player_game_stats WHERE player_id = ? AND game_id = ?",
            (player_id, game_id)
        )
        existing = cur.fetchone()
        if existing:
            return existing['stat_id']
        
        # Get game date for team history check
        cur = self.conn.execute(
            "SELECT game_date FROM games WHERE game_id = ?",
            (game_id,)
        )
        game_date = cur.fetchone()['game_date']
        
        # Check if team changed
        cur = self.conn.execute(
            """SELECT team_id FROM player_game_stats 
               WHERE player_id = ? 
               ORDER BY game_id DESC LIMIT 1""",
            (player_id,)
        )
        last_game = cur.fetchone()
        
        if last_game and last_game['team_id'] != team_id:
            # Team changed! Update player_team_history
            self.conn.execute(
                """UPDATE player_team_history 
                   SET end_date = ?, is_current = 0 
                   WHERE player_id = ? AND is_current = 1""",
                (game_date, player_id)
            )
            
            self.conn.execute(
                """INSERT INTO player_team_history 
                   (player_id, team_id, start_date, is_current) 
                   VALUES (?, ?, ?, 1)""",
                (player_id, team_id, game_date)
            )
        elif not last_game:
            # First game for this player - create initial team history
            self.conn.execute(
                """INSERT INTO player_team_history 
                   (player_id, team_id, start_date, is_current) 
                   VALUES (?, ?, ?, 1)""",
                (player_id, team_id, game_date)
            )
        
        # Insert stats
        cur = self.conn.execute(
            """INSERT INTO player_game_stats 
               (player_id, game_id, team_id, opponent_team_id, venue_id, 
                location, game_time, disposals, goals) 
               VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?) 
               RETURNING stat_id""",
            (player_id, game_id, team_id, opponent_team_id, venue_id,
             location, game_time, disposals, goals)
        )
        self.conn.commit()
        return cur.fetchone()['stat_id']
    
    def find_potential_duplicates(self) -> list:
        """
        Find players with same name but different API IDs.
        Returns list of potential duplicates for manual review.
        """
        cur = self.conn.execute("""
            SELECT 
                player_name,
                COUNT(DISTINCT api_player_id) as different_api_ids,
                COUNT(*) as total_records,
                GROUP_CONCAT(DISTINCT api_player_id) as api_ids,
                GROUP_CONCAT(DISTINCT player_id) as our_ids,
                GROUP_CONCAT(DISTINCT date_of_birth) as birth_dates
            FROM players
            WHERE api_player_id IS NOT NULL
            GROUP BY player_name
            HAVING COUNT(DISTINCT api_player_id) > 1
            ORDER BY different_api_ids DESC, player_name
        """)
        return [dict(row) for row in cur.fetchall()]
    
    def update_days_since_last_game(self):
        """Calculate and update days_since_last_game for all stats"""
        self.conn.execute("""
            WITH ranked_games AS (
                SELECT 
                    pgs.stat_id,
                    pgs.player_id,
                    pgs.game_id,
                    g.game_date,
                    LAG(g.game_date) OVER (
                        PARTITION BY pgs.player_id 
                        ORDER BY g.game_date
                    ) as prev_game_date
                FROM player_game_stats pgs
                JOIN games g ON pgs.game_id = g.game_id
            )
            UPDATE player_game_stats
            SET days_since_last_game = (
                SELECT JULIANDAY(rg.game_date) - JULIANDAY(rg.prev_game_date)
                FROM ranked_games rg
                WHERE rg.stat_id = player_game_stats.stat_id
            )
        """)
        self.conn.commit()
    
    def close(self):
        self.conn.close()

