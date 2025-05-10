#!/usr/bin/env python3
"""
F1 Leaderboard Application - Rig Listener Test Utility

This script simulates F1 telemetry data for testing the rig_listener.py
without having to run the F1 game. It sends mock lap completion events.

Usage:
    1. Start the backend API: python backend/main.py
    2. Start the rig listener: python listeners/rig_listener.py --rig-id RIG1
    3. Run this script: python scripts/test_rig_listener.py
"""

import os
import sys
import time
import socket
import struct
import random
import argparse
import logging

# Add the project root to the Python path
script_dir = os.path.dirname(os.path.abspath(__file__))
project_root = os.path.abspath(os.path.join(script_dir, ".."))
sys.path.append(project_root)

# Import app configuration
from config.app_config import TRACK_ID_MAPPING, DEFAULT_UDP_PORT

# Set up logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

def send_mock_session_data(sock, track_id):
    """Send mock session data packet with track information.
    
    Args:
        sock (socket.socket): UDP socket
        track_id (int): Track ID to send
    """
    # Create a more realistic mock packet that matches F1 telemetry format size
    # F1 packets have a header (29 bytes) followed by packet data
    
    # Header (29 bytes)
    packet_format = 2024  # F1 2024
    game_major_version = 1
    game_minor_version = 0
    packet_version = 1
    packet_id = 1  # Session data packet
    session_uid = 12345678
    session_time = 0.0
    frame_identifier = 0
    player_car_index = 0
    secondary_player_index = 255  # 255 = no secondary player
    
    # Create header and add some minimal session data 
    header = struct.pack(
        '<HBBBBQfIBB',
        packet_format, game_major_version, game_minor_version, packet_version,
        packet_id, session_uid, session_time, frame_identifier,
        player_car_index, secondary_player_index
    )
    
    # Add minimal mock session data (we just need the track ID)
    # Pad the packet with zeros to make it a realistic size
    session_data = struct.pack('<B', track_id) + b'\0' * 150
    
    # Combine header and data
    data = header + session_data
    
    sock.sendto(data, ('127.0.0.1', DEFAULT_UDP_PORT))
    logger.info(f"Sent session data packet with track ID: {track_id}")

def send_mock_lap_data(sock, car_index, lap_time_ms):
    """Send mock lap data packet with lap completion information.
    
    Args:
        sock (socket.socket): UDP socket
        car_index (int): Car index (0 for player car)
        lap_time_ms (int): Lap time in milliseconds
    """
    # Create a more realistic mock packet that matches F1 telemetry format size
    # F1 packets have a header (29 bytes) followed by packet data
    
    # Header (29 bytes)
    packet_format = 2024  # F1 2024
    game_major_version = 1
    game_minor_version = 0
    packet_version = 1
    packet_id = 2  # Lap data packet
    session_uid = 12345678
    session_time = 0.0
    frame_identifier = 0
    player_car_index = 0
    secondary_player_index = 255  # 255 = no secondary player
    
    # Create header
    header = struct.pack(
        '<HBBBBQfIBB',
        packet_format, game_major_version, game_minor_version, packet_version,
        packet_id, session_uid, session_time, frame_identifier,
        player_car_index, secondary_player_index
    )
    
    # Prepare lap data - we need to set the fields for a single car's lap data
    # We'll create a minimal representation with just the fields we need
    current_lap_invalid = 0  # 0 = valid lap
    last_lap_time_in_ms = lap_time_ms
    current_lap_time_in_ms = 0  # completed lap
    
    # Add a dummy lap data entry for the specified car
    # Real packet has data for all cars but we only care about one
    lap_data = bytearray(b'\0' * 1500)  # Pre-allocate with zeros
    
    # Insert data for our target car at the appropriate offset
    car_offset = car_index * 50  # Assume each car data block is 50 bytes (simplified)
    
    # Pack the last lap time at appropriate offset
    struct.pack_into('<fI', lap_data, car_offset, 0.0, last_lap_time_in_ms)
    struct.pack_into('<B', lap_data, car_offset + 30, current_lap_invalid)
    
    # Combine header and data
    data = header + lap_data
    
    sock.sendto(data, ('127.0.0.1', DEFAULT_UDP_PORT))
    logger.info(f"Sent lap data packet - Car: {car_index}, Lap time: {lap_time_ms}ms")

def main():
    """Main function."""
    parser = argparse.ArgumentParser(description="F1 Telemetry Test Utility")
    
    parser.add_argument(
        "--num-laps",
        type=int,
        default=5,
        help="Number of mock laps to send (default: 5)"
    )
    
    args = parser.parse_args()
    
    # Create UDP socket
    sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
    
    try:
        logger.info("F1 Telemetry Test Utility")
        logger.info("=========================")
        logger.info(f"Sending {args.num_laps} mock lap completions to localhost:{DEFAULT_UDP_PORT}")
        logger.info("Make sure both the backend API and rig_listener.py are running")
        
        # Get a list of track IDs
        track_ids = list(TRACK_ID_MAPPING.values())
        
        # Send mock session data for a random track
        track_id = random.choice(track_ids)
        send_mock_session_data(sock, track_id)
        
        # Wait for the listener to process the session data
        time.sleep(1)
        
        # Send mock lap completions
        for i in range(args.num_laps):
            # Generate a random lap time between 85 and 95 seconds
            lap_time_ms = random.randint(85000, 95000)
            
            # Send mock lap data (car index 0 = player car)
            send_mock_lap_data(sock, 0, lap_time_ms)
            
            # Wait for the listener to process the lap data
            time.sleep(2)
            
            # Log the lap
            logger.info(f"Lap {i+1}/{args.num_laps} completed")
            
            # Occasionally change the track
            if i > 0 and i % 3 == 0:
                track_id = random.choice(track_ids)
                send_mock_session_data(sock, track_id)
                time.sleep(1)
        
        logger.info("Test completed successfully")
        return 0
    
    except KeyboardInterrupt:
        logger.info("Test interrupted by user")
    except Exception as e:
        logger.error(f"Error: {e}")
        return 1
    finally:
        sock.close()
    
    return 0

if __name__ == "__main__":
    sys.exit(main()) 