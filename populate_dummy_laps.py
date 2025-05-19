#!/usr/bin/env python3
"""
Script to populate the F1 Leaderboard database with dummy lap times for testing.
"""

import os
import sys
import random

# Add the project root to the Python path to allow importing backend modules
root_dir = os.path.abspath(os.path.dirname(__file__))
sys.path.append(os.path.join(root_dir, "f1_leaderboard_app"))

try:
    from backend.database.db_manager import add_lap_time, initialize_database, get_rig_id, get_track_id
    from config.app_config import F1_2024_TRACKS # To ensure track name is valid
except ImportError as e:
    print(f"Error importing necessary modules: {e}")
    print("Please ensure this script is run from the project root directory (f1-24-leaderboard)")
    print("and that your PYTHONPATH is set up correctly if issues persist.")
    sys.exit(1)

def populate_laps():
    """
    Adds 20 dummy lap times for Jeddah Corniche Circuit.
    """
    track_to_populate = "Jeddah Corniche Circuit"
    num_laps = 20
    rig_identifier_for_laps = "RIG1"  # Ensure this rig exists in your database

    print(f"Attempting to populate {num_laps} lap times for track: '{track_to_populate}' using rig: '{rig_identifier_for_laps}'")

    # First, ensure the database is initialized (creates tables, tracks, rigs if not present)
    # This is generally safe to call as it uses INSERT OR IGNORE for tracks and rigs.
    try:
        print("Initializing database (if not already initialized)...")
        initialize_database()
    except Exception as e:
        print(f"Error during database initialization: {e}")
        # Depending on the error, we might not want to proceed
        # For now, we'll try to continue as add_lap_time has its own checks

    # Verify that the target track and rig exist
    if track_to_populate not in F1_2024_TRACKS:
        print(f"Error: Target track '{track_to_populate}' is not in the configured F1_2024_TRACKS list.")
        print("Please use a valid track name from config/app_config.py.")
        return

    if not get_track_id(track_to_populate):
        print(f"Error: Track '{track_to_populate}' not found in the database. Make sure it was added during initialization.")
        return
        
    if not get_rig_id(rig_identifier_for_laps):
        print(f"Error: Rig '{rig_identifier_for_laps}' not found in the database. Make sure it was added during initialization.")
        return

    print(f"Proceeding to add {num_laps} lap times...")
    laps_added_count = 0
    for i in range(1, num_laps + 1):
        player_name = f"Dummy Player {i:02d}"
        # Lap times between 1:28.000 and 1:35.000
        # 88,000 ms to 95,000 ms
        base_lap_time_ms = 88000 
        lap_time_ms = base_lap_time_ms + random.randint(0, 7000) + random.randint(0, 999)
        
        print(f"Adding lap: Player='{player_name}', Track='{track_to_populate}', Rig='{rig_identifier_for_laps}', Time='{lap_time_ms}ms'")
        success = add_lap_time(
            rig_identifier=rig_identifier_for_laps,
            track_name=track_to_populate,
            player_name=player_name,
            lap_time_ms=lap_time_ms
        )
        if success:
            laps_added_count +=1
        else:
            print(f"Failed to add lap for {player_name}. Check logs for details.")

    print(f"\nFinished populating dummy laps. Successfully added {laps_added_count}/{num_laps} laps.")

if __name__ == "__main__":
    # Note: This script modifies your database.
    # Ensure you have a backup if your DB contains important data.
    print("--- Dummy Lap Time Population Script ---")
    populate_laps()
    print("--- Script finished ---") 