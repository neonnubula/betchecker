# Scraping Implementation Guide

## Quick Start

This guide provides step-by-step instructions for implementing the scraping system.

## Prerequisites

1. **Database Setup**: Ensure schema is created and migration applied
2. **Python Dependencies**: 
   ```bash
   pip install requests beautifulsoup4 lxml sqlite3
   ```

## Step 1: Database Manager

Create `BetChecker-BackEnd/database/db_manager.py`:

```python
import sqlite3
from typing import Optional, Tuple
from datetime import date

class DatabaseManager:
    def __init__(self, db_path: str):
        self.db_path = db_path
        self.conn = sqlite3.connect(db_path)
        self.conn.row_factory = sqlite3.Row
    
    def get_or_create_team(self, team_name: str) -> int:
        """Get team_id, create if doesn't exist"""
        cur = self.conn.execute(
            "SELECT team_id FROM teams WHERE team_name = ?",
            (team_name,)
        )
        row = cur.fetchone()
        if row:
            return row['team_id']
        
        cur = self.conn.execute(
            "INSERT INTO teams (team_name, is_active) VALUES (?, 1) RETURNING team_id",
            (team_name,)
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
        date_of_birth: Optional[date] = None,
        first_name: Optional[str] = None,
        last_name: Optional[str] = None,
        debut_year: Optional[int] = None
    ) -> int:
        """
        Get player_id by name + DOB, create if doesn't exist.
        This handles duplicate names by using DOB as unique identifier.
        """
        if date_of_birth:
            # Try to find by name + DOB (most reliable)
            cur = self.conn.execute(
                "SELECT player_id FROM players WHERE player_name = ? AND date_of_birth = ?",
                (player_name, date_of_birth)
            )
            row = cur.fetchone()
            if row:
                return row['player_id']
        else:
            # Fallback: try name only (less reliable, may have duplicates)
            cur = self.conn.execute(
                "SELECT player_id FROM players WHERE player_name = ? AND date_of_birth IS NULL",
                (player_name,)
            )
            row = cur.fetchone()
            if row:
                return row['player_id']
        
        # Create new player
        cur = self.conn.execute(
            """INSERT INTO players 
               (player_name, first_name, last_name, date_of_birth, debut_year) 
               VALUES (?, ?, ?, ?, ?) 
               RETURNING player_id""",
            (player_name, first_name, last_name, date_of_birth, debut_year)
        )
        self.conn.commit()
        return cur.fetchone()['player_id']
    
    def get_or_create_game(
        self,
        season_year: int,
        round_number: Optional[int],
        game_type: str,
        game_date: date,
        game_time: Optional[str],
        venue_id: int,
        home_team_id: int,
        away_team_id: int
    ) -> int:
        """Get game_id, create if doesn't exist"""
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
            return row['game_id']
        
        cur = self.conn.execute(
            """INSERT INTO games 
               (season_year, round_number, game_type, game_date, game_time, 
                venue_id, home_team_id, away_team_id) 
               VALUES (?, ?, ?, ?, ?, ?, ?, ?) 
               RETURNING game_id""",
            (season_year, round_number, game_type, game_date, game_time,
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
```

## Step 2: Base Scraper

Create `BetChecker-BackEnd/scrapers/base_scraper.py`:

```python
import requests
import time
from typing import Optional
from database.db_manager import DatabaseManager

class BaseScraper:
    def __init__(self, db_manager: DatabaseManager, delay: float = 1.0):
        self.db = db_manager
        self.delay = delay
        self.session = requests.Session()
        self.session.headers.update({
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36'
        })
        self.last_request_time = 0
    
    def fetch_page(self, url: str, retries: int = 3) -> Optional[str]:
        """Fetch a page with rate limiting and retries"""
        # Rate limiting
        time_since_last = time.time() - self.last_request_time
        if time_since_last < self.delay:
            time.sleep(self.delay - time_since_last)
        
        for attempt in range(retries):
            try:
                response = self.session.get(url, timeout=10)
                response.raise_for_status()
                self.last_request_time = time.time()
                return response.text
            except requests.RequestException as e:
                if attempt == retries - 1:
                    print(f"Error fetching {url}: {e}")
                    return None
                time.sleep(2 ** attempt)  # Exponential backoff
        
        return None
```

## Step 3: Example Player Scraper

Create `BetChecker-BackEnd/scrapers/players_scraper.py`:

```python
from bs4 import BeautifulSoup
from datetime import datetime
from typing import Optional, Dict
from scrapers.base_scraper import BaseScraper
from database.db_manager import DatabaseManager

class PlayerScraper(BaseScraper):
    def scrape_player_profile(self, player_url: str) -> Optional[Dict]:
        """
        Scrape player profile page.
        Returns dict with: name, dob, first_name, last_name, debut_year
        """
        html = self.fetch_page(player_url)
        if not html:
            return None
        
        soup = BeautifulSoup(html, 'lxml')
        
        # Extract player name (adjust selectors based on actual site)
        name_elem = soup.select_one('.player-name')  # Adjust selector
        if not name_elem:
            return None
        
        full_name = name_elem.get_text(strip=True)
        
        # Extract DOB (adjust selector)
        dob_elem = soup.select_one('.player-dob')  # Adjust selector
        dob = None
        if dob_elem:
            dob_str = dob_elem.get_text(strip=True)
            try:
                dob = datetime.strptime(dob_str, '%d/%m/%Y').date()
            except:
                pass
        
        # Extract first/last name
        name_parts = full_name.split()
        first_name = name_parts[0] if name_parts else None
        last_name = ' '.join(name_parts[1:]) if len(name_parts) > 1 else None
        
        # Extract debut year (adjust selector)
        debut_elem = soup.select_one('.player-debut')  # Adjust selector
        debut_year = None
        if debut_elem:
            try:
                debut_year = int(debut_elem.get_text(strip=True))
            except:
                pass
        
        return {
            'player_name': full_name,
            'date_of_birth': dob,
            'first_name': first_name,
            'last_name': last_name,
            'debut_year': debut_year
        }
    
    def get_or_create_player_from_url(self, player_url: str) -> Optional[int]:
        """Scrape player profile and get/create player in database"""
        player_data = self.scrape_player_profile(player_url)
        if not player_data:
            return None
        
        return self.db.get_or_create_player(
            player_name=player_data['player_name'],
            date_of_birth=player_data['date_of_birth'],
            first_name=player_data['first_name'],
            last_name=player_data['last_name'],
            debut_year=player_data['debut_year']
        )
```

## Step 4: Usage Example

Create `BetChecker-BackEnd/scripts/scrape_example.py`:

```python
from database.db_manager import DatabaseManager
from scrapers.players_scraper import PlayerScraper

# Initialize
db = DatabaseManager('BetChecker-PlayerDatabase/afl_stats.db')
scraper = PlayerScraper(db, delay=2.0)  # 2 second delay between requests

# Example: Scrape a player
player_id = scraper.get_or_create_player_from_url(
    'https://example-site.com/player/scott-pendlebury'
)

print(f"Player ID: {player_id}")

db.close()
```

## Next Steps

1. **Research Data Sources**: Identify which sites have the data you need
2. **Inspect HTML Structure**: Use browser DevTools to find CSS selectors
3. **Test Selectors**: Write small test scripts to verify extraction
4. **Handle Edge Cases**: Missing DOB, name variations, etc.
5. **Add Logging**: Log all operations for debugging
6. **Add Error Recovery**: Handle network errors, missing data gracefully

## Important Notes

- **Always use (name + DOB) for player identification**
- **Check for existing records before inserting**
- **Update team history when team changes**
- **Respect rate limits and robots.txt**
- **Test with small datasets first**
- **Backup database before bulk operations**

