#!/usr/bin/env python3
"""
F1 Leaderboard Control Test Script

This script tests the advanced leaderboard control API endpoints:
- GET /api/display/current_leaderboard_data
- POST /api/admin/track/select
- POST /api/admin/track/toggle_autocycle
- GET /api/admin/track/status

Usage:
    python scripts/test_leaderboard_control.py
"""

import os
import sys
import time
import json
import logging
import requests
import argparse

# Add the project root to the Python path
script_dir = os.path.dirname(os.path.abspath(__file__))
project_root = os.path.abspath(os.path.join(script_dir, ".."))
sys.path.append(project_root)

# Import app configuration
from config.app_config import API_HOST, API_PORT, F1_2024_TRACKS, AUTO_CYCLE_INTERVAL_SECONDS

# Set up logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

# Base URL for API
API_BASE_URL = f"http://{API_HOST}:{API_PORT}/api"

def get_current_leaderboard_data():
    """Get the current leaderboard data."""
    url = f"{API_BASE_URL}/display/current_leaderboard_data"
    
    try:
        response = requests.get(url)
        if response.status_code == 200:
            data = response.json()
            track_name = data.get("track_name", "Unknown")
            auto_cycle = data.get("auto_cycle_enabled", False)
            leaderboard_count = len(data.get("leaderboard", []))
            
            logger.info(f"Current Track: {track_name}")
            logger.info(f"Auto-cycle: {'Enabled' if auto_cycle else 'Disabled'}")
            logger.info(f"Leaderboard Entries: {leaderboard_count}")
            return data
        else:
            logger.error(f"Error: {response.status_code} - {response.text}")
            return None
    except Exception as e:
        logger.error(f"Exception: {e}")
        return None

def get_track_status():
    """Get the current track status."""
    url = f"{API_BASE_URL}/admin/track/status"
    
    try:
        response = requests.get(url)
        if response.status_code == 200:
            data = response.json()
            logger.info(f"Track Status:")
            logger.info(f"  Current Display Track: {data.get('current_display_track', 'Unknown')}")
            logger.info(f"  Manual Selection Active: {data.get('manual_selection_active', False)}")
            logger.info(f"  Manual Selection: {data.get('manual_selection', 'None')}")
            logger.info(f"  Auto-cycle Enabled: {data.get('auto_cycle_enabled', False)}")
            logger.info(f"  Current Track Index: {data.get('current_track_index', 0)}")
            time_until_next = data.get('time_until_next_cycle')
            if time_until_next is not None:
                logger.info(f"  Time Until Next Cycle: {time_until_next:.1f} seconds")
            return data
        else:
            logger.error(f"Error: {response.status_code} - {response.text}")
            return None
    except Exception as e:
        logger.error(f"Exception: {e}")
        return None

def select_track(track_name):
    """Manually select a track."""
    url = f"{API_BASE_URL}/admin/track/select"
    
    try:
        data = {"track_name": track_name}
        response = requests.post(url, json=data)
        if response.status_code == 200:
            result = response.json()
            logger.info(f"Track selection result: {result.get('message', 'Unknown')}")
            return result
        else:
            logger.error(f"Error: {response.status_code} - {response.text}")
            return None
    except Exception as e:
        logger.error(f"Exception: {e}")
        return None

def toggle_autocycle():
    """Toggle the auto-cycle feature."""
    url = f"{API_BASE_URL}/admin/track/toggle_autocycle"
    
    try:
        response = requests.post(url)
        if response.status_code == 200:
            result = response.json()
            auto_cycle = result.get("auto_cycle_enabled", False)
            logger.info(f"Auto-cycle: {'Enabled' if auto_cycle else 'Disabled'}")
            return result
        else:
            logger.error(f"Error: {response.status_code} - {response.text}")
            return None
    except Exception as e:
        logger.error(f"Exception: {e}")
        return None

def test_auto_cycling():
    """Test the auto-cycling functionality."""
    logger.info("Testing auto-cycling functionality")
    
    # Get initial status
    status = get_track_status()
    if not status:
        return
    
    # Make sure auto-cycle is enabled
    if not status.get("auto_cycle_enabled", False):
        logger.info("Enabling auto-cycle")
        toggle_autocycle()
    
    # Get the current track
    initial_track = get_current_leaderboard_data().get("track_name")
    logger.info(f"Initial track: {initial_track}")
    
    # Wait for a cycle
    cycle_time = AUTO_CYCLE_INTERVAL_SECONDS + 1
    logger.info(f"Waiting {cycle_time} seconds for auto-cycle...")
    time.sleep(cycle_time)
    
    # Get the new track
    new_track = get_current_leaderboard_data().get("track_name")
    logger.info(f"New track: {new_track}")
    
    # Check if the track changed
    if new_track != initial_track:
        logger.info("Auto-cycling test PASSED ✓")
    else:
        logger.error("Auto-cycling test FAILED ✗")

def test_manual_selection():
    """Test the manual track selection functionality."""
    logger.info("Testing manual track selection")
    
    # Get the available tracks
    if len(F1_2024_TRACKS) < 2:
        logger.error("Not enough tracks to test manual selection")
        return
    
    # Get initial status
    current_data = get_current_leaderboard_data()
    if not current_data:
        return
    
    initial_track = current_data.get("track_name")
    
    # Select a different track
    for track in F1_2024_TRACKS:
        if track != initial_track:
            target_track = track
            break
    
    logger.info(f"Selecting track: {target_track}")
    select_track(target_track)
    
    # Get the new current track
    new_data = get_current_leaderboard_data()
    if not new_data:
        return
    
    new_track = new_data.get("track_name")
    
    # Check if the track changed to the selected one
    if new_track == target_track:
        logger.info("Manual selection test PASSED ✓")
    else:
        logger.error(f"Manual selection test FAILED ✗ (got {new_track}, expected {target_track})")
    
    # Get track status
    get_track_status()

def test_toggle_autocycle():
    """Test toggling the auto-cycle feature."""
    logger.info("Testing auto-cycle toggle")
    
    # Get initial status
    status = get_track_status()
    if not status:
        return
    
    initial_auto_cycle = status.get("auto_cycle_enabled", False)
    logger.info(f"Initial auto-cycle: {'Enabled' if initial_auto_cycle else 'Disabled'}")
    
    # Toggle auto-cycle
    logger.info("Toggling auto-cycle")
    toggle_autocycle()
    
    # Get new status
    new_status = get_track_status()
    if not new_status:
        return
    
    new_auto_cycle = new_status.get("auto_cycle_enabled", False)
    logger.info(f"New auto-cycle: {'Enabled' if new_auto_cycle else 'Disabled'}")
    
    # Check if the auto-cycle state changed
    if new_auto_cycle != initial_auto_cycle:
        logger.info("Auto-cycle toggle test PASSED ✓")
    else:
        logger.error("Auto-cycle toggle test FAILED ✗")
    
    # Toggle back to original state
    logger.info("Toggling auto-cycle back to original state")
    toggle_autocycle()
    
    # Get final status
    final_status = get_track_status()
    if final_status and final_status.get("auto_cycle_enabled") == initial_auto_cycle:
        logger.info("Auto-cycle restored to original state ✓")

def main():
    parser = argparse.ArgumentParser(description="Test F1 Leaderboard Control API")
    parser.add_argument("--test", choices=["all", "status", "cycle", "manual", "toggle"], default="all",
                        help="Specify which test to run (default: all)")
    args = parser.parse_args()
    
    logger.info("=== F1 Leaderboard Control Test ===")
    
    if args.test in ["all", "status"]:
        logger.info("\n=== Testing Current Status ===")
        get_current_leaderboard_data()
        get_track_status()
    
    if args.test in ["all", "cycle"]:
        logger.info("\n=== Testing Auto-cycling ===")
        test_auto_cycling()
    
    if args.test in ["all", "manual"]:
        logger.info("\n=== Testing Manual Selection ===")
        test_manual_selection()
    
    if args.test in ["all", "toggle"]:
        logger.info("\n=== Testing Auto-cycle Toggle ===")
        test_toggle_autocycle()
    
    logger.info("\n=== Test Complete ===")

if __name__ == "__main__":
    main() 