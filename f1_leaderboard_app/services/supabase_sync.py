"""
F1 Leaderboard to Supabase Sync Service

This service syncs F1 leaderboard data directly to the Supabase leaderboard table.
Simple 1:1 mapping with contact info and rig tracking.
"""

import os
import sys
import requests
import asyncio
import logging
from datetime import datetime
from typing import List, Dict, Optional
import json

# Add the project root to the Python path
root_dir = os.path.abspath(os.path.join(os.path.dirname(__file__), ".."))
sys.path.append(root_dir)

try:
    from config.app_config import F1_2024_TRACKS
    from backend.database.db_manager import get_all_lap_times_detailed, get_rig_assignments
except ImportError as e:
    print(f"Import error: {e}")
    print("Make sure you're running from the f1_leaderboard_app directory")
    sys.exit(1)

# Configuration - load from .env file in same directory
def load_env_from_file():
    env_path = os.path.join(os.path.dirname(__file__), '.env')
    env_vars = {}
    if os.path.exists(env_path):
        with open(env_path, 'r') as f:
            for line in f:
                line = line.strip()
                if line and not line.startswith('#') and '=' in line:
                    key, value = line.split('=', 1)
                    env_vars[key.strip()] = value.strip()
    return env_vars

env_vars = load_env_from_file()
SUPABASE_URL = env_vars.get('SUPABASE_URL', 'your-supabase-url')
SUPABASE_ANON_KEY = env_vars.get('SUPABASE_ANON_KEY', 'your-anon-key')

# Set up logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

class F1SupabaseSync:
    def __init__(self):
        self.supabase_url = SUPABASE_URL
        self.anon_key = SUPABASE_ANON_KEY
        self.headers = {
            'apikey': self.anon_key,
            'Authorization': f'Bearer {self.anon_key}',
            'Content-Type': 'application/json'
        }

    def format_lap_time(self, lap_time_ms: int) -> str:
        """Format lap time from milliseconds to MM:SS.mmm display format."""
        if lap_time_ms <= 0:
            return "00:00.000"
        
        total_seconds = lap_time_ms / 1000
        minutes = int(total_seconds // 60)
        seconds = int(total_seconds % 60)
        milliseconds = int((total_seconds - int(total_seconds)) * 1000)
        
        return f"{minutes:02d}:{seconds:02d}.{milliseconds:03d}"

    def get_contact_info_for_player(self, player_name: str, rig_assignments: List[Dict]) -> Dict[str, str]:
        """Get contact info for a player based on current rig assignments."""
        for rig in rig_assignments:
            if rig['current_player_name'] == player_name:
                return {
                    'phone_number': rig.get('phone_number', ''),
                    'email': rig.get('email', '')
                }
        return {'phone_number': '', 'email': ''}

    async def sync_all_leaderboard_data(self):
        """Sync all F1 leaderboard data to Supabase."""
        logger.info("Starting F1 to Supabase leaderboard sync...")
        
        try:
            # Get all F1 lap times
            f1_lap_times = get_all_lap_times_detailed()
            if not f1_lap_times:
                logger.info("No F1 lap times found")
                return
            
            # Get current rig assignments for contact info
            rig_assignments = get_rig_assignments()
            
            # Clear existing leaderboard data
            logger.info("Clearing existing leaderboard data...")
            delete_response = requests.delete(
                f"{self.supabase_url}/rest/v1/leaderboard",
                headers=self.headers,
                params={'simulator_type': 'eq.F1 Live'}
            )
            
            if delete_response.status_code not in [200, 204]:
                logger.warning(f"Failed to clear existing data: {delete_response.status_code}")
            
            # Group lap times by track and calculate positions
            tracks_data = {}
            for lap_time in f1_lap_times:
                track_name = lap_time['track_name']
                if track_name not in tracks_data:
                    tracks_data[track_name] = []
                tracks_data[track_name].append(lap_time)
            
            # Sort each track's data and assign positions
            all_entries = []
            for track_name, track_lap_times in tracks_data.items():
                # Sort by lap time (best first)
                track_lap_times.sort(key=lambda x: x['lap_time_ms'])
                
                for position, lap_time in enumerate(track_lap_times, 1):
                    # Get contact info for this player
                    contact_info = self.get_contact_info_for_player(
                        lap_time['player_name'], 
                        rig_assignments
                    )
                    
                    # Format entry for Supabase
                    entry = {
                        'player_name': lap_time['player_name'],
                        'track_name': track_name,
                        'lap_time_ms': lap_time['lap_time_ms'],
                        'lap_time_formatted': self.format_lap_time(lap_time['lap_time_ms']),
                        'position': position,
                        'rig_identifier': lap_time['rig_identifier'],
                        'session_date': lap_time['timestamp'],
                        'simulator_type': 'F1 Live',
                        'phone_number': contact_info['phone_number'],
                        'email': contact_info['email']
                    }
                    all_entries.append(entry)
            
            if not all_entries:
                logger.info("No entries to sync")
                return
            
            # Insert all entries
            logger.info(f"Inserting {len(all_entries)} leaderboard entries...")
            insert_response = requests.post(
                f"{self.supabase_url}/rest/v1/leaderboard",
                headers=self.headers,
                json=all_entries
            )
            
            if insert_response.status_code == 201:
                logger.info(f"Successfully synced {len(all_entries)} leaderboard entries!")
                
                # Log summary by track
                track_counts = {}
                for entry in all_entries:
                    track_name = entry['track_name']
                    track_counts[track_name] = track_counts.get(track_name, 0) + 1
                
                for track_name, count in track_counts.items():
                    logger.info(f"  - {track_name}: {count} entries")
            else:
                logger.error(f"Failed to insert leaderboard entries: {insert_response.status_code}")
                logger.error(f"Response: {insert_response.text}")
                
        except Exception as e:
            logger.error(f"Error in sync: {e}")
            raise

    async def run_periodic_sync(self, interval_minutes: int = 5):
        """Run periodic sync every N minutes."""
        logger.info(f"Starting periodic F1 leaderboard sync (every {interval_minutes} minutes)")
        
        while True:
            try:
                await self.sync_all_leaderboard_data()
                logger.info(f"Next sync in {interval_minutes} minutes...")
                await asyncio.sleep(interval_minutes * 60)
            except KeyboardInterrupt:
                logger.info("Sync stopped by user")
                break
            except Exception as e:
                logger.error(f"Error in periodic sync: {e}")
                logger.info("Retrying in 1 minute...")
                await asyncio.sleep(60)

async def main():
    """Main function to run the sync service."""
    sync_service = F1SupabaseSync()
    
    # Check for command line arguments
    if len(sys.argv) > 1:
        if sys.argv[1] == '--once':
            # Run sync once and exit
            await sync_service.sync_all_leaderboard_data()
        elif sys.argv[1] == '--interval':
            # Run with custom interval
            interval = int(sys.argv[2]) if len(sys.argv) > 2 else 5
            await sync_service.run_periodic_sync(interval)
        else:
            print("Usage: python supabase_sync.py [--once | --interval <minutes>]")
    else:
        # Default: run periodic sync every 5 minutes
        await sync_service.run_periodic_sync(5)

if __name__ == "__main__":
    asyncio.run(main())