#!/usr/bin/env python3
"""
Test script to find potential duplicate players.
Players with same name but different API IDs need manual review.
"""

import sys
from pathlib import Path

# Add parent directory to path
sys.path.insert(0, str(Path(__file__).parent.parent))

from database.db_manager_api import DatabaseManager

def test_duplicate_players(db_path: str):
    """Find and display potential duplicate players"""
    db = DatabaseManager(db_path)
    
    print("="*80)
    print("POTENTIAL DUPLICATE PLAYERS TEST")
    print("="*80)
    print("\nLooking for players with same name but different API IDs...")
    print("These need manual review to determine if they're the same person.\n")
    
    duplicates = db.find_potential_duplicates()
    
    if not duplicates:
        print("✅ No potential duplicates found!")
        print("All players with same name have the same API ID.")
    else:
        print(f"⚠️  Found {len(duplicates)} potential duplicate cases:\n")
        
        for dup in duplicates:
            print(f"Player Name: {dup['player_name']}")
            print(f"  Different API IDs: {dup['different_api_ids']}")
            print(f"  Total Records: {dup['total_records']}")
            print(f"  API IDs: {dup['api_ids']}")
            print(f"  Our Player IDs: {dup['our_ids']}")
            if dup['birth_dates']:
                print(f"  Birth Dates: {dup['birth_dates']}")
            print()
        
        print("\n" + "="*80)
        print("MANUAL REVIEW REQUIRED")
        print("="*80)
        print("\nFor each case above:")
        print("1. Check if the API IDs refer to the same person")
        print("2. If yes: Merge the records (keep one, update stats to point to it)")
        print("3. If no: They're different people with same name (no action needed)")
        print("\nTo merge:")
        print("  UPDATE player_game_stats SET player_id = <keep_id> WHERE player_id = <duplicate_id>;")
        print("  DELETE FROM players WHERE player_id = <duplicate_id>;")
    
    db.close()

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
    
    print(f"Using database: {db_path}\n")
    test_duplicate_players(db_path)

