#!/usr/bin/env python3
"""
Test script to explore API-Sports.io AFL API structure.

This script helps you:
1. Test API connectivity
2. Inspect response structure
3. Identify available endpoints
4. Map fields to our database schema

Usage:
    python scripts/test_api_sports.py YOUR_API_KEY
"""

import requests
import json
import sys
from typing import Optional, Dict

class APISportsTester:
    def __init__(self, api_key: str):
        self.api_key = api_key
        self.base_url = "https://v1.afl.api-sports.io"
        self.headers = {
            'x-rapidapi-key': api_key,
            'x-rapidapi-host': 'v1.afl.api-sports.io'
        }
    
    def test_endpoint(self, endpoint: str, params: Optional[Dict] = None) -> Optional[Dict]:
        """Test an API endpoint and return response"""
        url = f"{self.base_url}{endpoint}"
        print(f"\n{'='*80}")
        print(f"Testing: {endpoint}")
        print(f"URL: {url}")
        if params:
            print(f"Params: {params}")
        print(f"{'='*80}")
        
        try:
            response = requests.get(url, headers=self.headers, params=params, timeout=10)
            print(f"Status Code: {response.status_code}")
            
            if response.status_code == 200:
                data = response.json()
                print(f"Response keys: {list(data.keys()) if isinstance(data, dict) else 'Not a dict'}")
                print(f"\nResponse (formatted):")
                print(json.dumps(data, indent=2)[:2000])  # First 2000 chars
                return data
            elif response.status_code == 429:
                print("❌ Rate limit exceeded. Wait before trying again.")
                return None
            elif response.status_code == 401:
                print("❌ Unauthorized. Check your API key.")
                return None
            else:
                print(f"❌ Error: {response.status_code}")
                print(response.text[:500])
                return None
                
        except requests.RequestException as e:
            print(f"❌ Request failed: {e}")
            return None
    
    def explore_api(self):
        """Explore available endpoints"""
        print("Exploring API-Sports.io AFL API")
        print("="*80)
        
        # Test common endpoints
        endpoints_to_test = [
            ("/teams", None),
            ("/players", None),
            ("/players/search", {"name": "Pendlebury"}),
            ("/fixtures", {"season": 2024}),
            ("/standings", {"season": 2024}),
        ]
        
        results = {}
        for endpoint, params in endpoints_to_test:
            result = self.test_endpoint(endpoint, params)
            if result:
                results[endpoint] = result
            print("\n" + "-"*80)
        
        return results
    
    def analyze_player_structure(self, player_data: Dict):
        """Analyze player data structure"""
        print("\n" + "="*80)
        print("PLAYER DATA STRUCTURE ANALYSIS")
        print("="*80)
        
        def print_structure(obj, prefix="", max_depth=3, current_depth=0):
            if current_depth >= max_depth:
                return
            
            if isinstance(obj, dict):
                for key, value in obj.items():
                    if isinstance(value, (dict, list)):
                        print(f"{prefix}{key}: {type(value).__name__}")
                        print_structure(value, prefix + "  ", max_depth, current_depth + 1)
                    else:
                        print(f"{prefix}{key}: {type(value).__name__} = {value}")
            elif isinstance(obj, list) and len(obj) > 0:
                print(f"{prefix}[0]: {type(obj[0]).__name__}")
                print_structure(obj[0], prefix + "  ", max_depth, current_depth + 1)
        
        print_structure(player_data)
    
    def check_dob_availability(self, player_data: Dict) -> bool:
        """Check if date of birth is available in player data"""
        print("\n" + "="*80)
        print("CHECKING FOR DATE OF BIRTH")
        print("="*80)
        
        # Common field names for DOB
        dob_fields = ['birth', 'date_of_birth', 'dob', 'birthdate', 'birthDate']
        
        def find_dob(obj, path=""):
            if isinstance(obj, dict):
                for key, value in obj.items():
                    current_path = f"{path}.{key}" if path else key
                    if key.lower() in dob_fields:
                        print(f"✅ Found DOB at: {current_path} = {value}")
                        return True, current_path, value
                    if isinstance(value, (dict, list)):
                        found, found_path, found_value = find_dob(value, current_path)
                        if found:
                            return True, found_path, found_value
            elif isinstance(obj, list):
                for i, item in enumerate(obj):
                    found, found_path, found_value = find_dob(item, f"{path}[{i}]")
                    if found:
                        return True, found_path, found_value
            return False, None, None
        
        found, path, value = find_dob(player_data)
        if not found:
            print("❌ Date of birth not found in player data")
            print("Available fields:")
            print(json.dumps(player_data, indent=2)[:1000])
        return found


if __name__ == "__main__":
    if len(sys.argv) < 2:
        print("Usage: python test_api_sports.py YOUR_API_KEY")
        print("\nGet your API key from: https://dashboard.api-sports.io")
        sys.exit(1)
    
    api_key = sys.argv[1]
    tester = APISportsTester(api_key)
    
    # Explore the API
    results = tester.explore_api()
    
    # If we got player data, analyze it
    if 'players' in results or '/players' in results:
        player_data = results.get('players') or results.get('/players')
        if player_data:
            tester.analyze_player_structure(player_data)
            tester.check_dob_availability(player_data)
    
    print("\n" + "="*80)
    print("EXPLORATION COMPLETE")
    print("="*80)
    print("\nNext steps:")
    print("1. Review the response structures above")
    print("2. Map fields to our database schema")
    print("3. Update API_SPORTS_IO_GUIDE.md with actual structure")
    print("4. Build the scraper based on real API responses")

