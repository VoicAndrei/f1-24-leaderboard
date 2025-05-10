#!/usr/bin/env python3
"""
F1 Leaderboard - Rig Telemetry Listener

This script captures F1 2024 telemetry data broadcasted via UDP,
extracts lap times and track information, and sends them to the backend API.
Each instance of this script is associated with a specific simulator rig.

Prerequisites:
- F1 2024 game with UDP telemetry enabled (Settings > Telemetry Settings)
- UDP broadcast enabled or pointed to this computer's IP
- Port set to 20777 (default)
- Backend API running and accessible

Usage:
Run from the f1_leaderboard_app root directory:
$ python listeners/rig_listener.py --rig-id RIG1
$ python listeners/rig_listener.py --rig-id RIG1 --api-host 192.168.1.100 --api-port 8000
"""

import os
import sys
import time
import logging
import argparse
import requests
from datetime import datetime
from urllib.parse import urljoin

# Add the project root to the Python path
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

# Import app configuration
from config.app_config import (
    TELEMETRY_REPO_PATH, 
    TRACK_ID_MAPPING, 
    F1_2024_TRACKS,
    API_HOST,
    API_PORT,
    DEFAULT_UDP_PORT
)

# Add the telemetry repository to the Python path
sys.path.append(TELEMETRY_REPO_PATH)

# Import telemetry components
try:
    from parser2024 import Listener, HEADER_FIELD_TO_PACKET_TYPE
    from dictionnaries import track_dictionary, conversion
    from Player import Player
    from Session import Session
except ImportError as e:
    print(f"Error importing F1 telemetry repository components: {e}")
    print(f"Make sure the repository is available at: {TELEMETRY_REPO_PATH}")
    sys.exit(1)

# Set up logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s',
    handlers=[
        logging.StreamHandler(sys.stdout)
    ]
)
logger = logging.getLogger(__name__)

# Reverse track dictionary mapping (ID to name)
TRACK_ID_TO_NAME = {v: k for k, v in TRACK_ID_MAPPING.items()}

class RigTelemetryListener:
    """Telemetry listener for F1 2024 game data from a specific rig."""
    
    def __init__(self, rig_id, api_host, api_port, udp_port=DEFAULT_UDP_PORT):
        """Initialize the telemetry listener.
        
        Args:
            rig_id (str): Identifier for the simulator rig (e.g., "RIG1")
            api_host (str): Host address for the backend API
            api_port (int): Port for the backend API
            udp_port (int): UDP port to listen on (default: 20777)
        """
        self.rig_id = rig_id
        self.udp_port = udp_port
        self.api_base_url = f"http://{api_host}:{api_port}"
        self.lap_submission_url = urljoin(self.api_base_url, "/api/laptime")
        
        self.listener = None
        self.players = [Player() for _ in range(22)]  # F1 has a maximum of 22 cars
        self.session = Session()
        self.last_lap_times = [0] * 22  # Store previous lap times to detect changes
        self.running = False
        
        logger.info(f"Rig ID: {self.rig_id}")
        logger.info(f"API endpoint: {self.lap_submission_url}")
        logger.info(f"UDP port: {self.udp_port}")
        
    def initialize(self):
        """Initialize the UDP listener."""
        try:
            logger.info(f"Initializing UDP listener on port {self.udp_port}")
            self.listener = Listener(port=self.udp_port)
            
            # Test API connection
            try:
                response = requests.get(self.api_base_url)
                logger.info(f"API connection test: {response.status_code}")
            except requests.RequestException as e:
                logger.warning(f"Unable to connect to API at {self.api_base_url}: {e}")
                logger.warning("Will continue but lap times may not be recorded in the database.")
                
            return True
        except Exception as e:
            logger.error(f"Failed to initialize listener: {e}")
            return False
    
    def resolve_track_name(self, track_id):
        """Resolve the track ID to an official track name from F1_2024_TRACKS.
        
        Args:
            track_id (int): Track ID from telemetry
            
        Returns:
            tuple: (track_name, successful)
            - track_name (str): Official track name or best guess
            - successful (bool): Whether the resolution was successful
        """
        # Try direct mapping from TRACK_ID_MAPPING
        for official_name, tid in TRACK_ID_MAPPING.items():
            if tid == track_id:
                return official_name, True
        
        # Try to get internal name from track_dictionary
        if track_id in track_dictionary:
            internal_name = track_dictionary[track_id][0]
            
            # Try a fuzzy match with F1_2024_TRACKS
            for official_name in F1_2024_TRACKS:
                # Convert to lowercase for matching
                if internal_name.lower() in official_name.lower():
                    return official_name, True
            
            # No match found, return best guess with warning
            best_guess = None
            
            # Special cases
            if internal_name == "sakhir":
                best_guess = "Bahrain International Circuit"
            elif internal_name == "melbourne":
                best_guess = "Albert Park Circuit"
            elif internal_name == "shanghai": 
                best_guess = "Shanghai International Circuit"
            elif internal_name == "monaco":
                best_guess = "Circuit de Monaco"
            elif internal_name == "catalunya":
                best_guess = "Circuit de Barcelona-Catalunya"
            elif internal_name == "spa":
                best_guess = "Circuit de Spa-Francorchamps"
            
            if best_guess:
                logger.warning(f"Track '{internal_name}' not directly mapped, using best guess: {best_guess}")
                return best_guess, True
            
            # Return internal name with warning
            logger.warning(f"Track '{internal_name}' (ID: {track_id}) not found in F1_2024_TRACKS, using internal name")
            return f"Track: {internal_name}", False
        
        # Unknown track
        logger.warning(f"Unknown track ID: {track_id}, cannot submit lap time")
        return f"Unknown Track (ID: {track_id})", False
    
    def format_lap_time(self, milliseconds):
        """Format lap time from milliseconds to MM:SS.mmm.
        
        Args:
            milliseconds (float): Lap time in milliseconds
            
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
    
    def submit_lap_time(self, track_name, lap_time_ms):
        """Submit lap time to the backend API.
        
        Args:
            track_name (str): Name of the track
            lap_time_ms (int): Lap time in milliseconds
            
        Returns:
            bool: True if successful, False otherwise
        """
        payload = {
            "rig_identifier": self.rig_id,
            "track_name": track_name,
            "lap_time_ms": lap_time_ms
        }
        
        try:
            response = requests.post(
                self.lap_submission_url,
                json=payload,
                timeout=5  # 5 second timeout
            )
            
            if response.status_code == 200:
                result = response.json()
                logger.info(f"Lap time submitted successfully: {result.get('message')}")
                return True
            else:
                logger.error(f"Failed to submit lap time: HTTP {response.status_code}")
                logger.error(f"Response: {response.text}")
                return False
                
        except requests.RequestException as e:
            logger.error(f"Error submitting lap time to API: {e}")
            return False
    
    def process_lap_data(self, packet, player_car_index):
        """Process lap data packet, print and submit new lap times.
        
        Args:
            packet: The LapData packet
            player_car_index (int): Index of the player's car
        """
        for i in range(len(packet.m_lap_data)):
            lap_data = packet.m_lap_data[i]
            player = self.players[i]
            
            # Update player lap times
            current_lap_time = lap_data.m_current_lap_time_in_ms
            last_lap_time = lap_data.m_last_lap_time_in_ms
            
            # Store the last lap time
            player.lastLapTime = last_lap_time
            player.currentLapTime = current_lap_time
            
            # Check if this is a new completed lap
            if last_lap_time != 0 and last_lap_time != self.last_lap_times[i]:
                self.last_lap_times[i] = last_lap_time
                
                # Only process valid laps
                if not lap_data.m_current_lap_invalid:
                    formatted_time = self.format_lap_time(last_lap_time)
                    
                    # Check if this is the player's car
                    car_type = "Player Car" if i == player_car_index else "AI Car"
                    
                    # Resolve track name for API submission
                    track_name, track_resolved = self.resolve_track_name(self.session.track)
                    
                    # Print lap information
                    logger.info(
                        f"New Lap Completed - {car_type} (Index: {i})\n"
                        f"  Track: {track_name}\n"
                        f"  Lap Time: {formatted_time}\n"
                        f"  Position: {lap_data.m_car_position}\n"
                        f"  Current Lap: {lap_data.m_current_lap_num}\n"
                    )
                    
                    # Update best lap time if applicable
                    if player.bestLapTime > last_lap_time or player.bestLapTime == 0:
                        player.bestLapTime = last_lap_time
                        formatted_best = self.format_lap_time(player.bestLapTime)
                        logger.info(f"  New Personal Best: {formatted_best}")
                    
                    # Submit lap time to API (only if this is the player's car or if we want to submit AI car laps)
                    # For the purpose of the application, we'll submit all lap times
                    if track_resolved:
                        logger.info(f"Submitting lap time to API: {track_name} - {formatted_time}")
                        self.submit_lap_time(track_name, last_lap_time)
    
    def process_session_data(self, packet):
        """Process session data packet to update track information.
        
        Args:
            packet: The SessionData packet
        """
        # Update track ID if changed
        if self.session.track != packet.m_track_id:
            track_name, _ = self.resolve_track_name(self.session.track if self.session.track != -1 else 0)
            old_track = track_name if self.session.track != -1 else "None"
            
            self.session.track = packet.m_track_id
            new_track, _ = self.resolve_track_name(self.session.track)
            
            logger.info(f"Track changed: {old_track} -> {new_track}")
            
            # Reset lap times when track changes
            self.last_lap_times = [0] * 22
            for player in self.players:
                player.bestLapTime = 0
                player.lastLapTime = 0
    
    def run(self):
        """Main loop to capture and process telemetry data."""
        if not self.initialize():
            return False
        
        self.running = True
        logger.info(f"Telemetry listener for rig {self.rig_id} started. Waiting for F1 2024 telemetry data...")
        logger.info("Press Ctrl+C to stop.")
        
        try:
            while self.running:
                # Get packet from the listener
                header_and_packet = self.listener.get()
                
                if header_and_packet:
                    header, packet = header_and_packet
                    
                    # Get player car index
                    player_car_index = header.m_player_car_index
                    
                    # Process different packet types
                    if header.m_packet_id == 1:  # Session data (includes track info)
                        self.process_session_data(packet)
                    
                    elif header.m_packet_id == 2:  # Lap data
                        self.process_lap_data(packet, player_car_index)
                
                # Small sleep to prevent high CPU usage
                time.sleep(0.001)
                
        except KeyboardInterrupt:
            logger.info("Telemetry listener stopped by user.")
        except Exception as e:
            logger.error(f"Error in telemetry listener: {e}")
        
        return True

def parse_arguments():
    """Parse command-line arguments.
    
    Returns:
        argparse.Namespace: Parsed arguments
    """
    parser = argparse.ArgumentParser(description="F1 2024 Telemetry Listener for a specific simulator rig")
    
    parser.add_argument(
        "--rig-id",
        required=True,
        help="Identifier for the simulator rig (e.g., 'RIG1', 'RIG2', 'RIG3')"
    )
    
    parser.add_argument(
        "--api-host",
        default=API_HOST,
        help=f"Host address for the backend API (default: {API_HOST})"
    )
    
    parser.add_argument(
        "--api-port",
        type=int,
        default=API_PORT,
        help=f"Port for the backend API (default: {API_PORT})"
    )
    
    parser.add_argument(
        "--udp-port",
        type=int,
        default=DEFAULT_UDP_PORT,
        help=f"UDP port to listen on (default: {DEFAULT_UDP_PORT})"
    )
    
    return parser.parse_args()

def main():
    """Main entry point."""
    try:
        # Parse command-line arguments
        args = parse_arguments()
        
        # Create and run the telemetry listener
        listener = RigTelemetryListener(
            rig_id=args.rig_id,
            api_host=args.api_host,
            api_port=args.api_port,
            udp_port=args.udp_port
        )
        
        listener.run()
    except Exception as e:
        logger.error(f"Unhandled error: {e}")
        return 1
    
    return 0

if __name__ == "__main__":
    sys.exit(main()) 