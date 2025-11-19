#!/usr/bin/env python3
"""
Run all data validation tests and generate a report.

Usage:
    python scripts/run_validation_tests.py
"""

import sqlite3
import sys
from pathlib import Path

# Add parent directory to path
sys.path.insert(0, str(Path(__file__).parent.parent))


class ValidationTester:
    def __init__(self, db_path: str):
        self.db_path = db_path
        self.conn = sqlite3.connect(db_path)
        self.conn.row_factory = sqlite3.Row
        self.results = []
    
    def run_test(self, test_name: str, query: str, expected: str):
        """Run a test and record results"""
        try:
            cursor = self.conn.execute(query)
            rows = cursor.fetchall()
            passed = len(rows) == 0 if expected == "0 rows" else True
            
            self.results.append({
                'test': test_name,
                'passed': passed,
                'row_count': len(rows),
                'expected': expected,
                'sample_rows': rows[:3]  # First 3 rows for inspection
            })
        except Exception as e:
            self.results.append({
                'test': test_name,
                'passed': False,
                'error': str(e)
            })
    
    def run_all_tests(self):
        """Run all validation tests"""
        
        # Test 1: Duplicate players (same name + DOB)
        self.run_test(
            "Duplicate Players (Same Name + DOB)",
            """
            SELECT player_name, date_of_birth, COUNT(*) as count
            FROM players
            WHERE date_of_birth IS NOT NULL
            GROUP BY player_name, date_of_birth
            HAVING COUNT(*) > 1
            """,
            "0 rows"
        )
        
        # Test 2: Duplicate game stats
        self.run_test(
            "Duplicate Game Stats",
            """
            SELECT player_id, game_id, COUNT(*) as count
            FROM player_game_stats
            GROUP BY player_id, game_id
            HAVING COUNT(*) > 1
            """,
            "0 rows"
        )
        
        # Test 3: Team assignment validation
        self.run_test(
            "Invalid Team Assignments",
            """
            SELECT pgs.stat_id
            FROM player_game_stats pgs
            JOIN games g ON pgs.game_id = g.game_id
            WHERE pgs.team_id NOT IN (g.home_team_id, g.away_team_id)
            """,
            "0 rows"
        )
        
        # Test 4: Opponent validation
        self.run_test(
            "Invalid Opponent Teams",
            """
            SELECT stat_id
            FROM player_game_stats
            WHERE team_id = opponent_team_id
            """,
            "0 rows"
        )
        
        # Test 5: Multiple current teams
        self.run_test(
            "Multiple Current Teams",
            """
            SELECT player_id, COUNT(*) as count
            FROM player_team_history
            WHERE is_current = 1
            GROUP BY player_id
            HAVING COUNT(*) > 1
            """,
            "0 rows"
        )
        
        # Test 6: Players without DOB (count only)
        cursor = self.conn.execute("""
            SELECT COUNT(*) as count
            FROM players
            WHERE date_of_birth IS NULL
        """)
        missing_dob = cursor.fetchone()['count']
        
        total_players_cursor = self.conn.execute("SELECT COUNT(*) as count FROM players")
        total_players = total_players_cursor.fetchone()['count']
        missing_dob_pct = (missing_dob / total_players * 100) if total_players > 0 else 0
        
        self.results.append({
            'test': "Players Without DOB",
            'passed': missing_dob_pct < 5.0,  # Less than 5% missing
            'row_count': missing_dob,
            'expected': f"< 5% ({missing_dob_pct:.2f}% missing)"
        })
        
        # Test 7: Same name, different DOB (valid duplicates - just report)
        cursor = self.conn.execute("""
            SELECT 
                player_name,
                COUNT(DISTINCT date_of_birth) as different_dobs,
                COUNT(*) as total_players
            FROM players
            WHERE date_of_birth IS NOT NULL
            GROUP BY player_name
            HAVING COUNT(DISTINCT date_of_birth) > 1
        """)
        same_name_different_dob = cursor.fetchall()
        
        self.results.append({
            'test': "Same Name, Different DOB (Valid Duplicates)",
            'passed': True,  # This is expected and correct
            'row_count': len(same_name_different_dob),
            'expected': "> 0 rows (expected)",
            'sample_rows': same_name_different_dob[:3]
        })
        
        # Test 8: Venue consistency
        self.run_test(
            "Venue Consistency",
            """
            SELECT pgs.stat_id
            FROM player_game_stats pgs
            JOIN games g ON pgs.game_id = g.game_id
            WHERE pgs.venue_id != g.venue_id
            """,
            "0 rows"
        )
        
        # Test 9: Statistical outliers (negative values)
        self.run_test(
            "Negative Stat Values",
            """
            SELECT stat_id, disposals, goals
            FROM player_game_stats
            WHERE disposals < 0 OR goals < 0
            """,
            "0 rows"
        )
    
    def print_report(self):
        """Print test results report"""
        print("=" * 80)
        print("DATA VALIDATION TEST REPORT")
        print("=" * 80)
        print()
        
        passed = sum(1 for r in self.results if r.get('passed', False))
        total = len(self.results)
        
        for result in self.results:
            status = "✅ PASS" if result.get('passed', False) else "❌ FAIL"
            print(f"{status} - {result['test']}")
            
            if 'error' in result:
                print(f"   Error: {result['error']}")
            elif 'row_count' in result:
                print(f"   Found: {result['row_count']} rows (Expected: {result['expected']})")
                if result['row_count'] > 0 and result.get('sample_rows'):
                    print("   Sample rows:")
                    for row in result['sample_rows']:
                        print(f"     {dict(row)}")
            print()
        
        print("=" * 80)
        print(f"Summary: {passed}/{total} tests passed")
        print("=" * 80)
        
        # Additional statistics
        print()
        print("DATABASE STATISTICS:")
        print("-" * 80)
        
        stats_queries = [
            ("Total Players", "SELECT COUNT(*) as count FROM players"),
            ("Players with DOB", "SELECT COUNT(*) as count FROM players WHERE date_of_birth IS NOT NULL"),
            ("Total Games", "SELECT COUNT(*) as count FROM games"),
            ("Total Player Stats", "SELECT COUNT(*) as count FROM player_game_stats"),
            ("Total Teams", "SELECT COUNT(*) as count FROM teams"),
            ("Total Venues", "SELECT COUNT(*) as count FROM venues"),
        ]
        
        for stat_name, query in stats_queries:
            cursor = self.conn.execute(query)
            count = cursor.fetchone()['count']
            print(f"  {stat_name}: {count}")
    
    def close(self):
        self.conn.close()


if __name__ == "__main__":
    # Try to find database in common locations
    possible_paths = [
        "BetChecker-PlayerDatabase/afl_stats.db",
        "BetChecker-BackEnd/BetChecker-PlayerDatabase/afl_stats.db",
        "../BetChecker-PlayerDatabase/afl_stats.db",
        "afl_stats.db"
    ]
    
    db_path = None
    for path in possible_paths:
        if Path(path).exists():
            db_path = path
            break
    
    if not db_path:
        print("Error: Database not found. Tried:")
        for path in possible_paths:
            print(f"  - {path}")
        sys.exit(1)
    
    print(f"Using database: {db_path}")
    print()
    
    tester = ValidationTester(db_path)
    tester.run_all_tests()
    tester.print_report()
    tester.close()

