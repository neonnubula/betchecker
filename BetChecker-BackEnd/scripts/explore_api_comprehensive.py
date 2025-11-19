#!/usr/bin/env python3
"""
Comprehensive API exploration script.
Tests all possible endpoints and documents what's actually available.
"""

import requests
import json
import sys
from typing import Dict, List, Optional

class APIExplorer:
    def __init__(self, api_key: str):
        self.api_key = api_key
        self.base_url = "https://v1.afl.api-sports.io"
        self.headers = {
            'x-rapidapi-key': api_key,
            'x-rapidapi-host': 'v1.afl.api-sports.io'
        }
        self.findings = {
            'endpoints': {},
            'data_structures': {},
            'available_fields': {}
        }
    
    def test_endpoint(self, endpoint: str, params: Optional[Dict] = None, description: str = "") -> Optional[Dict]:
        """Test an endpoint and document results"""
        url = f"{self.base_url}{endpoint}"
        print(f"\n{'='*80}")
        print(f"Testing: {endpoint}")
        if description:
            print(f"Purpose: {description}")
        if params:
            print(f"Params: {params}")
        print(f"{'='*80}")
        
        try:
            response = requests.get(url, headers=self.headers, params=params, timeout=10)
            print(f"Status: {response.status_code}")
            
            if response.status_code == 200:
                data = response.json()
                
                # Check for errors
                if 'errors' in data and data['errors']:
                    print(f"⚠️  Errors: {data['errors']}")
                    self.findings['endpoints'][endpoint] = {
                        'status': 'error',
                        'errors': data['errors'],
                        'params': params
                    }
                    return None
                
                # Document successful response
                if 'response' in data and data['response']:
                    sample = data['response'][0] if isinstance(data['response'], list) else data['response']
                    print(f"✅ Success - Found {data.get('results', 0)} results")
                    print(f"\nSample response structure:")
                    print(json.dumps(sample, indent=2)[:3000])
                    
                    self.findings['endpoints'][endpoint] = {
                        'status': 'success',
                        'results': data.get('results', 0),
                        'sample': sample,
                        'params': params
                    }
                    
                    # Extract field names
                    if isinstance(sample, dict):
                        self.findings['data_structures'][endpoint] = list(sample.keys())
                    
                    return data
                else:
                    print("⚠️  Empty response")
                    self.findings['endpoints'][endpoint] = {
                        'status': 'empty',
                        'params': params
                    }
                    return data
            else:
                print(f"❌ Failed: {response.status_code}")
                print(response.text[:500])
                return None
                
        except Exception as e:
            print(f"❌ Exception: {e}")
            return None
    
    def explore_all(self):
        """Explore all possible endpoints"""
        print("="*80)
        print("COMPREHENSIVE API EXPLORATION")
        print("="*80)
        
        # Get a sample game ID and player ID first
        print("\n🔍 Getting sample IDs...")
        games_resp = self.test_endpoint("/games", {"season": 2023, "league": 1}, "Get sample games")
        sample_game_id = None
        if games_resp and games_resp.get('response'):
            sample_game_id = games_resp['response'][0].get('game', {}).get('id')
            print(f"✅ Sample game ID: {sample_game_id}")
        
        players_resp = self.test_endpoint("/players", {"team": 4, "season": 2023}, "Get sample players")
        sample_player_id = None
        if players_resp and players_resp.get('response'):
            sample_player_id = players_resp['response'][0].get('id')
            print(f"✅ Sample player ID: {sample_player_id}")
        
        # Now test various endpoint patterns
        endpoints_to_test = [
            # Base endpoints
            ("/teams", None, "Get all teams"),
            ("/leagues", None, "Get leagues"),
            ("/seasons", None, "Get available seasons"),
            
            # Players endpoints
            ("/players", {"id": sample_player_id}, "Get player by ID"),
            ("/players", {"name": "Pendlebury"}, "Search player by name"),
            ("/players", {"team": 4}, "Get players by team"),
            ("/players", {"season": 2023}, "Get players by season"),
            ("/players", {"team": 4, "season": 2023}, "Get players by team and season"),
            
            # Games endpoints
            ("/games", {"id": sample_game_id}, "Get game by ID"),
            ("/games", {"season": 2023, "league": 1}, "Get games by season"),
            ("/games", {"team": 4, "season": 2023}, "Get games by team"),
            ("/games", {"date": "2023-03-16"}, "Get games by date"),
            
            # Statistics endpoints (various patterns)
            ("/players/statistics", {"player": sample_player_id}, "Player statistics"),
            ("/players/statistics", {"player": sample_player_id, "season": 2023}, "Player statistics by season"),
            ("/statistics", {"player": sample_player_id}, "Statistics endpoint"),
            ("/statistics/players", {"player": sample_player_id}, "Statistics players"),
            
            # Game-related endpoints
            (f"/games/{sample_game_id}", None, "Get game details"),
            (f"/games/{sample_game_id}/players", None, "Get game players"),
            (f"/games/{sample_game_id}/statistics", None, "Get game statistics"),
            (f"/games/{sample_game_id}/events", None, "Get game events"),
            
            # Player-related endpoints
            (f"/players/{sample_player_id}", None, "Get player details"),
            (f"/players/{sample_player_id}/statistics", None, "Get player statistics"),
            (f"/players/{sample_player_id}/games", None, "Get player games"),
            (f"/players/{sample_player_id}/injuries", None, "Get player injuries"),
            
            # Standings/Table
            ("/standings", {"season": 2023, "league": 1}, "Get standings"),
            ("/standings", {"season": 2021, "league": 1}, "Get standings (free tier season)"),
            
            # Other potential endpoints
            ("/venues", None, "Get venues"),
            ("/rounds", {"season": 2023}, "Get rounds"),
            ("/fixtures", {"season": 2023}, "Get fixtures (alternative name)"),
        ]
        
        for endpoint, params, desc in endpoints_to_test:
            if endpoint and (not endpoint.startswith('/games/') or sample_game_id):
                self.test_endpoint(endpoint, params, desc)
        
        # Print summary
        self.print_summary()
    
    def print_summary(self):
        """Print summary of findings"""
        print("\n" + "="*80)
        print("EXPLORATION SUMMARY")
        print("="*80)
        
        print("\n✅ WORKING ENDPOINTS:")
        for endpoint, info in self.findings['endpoints'].items():
            if info.get('status') == 'success':
                print(f"  {endpoint}")
                if 'results' in info:
                    print(f"    - Results: {info['results']}")
                if 'sample' in info:
                    print(f"    - Fields: {list(info['sample'].keys()) if isinstance(info['sample'], dict) else 'N/A'}")
        
        print("\n❌ FAILED ENDPOINTS:")
        for endpoint, info in self.findings['endpoints'].items():
            if info.get('status') == 'error':
                print(f"  {endpoint}")
                if 'errors' in info:
                    print(f"    - Error: {info['errors']}")
        
        print("\n📊 DATA STRUCTURES FOUND:")
        for endpoint, fields in self.findings['data_structures'].items():
            print(f"  {endpoint}:")
            for field in fields:
                print(f"    - {field}")
        
        # Save findings to file
        with open('api_findings.json', 'w') as f:
            json.dump(self.findings, f, indent=2, default=str)
        print(f"\n💾 Full findings saved to: api_findings.json")


if __name__ == "__main__":
    if len(sys.argv) < 2:
        print("Usage: python explore_api_comprehensive.py YOUR_API_KEY")
        sys.exit(1)
    
    api_key = sys.argv[1]
    explorer = APIExplorer(api_key)
    explorer.explore_all()

