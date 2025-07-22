#!/usr/bin/env python3
"""
Create mock F1 leaderboard data for testing Supabase sync.
"""

import os
import sys
import random
from datetime import datetime, timedelta

# Add the project root to the Python path
root_dir = os.path.abspath(os.path.join(os.path.dirname(__file__), ".."))
sys.path.append(root_dir)

from backend.database.db_manager import add_lap_time, assign_player_to_rig, get_db_connection

# Mock player data
MOCK_PLAYERS = [
    {"name": "Alex Johnson", "phone": "+1-555-0101", "email": "alex.johnson@email.com"},
    {"name": "Sarah Chen", "phone": "+1-555-0102", "email": "sarah.chen@email.com"},
    {"name": "Mike Rodriguez", "phone": "+1-555-0103", "email": "mike.rodriguez@email.com"},
    {"name": "Emma Thompson", "phone": "+1-555-0104", "email": "emma.thompson@email.com"},
    {"name": "David Park", "phone": "+1-555-0105", "email": "david.park@email.com"},
    {"name": "Lisa Wang", "phone": "+1-555-0106", "email": "lisa.wang@email.com"},
    {"name": "Tom Anderson", "phone": "+1-555-0107", "email": "tom.anderson@email.com"},
    {"name": "Maria Garcia", "phone": "+1-555-0108", "email": "maria.garcia@email.com"},
]

# Mock tracks with realistic lap time ranges (in milliseconds)
TRACK_LAP_TIMES = {
    "Bahrain International Circuit": (88000, 95000),  # 1:28 - 1:35
    "Jeddah Corniche Circuit": (78000, 85000),        # 1:18 - 1:25  
    "Albert Park Circuit": (80000, 87000),            # 1:20 - 1:27
    "Imola Circuit": (76000, 83000),                  # 1:16 - 1:23
    "Miami International Autodrome": (82000, 89000),  # 1:22 - 1:29
    "Circuit de Monaco": (72000, 79000),              # 1:12 - 1:19
    "Circuit Gilles Villeneuve": (75000, 82000),     # 1:15 - 1:22
}

def create_mock_data():
    """Create mock F1 leaderboard data."""
    print("Creating mock F1 leaderboard data...")
    
    # Assign players to rigs with contact info
    rigs = ["RIG1", "RIG2", "RIG3", "RIG4"]
    for i, rig in enumerate(rigs):
        if i < len(MOCK_PLAYERS):
            player = MOCK_PLAYERS[i]
            assign_player_to_rig(
                rig, 
                player["name"], 
                player["phone"], 
                player["email"]
            )
            print(f"Assigned {player['name']} to {rig}")
    
    # Create lap times for multiple tracks
    created_count = 0
    for track_name, (min_time, max_time) in TRACK_LAP_TIMES.items():
        print(f"Creating lap times for {track_name}...")
        
        # Create 6-8 lap times per track
        num_times = random.randint(6, 8)
        selected_players = random.sample(MOCK_PLAYERS, num_times)
        
        for player in selected_players:
            # Generate realistic lap time with some variation
            base_time = random.randint(min_time, max_time)
            
            # Add some skill-based consistency (some players are consistently faster)
            player_skill = hash(player["name"]) % 1000
            skill_modifier = (player_skill - 500) * 2  # +/- 1 second variation
            lap_time_ms = max(min_time, base_time + skill_modifier)
            
            # Random rig assignment
            rig = random.choice(rigs)
            
            success = add_lap_time(rig, track_name, player["name"], lap_time_ms)
            if success:
                created_count += 1
                # Format time for display
                minutes = lap_time_ms // 60000
                seconds = (lap_time_ms % 60000) // 1000
                millis = lap_time_ms % 1000
                time_str = f"{minutes}:{seconds:02d}.{millis:03d}"
                print(f"  - {player['name']}: {time_str} ({rig})")
    
    print(f"\n✅ Created {created_count} mock lap times across {len(TRACK_LAP_TIMES)} tracks!")
    print("Mock data is ready for Supabase sync testing.")

def clear_existing_data():
    """Clear existing lap times (but keep rigs and tracks)."""
    print("Clearing existing lap time data...")
    conn = get_db_connection()
    try:
        conn.execute("DELETE FROM lap_times")
        conn.commit()
        print("✅ Cleared existing lap times")
    finally:
        conn.close()

if __name__ == "__main__":
    if len(sys.argv) > 1 and sys.argv[1] == "--clear":
        clear_existing_data()
    else:
        clear_existing_data()  # Clear first
        create_mock_data()