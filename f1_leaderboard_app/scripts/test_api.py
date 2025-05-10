#!/usr/bin/env python3
"""
F1 Leaderboard Application - API Test Script

This script tests the API functionality by directly submitting a lap time
and then retrieving the leaderboard for verification.
"""

import sys
import requests
import time
import traceback
import logging

# Set up logging to file and console
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler("api_test.log"),
        logging.StreamHandler(sys.stdout)
    ]
)
logger = logging.getLogger(__name__)

# API configuration
API_HOST = "localhost"
API_PORT = 8000
API_BASE_URL = f"http://{API_HOST}:{API_PORT}"

def test_api_connection():
    """Test basic API connectivity."""
    try:
        response = requests.get(f"{API_BASE_URL}/api")
        logger.info(f"API connection test: {response.status_code}")
        logger.info(f"Response: {response.json()}")
        return response.status_code == 200
    except requests.RequestException as e:
        logger.error(f"Error connecting to API: {e}")
        return False
    except Exception as e:
        logger.error(f"Unexpected error testing API connection: {e}")
        logger.error(traceback.format_exc())
        return False

def submit_lap_time(rig_id, track_name, lap_time_ms):
    """Submit a lap time to the API."""
    url = f"{API_BASE_URL}/api/laptime"
    payload = {
        "rig_identifier": rig_id,
        "track_name": track_name,
        "lap_time_ms": lap_time_ms
    }
    
    try:
        logger.info(f"Submitting lap time: {payload}")
        response = requests.post(url, json=payload)
        logger.info(f"Response status: {response.status_code}")
        logger.info(f"Response: {response.json()}")
        return response.status_code == 200
    except requests.RequestException as e:
        logger.error(f"Error submitting lap time: {e}")
        return False
    except Exception as e:
        logger.error(f"Unexpected error submitting lap time: {e}")
        logger.error(traceback.format_exc())
        return False

def get_leaderboard(track_name):
    """Get the leaderboard for a track."""
    url = f"{API_BASE_URL}/api/leaderboard/{track_name}"
    
    try:
        logger.info(f"Getting leaderboard for: {track_name}")
        response = requests.get(url)
        logger.info(f"Response status: {response.status_code}")
        leaderboard = response.json()
        logger.info(f"Leaderboard: {leaderboard}")
        return leaderboard
    except requests.RequestException as e:
        logger.error(f"Error getting leaderboard: {e}")
        return None
    except Exception as e:
        logger.error(f"Unexpected error getting leaderboard: {e}")
        logger.error(traceback.format_exc())
        return None

def main():
    """Main function."""
    try:
        logger.info("F1 Leaderboard API Test")
        logger.info("======================")
        
        # Test API connection
        if not test_api_connection():
            logger.error("Failed to connect to API. Make sure it's running.")
            return 1
        
        # Submit lap times
        tracks = [
            "Bahrain International Circuit",  # First track in F1_2024_TRACKS
            "Autodromo Nazionale Monza",
            "Circuit de Monaco",
            "Silverstone Circuit"
        ]
        
        rig_id = "RIG1"
        
        # Submit multiple lap times for different tracks
        for track in tracks:
            # Submit 3 lap times per track
            for i in range(3):
                # Generate lap times between 85 and 95 seconds
                lap_time_ms = 85000 + (i * 2000) + (1000 if i == 1 else 0)
                
                if not submit_lap_time(rig_id, track, lap_time_ms):
                    logger.warning(f"Failed to submit lap time for {track}")
                
                # Wait a bit between submissions
                time.sleep(0.5)
        
        # Wait for any database operations to complete
        time.sleep(1)
        
        # Get leaderboards for verification
        for track in tracks:
            get_leaderboard(track)
        
        logger.info("Test completed successfully")
        return 0
    except Exception as e:
        logger.error(f"Unhandled exception in main: {e}")
        logger.error(traceback.format_exc())
        return 1

if __name__ == "__main__":
    sys.exit(main()) 