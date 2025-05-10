"""
F1 Leaderboard Application - Database Manager

This module handles database connections and operations for the F1 Leaderboard application.
It provides functions for initializing the database, adding lap times, and retrieving leaderboard data.
"""

import os
import sqlite3
import logging
from datetime import datetime
import sys

# Add the project root to the Python path
root_dir = os.path.abspath(os.path.join(os.path.dirname(__file__), "../.."))
sys.path.append(root_dir)

# Import app configuration
from config.app_config import DATABASE_URL, F1_2024_TRACKS, DEFAULT_RIG_NAMES

# Set up logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


def get_db_connection():
    """
    Create a connection to the SQLite database.
    
    Returns:
        sqlite3.Connection: Database connection object
    """
    db_path = os.path.join(root_dir, DATABASE_URL)
    
    # Ensure the directory exists
    os.makedirs(os.path.dirname(db_path), exist_ok=True)
    
    conn = sqlite3.connect(db_path)
    conn.row_factory = sqlite3.Row  # Return rows as dictionaries
    return conn


def initialize_database():
    """
    Initialize the database by creating tables and populating initial data.
    
    This function:
    1. Creates tables as defined in schema.sql
    2. Populates the tracks table with F1 2024 tracks
    3. Creates the default simulator rigs
    """
    conn = get_db_connection()
    
    try:
        # Read and execute schema.sql
        schema_path = os.path.join(os.path.dirname(__file__), "schema.sql")
        with open(schema_path, 'r') as f:
            conn.executescript(f.read())
        
        # Populate tracks table
        for track_name in F1_2024_TRACKS:
            conn.execute(
                "INSERT OR IGNORE INTO tracks (name) VALUES (?)",
                (track_name,)
            )
        
        # Create default rigs
        for rig_id, rig_name in DEFAULT_RIG_NAMES.items():
            conn.execute(
                "INSERT OR IGNORE INTO rigs (rig_identifier, current_player_name) VALUES (?, ?)",
                (rig_id, rig_name)
            )
        
        conn.commit()
        logger.info("Database initialized successfully")
    
    except Exception as e:
        conn.rollback()
        logger.error(f"Error initializing database: {e}")
        raise
    
    finally:
        conn.close()


def get_track_id(track_name):
    """
    Get the ID of a track based on its name.
    
    Args:
        track_name (str): Name of the track
        
    Returns:
        int: Track ID or None if not found
    """
    conn = get_db_connection()
    
    try:
        cursor = conn.execute(
            "SELECT id FROM tracks WHERE name = ?",
            (track_name,)
        )
        result = cursor.fetchone()
        return result['id'] if result else None
    
    finally:
        conn.close()


def get_rig_id(rig_identifier):
    """
    Get the ID of a simulator rig based on its identifier.
    
    Args:
        rig_identifier (str): Unique identifier for the rig (e.g., "RIG1")
        
    Returns:
        int: Rig ID or None if not found
    """
    conn = get_db_connection()
    
    try:
        cursor = conn.execute(
            "SELECT id FROM rigs WHERE rig_identifier = ?",
            (rig_identifier,)
        )
        result = cursor.fetchone()
        return result['id'] if result else None
    
    finally:
        conn.close()


def get_rig_current_player(rig_identifier):
    """
    Get the current player name assigned to a simulator rig.
    
    Args:
        rig_identifier (str): Unique identifier for the rig (e.g., "RIG1")
        
    Returns:
        str: Current player name or "Unknown Racer" if not found
    """
    conn = get_db_connection()
    
    try:
        cursor = conn.execute(
            "SELECT current_player_name FROM rigs WHERE rig_identifier = ?",
            (rig_identifier,)
        )
        result = cursor.fetchone()
        return result['current_player_name'] if result else "Unknown Racer"
    
    finally:
        conn.close()


def add_lap_time(rig_identifier, track_name, player_name, lap_time_ms):
    """
    Add a new lap time to the database.
    
    Args:
        rig_identifier (str): Unique identifier for the rig (e.g., "RIG1")
        track_name (str): Name of the track
        player_name (str): Name of the player who set the lap time
        lap_time_ms (int): Lap time in milliseconds
        
    Returns:
        bool: True if successful, False otherwise
    """
    conn = get_db_connection()
    
    try:
        # Get track and rig IDs
        track_id = get_track_id(track_name)
        rig_id = get_rig_id(rig_identifier)
        
        if not track_id:
            logger.error(f"Track not found: {track_name}")
            return False
        
        if not rig_id:
            logger.error(f"Rig not found: {rig_identifier}")
            return False
        
        # Check if the exact same lap time already exists for this player on this track
        cursor = conn.execute(
            """
            SELECT COUNT(*) FROM lap_times 
            WHERE track_id = ? AND player_name_on_lap = ? AND lap_time_ms = ?
            """,
            (track_id, player_name, lap_time_ms)
        )
        result = cursor.fetchone()
        if result and result[0] > 0:
            logger.info(f"Duplicate lap time detected: {player_name} - {track_name} - {lap_time_ms}ms, skipping")
            return True  # Return True to indicate "success" since we're intentionally skipping
        
        # Insert the lap time
        conn.execute(
            """
            INSERT INTO lap_times 
            (rig_id, track_id, player_name_on_lap, lap_time_ms, timestamp)
            VALUES (?, ?, ?, ?, ?)
            """,
            (rig_id, track_id, player_name, lap_time_ms, datetime.now().isoformat())
        )
        
        conn.commit()
        logger.info(f"Added lap time: {player_name} - {track_name} - {lap_time_ms}ms")
        return True
    
    except Exception as e:
        conn.rollback()
        logger.error(f"Error adding lap time: {e}")
        return False
    
    finally:
        conn.close()


def get_top_lap_times(track_name, limit=10):
    """
    Get the top lap times for a specific track.
    
    Args:
        track_name (str): Name of the track
        limit (int, optional): Maximum number of lap times to return. Defaults to 10.
        
    Returns:
        list: List of dictionaries containing lap time information
    """
    conn = get_db_connection()
    
    try:
        track_id = get_track_id(track_name)
        
        if not track_id:
            logger.error(f"Track not found: {track_name}")
            return []
        
        # Use a subquery to get only the best lap time for each player
        cursor = conn.execute(
            """
            WITH BestLapTimes AS (
                SELECT 
                    player_name_on_lap,
                    MIN(lap_time_ms) as best_time
                FROM 
                    lap_times
                WHERE 
                    track_id = ?
                GROUP BY 
                    player_name_on_lap
            )
            SELECT 
                lap_times.id,
                lap_times.player_name_on_lap,
                lap_times.lap_time_ms,
                lap_times.timestamp,
                rigs.rig_identifier
            FROM 
                lap_times
            JOIN 
                rigs ON lap_times.rig_id = rigs.id
            JOIN
                BestLapTimes ON lap_times.player_name_on_lap = BestLapTimes.player_name_on_lap 
                            AND lap_times.lap_time_ms = BestLapTimes.best_time
            WHERE 
                lap_times.track_id = ?
            ORDER BY 
                lap_times.lap_time_ms ASC
            LIMIT ?
            """,
            (track_id, track_id, limit)
        )
        
        results = []
        for row in cursor.fetchall():
            results.append({
                'id': row['id'],
                'player_name': row['player_name_on_lap'],
                'lap_time_ms': row['lap_time_ms'],
                'timestamp': row['timestamp'],
                'rig_identifier': row['rig_identifier']
            })
        
        return results
    
    finally:
        conn.close()


def assign_player_to_rig(rig_identifier, player_name):
    """
    Assign a player to a simulator rig.
    
    Args:
        rig_identifier (str): Unique identifier for the rig (e.g., "RIG1")
        player_name (str): Name of the player to assign
        
    Returns:
        bool: True if successful, False otherwise
    """
    conn = get_db_connection()
    
    try:
        # Check if rig exists
        rig_id = get_rig_id(rig_identifier)
        
        if not rig_id:
            logger.error(f"Rig not found: {rig_identifier}")
            return False
        
        # Update the rig's current player
        conn.execute(
            "UPDATE rigs SET current_player_name = ? WHERE rig_identifier = ?",
            (player_name, rig_identifier)
        )
        
        conn.commit()
        logger.info(f"Assigned player '{player_name}' to rig '{rig_identifier}'")
        return True
    
    except Exception as e:
        conn.rollback()
        logger.error(f"Error assigning player to rig: {e}")
        return False
    
    finally:
        conn.close()


def get_rig_assignments():
    """
    Get all simulator rigs and their current player assignments.
    
    Returns:
        list: List of dictionaries containing rig information
    """
    conn = get_db_connection()
    
    try:
        cursor = conn.execute(
            "SELECT id, rig_identifier, current_player_name FROM rigs ORDER BY rig_identifier"
        )
        
        results = []
        for row in cursor.fetchall():
            results.append({
                'id': row['id'],
                'rig_identifier': row['rig_identifier'],
                'current_player_name': row['current_player_name']
            })
        
        return results
    
    finally:
        conn.close()


def get_all_tracks():
    """
    Get all tracks from the database.
    
    Returns:
        list: List of dictionaries containing track information
    """
    conn = get_db_connection()
    
    try:
        cursor = conn.execute(
            "SELECT id, name FROM tracks ORDER BY name"
        )
        
        results = []
        for row in cursor.fetchall():
            results.append({
                'id': row['id'],
                'name': row['name']
            })
        
        return results
    
    finally:
        conn.close() 