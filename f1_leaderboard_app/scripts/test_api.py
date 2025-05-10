#!/usr/bin/env python3
"""
F1 Leaderboard Application - API Test Script

This script tests the API endpoints for submitting lap times and retrieving leaderboard data.
"""

import sys
import os
import requests
import json
import time
from datetime import datetime

# Add the project root to the Python path
script_dir = os.path.dirname(os.path.abspath(__file__))
project_root = os.path.abspath(os.path.join(script_dir, ".."))
sys.path.append(project_root)

# Base URL for API
API_BASE_URL = "http://localhost:8000/api"

def submit_lap_time(rig_identifier, track_name, lap_time_ms):
    """
    Submit a lap time to the API.
    
    Args:
        rig_identifier (str): Identifier for the simulator rig (e.g., "RIG1")
        track_name (str): Name of the track
        lap_time_ms (int): Lap time in milliseconds
        
    Returns:
        dict: Response from the API
    """
    url = f"{API_BASE_URL}/laptime"
    data = {
        "rig_identifier": rig_identifier,
        "track_name": track_name,
        "lap_time_ms": lap_time_ms
    }
    
    response = requests.post(url, json=data)
    
    if response.status_code == 200:
        print(f"Lap time submitted successfully: {response.json()}")
        return response.json()
    else:
        print(f"Error submitting lap time: {response.status_code} - {response.text}")
        return None

def get_leaderboard(track_name, limit=10):
    """
    Get the leaderboard for a specific track.
    
    Args:
        track_name (str): Name of the track
        limit (int, optional): Maximum number of lap times to return. Defaults to 10.
        
    Returns:
        list: List of lap times for the track
    """
    url = f"{API_BASE_URL}/leaderboard/{track_name}"
    params = {"limit": limit}
    
    response = requests.get(url, params=params)
    
    if response.status_code == 200:
        lap_times = response.json()
        print(f"Retrieved {len(lap_times)} lap times for {track_name}:")
        
        for i, lap in enumerate(lap_times, 1):
            time_str = format_lap_time(lap["lap_time_ms"])
            print(f"{i}. {lap['player_name']} - {time_str} (Rig: {lap['rig_identifier']})")
        
        return lap_times
    else:
        print(f"Error retrieving leaderboard: {response.status_code} - {response.text}")
        return None

def get_tracks():
    """
    Get all available tracks.
    
    Returns:
        list: List of track information
    """
    url = f"{API_BASE_URL}/tracks"
    
    response = requests.get(url)
    
    if response.status_code == 200:
        tracks = response.json()
        print(f"Retrieved {len(tracks)} tracks:")
        
        for track in tracks:
            print(f"- {track['name']} (ID: {track['id']})")
        
        return tracks
    else:
        print(f"Error retrieving tracks: {response.status_code} - {response.text}")
        return None

def format_lap_time(milliseconds):
    """
    Format lap time from milliseconds to MM:SS.mmm.
    
    Args:
        milliseconds (int): Lap time in milliseconds
        
    Returns:
        str: Formatted lap time as MM:SS.mmm
    """
    if milliseconds == 0:
        return "00:00.000"
    
    total_seconds = milliseconds / 1000
    minutes = int(total_seconds // 60)
    seconds = int(total_seconds % 60)
    milliseconds = int((total_seconds - int(total_seconds)) * 1000)
    
    return f"{minutes:02d}:{seconds:02d}.{milliseconds:03d}"

def main():
    """
    Main function to test the API endpoints.
    """
    print("F1 Leaderboard API Test")
    print("======================")
    
    # Submit test lap times
    tracks_to_test = [
        "Bahrain International Circuit",
        "Jeddah Corniche Circuit",
        "Albert Park Circuit"
    ]
    
    # Get tracks
    print("\nFetching available tracks...")
    get_tracks()
    
    # Submit lap times for each track
    print("\nSubmitting test lap times...")
    for track in tracks_to_test:
        # RIG1 lap times
        submit_lap_time("RIG1", track, 90000)  # 1:30.000
        submit_lap_time("RIG1", track, 92500)  # 1:32.500
        
        # RIG2 lap times
        submit_lap_time("RIG2", track, 89500)  # 1:29.500
        submit_lap_time("RIG2", track, 91000)  # 1:31.000
        
        # RIG3 lap times
        submit_lap_time("RIG3", track, 88000)  # 1:28.000
        submit_lap_time("RIG3", track, 93000)  # 1:33.000
        
        # Wait a moment before fetching the leaderboard
        time.sleep(1)
        
        # Get leaderboard for the track
        print(f"\nLeaderboard for {track}:")
        get_leaderboard(track)
    
    return 0

if __name__ == "__main__":
    sys.exit(main()) 