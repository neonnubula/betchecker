#!/usr/bin/env python3
"""
Systematically test endpoint variations to find the game player statistics endpoint.
Based on documentation: "games > players statistics" with parameters: id, ids, date
"""

import requests
import json
import time
import sys

api_key = sys.argv[1] if len(sys.argv) > 1 else 'fef90da058feb563c00f7b594a69b407'
base_url = "https://v1.afl.api-sports.io"
headers = {
    'x-rapidapi-key': api_key,
    'x-rapidapi-host': 'v1.afl.api-sports.io'
}

game_id = 2524

# Based on docs: "games > players statistics"
# Parameters: id (game id), ids (multiple game ids), date
# Try all possible endpoint variations

endpoint_patterns = [
    # Direct patterns
    '/games-players-statistics',
    '/games_players_statistics',
    '/games/players-statistics',
    '/games/players/statistics',
    '/games-players/statistics',
    
    # Alternative structures
    '/players-statistics-games',
    '/players/games-statistics',
    '/players/games/statistics',
    
    # Maybe it's a parameter on existing endpoints?
    # (We'll test these separately)
]

param_combinations = [
    {'id': game_id},
    {'ids': str(game_id)},
    {'ids': f'{game_id}-{game_id+1}'},
    {'date': '2023-03-16'},
    {'game': game_id},
    {'game_id': game_id},
    {'games': game_id},
]

print("="*80)
print("SYSTEMATIC ENDPOINT TESTING")
print("="*80)
print(f"Testing for game ID: {game_id}")
print(f"Documentation says: 'games > players statistics' with id/ids/date parameters\n")

found_endpoints = []

# Test endpoint patterns
for endpoint in endpoint_patterns:
    for params in param_combinations:
        print(f"\nTesting: {endpoint} with {params}")
        try:
            response = requests.get(f"{base_url}{endpoint}", headers=headers, params=params, timeout=5)
            
            if response.status_code == 200:
                data = response.json()
                
                # Check if endpoint exists (not an "endpoint doesn't exist" error)
                if 'errors' in data:
                    errors = data['errors']
                    if 'endpoint' not in str(errors):
                        # Endpoint exists but parameter might be wrong
                        if 'plan' in str(errors):
                            print(f"  ✅ ENDPOINT EXISTS (needs paid plan): {errors}")
                            found_endpoints.append((endpoint, params, 'needs_paid_plan'))
                        else:
                            print(f"  ⚠️  Endpoint exists, parameter issue: {errors}")
                            found_endpoints.append((endpoint, params, 'parameter_error'))
                    else:
                        print(f"  ❌ Endpoint doesn't exist")
                elif data.get('response'):
                    print(f"  ✅✅✅ SUCCESS! Found {len(data['response'])} entries")
                    print(f"  Sample:")
                    sample = data['response'][0] if isinstance(data['response'], list) else data['response']
                    print(json.dumps(sample, indent=2)[:2000])
                    found_endpoints.append((endpoint, params, 'SUCCESS'))
                    break  # Found it!
                elif data.get('results', 0) > 0:
                    print(f"  ✅ Found {data.get('results')} results")
                    found_endpoints.append((endpoint, params, 'has_results'))
            
            time.sleep(0.5)  # Rate limiting
            
        except Exception as e:
            print(f"  ❌ Exception: {e}")

# Also test if it's a parameter on /players/statistics
print("\n" + "="*80)
print("TESTING /players/statistics WITH GAME PARAMETERS")
print("="*80)

for params in [
    {'game': game_id},
    {'game_id': game_id},
    {'games': game_id},
    {'game_ids': game_id},
    {'id': game_id, 'type': 'game'},  # Maybe id with type discriminator?
]:
    print(f"\nTesting /players/statistics with {params}")
    response = requests.get(f"{base_url}/players/statistics", headers=headers, params=params)
    
    if response.status_code == 200:
        data = response.json()
        if 'errors' in data:
            errors = data['errors']
            if 'endpoint' not in str(errors):
                print(f"  ⚠️  Parameter error (endpoint exists): {errors}")
        elif data.get('response'):
            print(f"  ✅✅✅ SUCCESS!")
            print(json.dumps(data, indent=2)[:4000])
            found_endpoints.append(('/players/statistics', params, 'SUCCESS'))
            break

# Summary
print("\n" + "="*80)
print("SUMMARY")
print("="*80)

if found_endpoints:
    print("\nFound potential endpoints:")
    for endpoint, params, status in found_endpoints:
        print(f"  {endpoint} with {params} - {status}")
else:
    print("\n❌ No working endpoint found")
    print("\nPossible reasons:")
    print("  1. Endpoint requires paid plan")
    print("  2. Endpoint URL structure is different")
    print("  3. Need to check API documentation PDF more carefully")

