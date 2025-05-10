#!/usr/bin/env python3
"""
F1 Leaderboard - Basic Telemetry Listener (Proof of Concept)

This script captures F1 2024 telemetry data broadcasted via UDP,
extracts lap times and track information, and prints them to the console.
This is a proof-of-concept for the telemetry data ingestion component.

Prerequisites:
- F1 2024 game with UDP telemetry enabled (Settings > Telemetry Settings)
- UDP broadcast enabled or pointed to this computer's IP
- Port set to 20777 (default)

Usage:
Run from the f1_leaderboard_app root directory:
$ python listeners/basic_listener.py
"""

import os
import sys
import time
import logging
from datetime import datetime

# Add the project root to the Python path
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

# Import app configuration
from config.app_config import TELEMETRY_REPO_PATH, TRACK_ID_MAPPING, F1_2024_TRACKS

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

class TelemetryListener:
    """Basic telemetry listener for F1 2024 game data."""
    
    def __init__(self, port=20777):
        """Initialize the telemetry listener.
        
        Args:
            port (int): UDP port to listen on (default: 20777)
        """
        self.port = port
        self.listener = None
        self.players = [Player() for _ in range(22)]  # F1 has a maximum of 22 cars
        self.session = Session()
        self.last_lap_times = [0] * 22  # Store previous lap times to detect changes
        self.running = False
        
    def initialize(self):
        """Initialize the UDP listener."""
        try:
            logger.info(f"Initializing UDP listener on port {self.port}")
            self.listener = Listener(port=self.port)
            return True
        except Exception as e:
            logger.error(f"Failed to initialize listener: {e}")
            return False
    
    def get_track_name(self, track_id):
        """Get the human-readable track name from the track ID.
        
        Args:
            track_id (int): Track ID from telemetry
            
        Returns:
            str: Human-readable track name or 'Unknown Track' if not found
        """
        if track_id in track_dictionary:
            internal_name = track_dictionary[track_id][0]
            
            # Try to map internal name to official name
            for official_name, tid in TRACK_ID_MAPPING.items():
                if tid == track_id:
                    return official_name
            
            return f"Track: {internal_name}"
        
        return f"Unknown Track (ID: {track_id})"
    
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
    
    def process_lap_data(self, packet, player_car_index):
        """Process lap data packet and print new lap times.
        
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
                
                # Only print lap times for valid laps
                if not lap_data.m_current_lap_invalid:
                    formatted_time = self.format_lap_time(last_lap_time)
                    
                    # Check if this is the player's car
                    car_type = "Player Car" if i == player_car_index else "AI Car"
                    
                    # Print lap information
                    logger.info(
                        f"New Lap Completed - {car_type} (Index: {i})\n"
                        f"  Track: {self.get_track_name(self.session.track)}\n"
                        f"  Lap Time: {formatted_time}\n"
                        f"  Position: {lap_data.m_car_position}\n"
                        f"  Current Lap: {lap_data.m_current_lap_num}\n"
                    )
                    
                    # Update best lap time if applicable
                    if player.bestLapTime > last_lap_time or player.bestLapTime == 0:
                        player.bestLapTime = last_lap_time
                        formatted_best = self.format_lap_time(player.bestLapTime)
                        logger.info(f"  New Personal Best: {formatted_best}")
    
    def process_session_data(self, packet):
        """Process session data packet to update track information.
        
        Args:
            packet: The SessionData packet
        """
        # Update track ID if changed
        if self.session.track != packet.m_track_id:
            old_track = self.get_track_name(self.session.track) if self.session.track != -1 else "None"
            self.session.track = packet.m_track_id
            new_track = self.get_track_name(self.session.track)
            
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
        logger.info("Telemetry listener started. Waiting for F1 2024 telemetry data...")
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

def main():
    """Main entry point."""
    try:
        # Create and run the telemetry listener
        listener = TelemetryListener()
        listener.run()
    except Exception as e:
        logger.error(f"Unhandled error: {e}")
        return 1
    
    return 0

if __name__ == "__main__":
    sys.exit(main()) 