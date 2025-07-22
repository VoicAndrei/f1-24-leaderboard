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


def get_top_lap_times(track_name, limit=20):
    """
    Get the top lap times for a specific track.
    
    Args:
        track_name (str): Name of the track
        limit (int, optional): Maximum number of lap times to return. Defaults to 20.
        
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


def assign_player_to_rig(rig_identifier, player_name, phone_number="", email=""):
    """
    Assign a player to a simulator rig.
    
    Args:
        rig_identifier (str): Unique identifier for the rig (e.g., "RIG1")
        player_name (str): Name of the player to assign
        phone_number (str, optional): Phone number of the player
        email (str, optional): Email address of the player
        
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
        
        # Update the rig's current player and contact information
        conn.execute(
            "UPDATE rigs SET current_player_name = ?, phone_number = ?, email = ? WHERE rig_identifier = ?",
            (player_name, phone_number, email, rig_identifier)
        )
        
        conn.commit()
        logger.info(f"Assigned player '{player_name}' to rig '{rig_identifier}' with contact info")
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
            "SELECT id, rig_identifier, current_player_name, phone_number, email FROM rigs ORDER BY rig_identifier"
        )
        
        results = []
        for row in cursor.fetchall():
            results.append({
                'id': row['id'],
                'rig_identifier': row['rig_identifier'],
                'current_player_name': row['current_player_name'],
                'phone_number': row['phone_number'] if row['phone_number'] else "",
                'email': row['email'] if row['email'] else ""
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


# Database Management Functions

def get_all_lap_times_detailed():
    """
    Get all lap times with detailed information for database management.
    
    Returns:
        list: List of all lap times with full details
    """
    conn = get_db_connection()
    
    try:
        cursor = conn.execute(
            """
            SELECT 
                lt.id,
                lt.lap_time_ms,
                lt.timestamp,
                lt.player_name_on_lap,
                r.rig_identifier,
                r.phone_number,
                r.email,
                t.name as track_name
            FROM lap_times lt
            JOIN rigs r ON lt.rig_id = r.id
            JOIN tracks t ON lt.track_id = t.id
            ORDER BY lt.timestamp DESC
            """
        )
        
        results = []
        for row in cursor.fetchall():
            results.append({
                'id': row['id'],
                'lap_time_ms': row['lap_time_ms'],
                'lap_time_formatted': format_lap_time_db(row['lap_time_ms']),
                'timestamp': row['timestamp'],
                'player_name': row['player_name_on_lap'],
                'rig_identifier': row['rig_identifier'],
                'phone_number': row['phone_number'] or '',
                'email': row['email'] or '',
                'track_name': row['track_name']
            })
        
        return results
    
    finally:
        conn.close()


def get_database_stats():
    """
    Get database statistics for overview.
    
    Returns:
        dict: Database statistics
    """
    conn = get_db_connection()
    
    try:
        stats = {}
        
        # Count total lap times
        cursor = conn.execute("SELECT COUNT(*) as count FROM lap_times")
        stats['total_lap_times'] = cursor.fetchone()['count']
        
        # Count unique players
        cursor = conn.execute("SELECT COUNT(DISTINCT player_name_on_lap) as count FROM lap_times")
        stats['unique_players'] = cursor.fetchone()['count']
        
        # Count total rigs
        cursor = conn.execute("SELECT COUNT(*) as count FROM rigs")
        stats['total_rigs'] = cursor.fetchone()['count']
        
        # Count tracks with lap times
        cursor = conn.execute(
            "SELECT COUNT(DISTINCT track_id) as count FROM lap_times"
        )
        stats['tracks_with_times'] = cursor.fetchone()['count']
        
        # Get fastest lap overall
        cursor = conn.execute(
            """
            SELECT lt.lap_time_ms, lt.player_name_on_lap, t.name as track_name
            FROM lap_times lt
            JOIN tracks t ON lt.track_id = t.id
            ORDER BY lt.lap_time_ms ASC
            LIMIT 1
            """
        )
        fastest = cursor.fetchone()
        if fastest:
            stats['fastest_lap'] = {
                'time_ms': fastest['lap_time_ms'],
                'time_formatted': format_lap_time_db(fastest['lap_time_ms']),
                'player': fastest['player_name_on_lap'],
                'track': fastest['track_name']
            }
        else:
            stats['fastest_lap'] = None
            
        return stats
    
    finally:
        conn.close()


def update_lap_time_entry(lap_time_id, player_name, lap_time_ms, track_name):
    """
    Update an existing lap time entry.
    
    Args:
        lap_time_id (int): ID of the lap time entry
        player_name (str): New player name
        lap_time_ms (int): New lap time in milliseconds
        track_name (str): New track name
        
    Returns:
        bool: True if successful, False otherwise
    """
    conn = get_db_connection()
    
    try:
        # Get track ID
        track_id = get_track_id(track_name)
        if not track_id:
            logger.error(f"Track not found: {track_name}")
            return False
        
        # Update the lap time entry
        conn.execute(
            """
            UPDATE lap_times 
            SET player_name_on_lap = ?, lap_time_ms = ?, track_id = ?
            WHERE id = ?
            """,
            (player_name, lap_time_ms, track_id, lap_time_id)
        )
        
        if conn.total_changes == 0:
            logger.error(f"No lap time found with ID: {lap_time_id}")
            return False
        
        conn.commit()
        logger.info(f"Updated lap time entry ID {lap_time_id}: {player_name} - {track_name} - {lap_time_ms}ms")
        return True
    
    except Exception as e:
        conn.rollback()
        logger.error(f"Error updating lap time entry: {e}")
        return False
    
    finally:
        conn.close()


def delete_lap_time_entry(lap_time_id):
    """
    Delete a lap time entry.
    
    Args:
        lap_time_id (int): ID of the lap time entry to delete
        
    Returns:
        bool: True if successful, False otherwise
    """
    conn = get_db_connection()
    
    try:
        # Delete the lap time entry
        conn.execute("DELETE FROM lap_times WHERE id = ?", (lap_time_id,))
        
        if conn.total_changes == 0:
            logger.error(f"No lap time found with ID: {lap_time_id}")
            return False
        
        conn.commit()
        logger.info(f"Deleted lap time entry ID {lap_time_id}")
        return True
    
    except Exception as e:
        conn.rollback()
        logger.error(f"Error deleting lap time entry: {e}")
        return False
    
    finally:
        conn.close()


def format_lap_time_db(milliseconds):
    """
    Format lap time from milliseconds to MM:SS.mmm for database management.
    
    Args:
        milliseconds (int): Lap time in milliseconds
        
    Returns:
        str: Formatted lap time as MM:SS.mmm
    """
    if milliseconds == 0 or milliseconds is None:
        return "00:00.000"
    
    total_seconds = milliseconds / 1000
    minutes = int(total_seconds // 60)
    seconds = int(total_seconds % 60)
    milliseconds_part = int((total_seconds - int(total_seconds)) * 1000)
    
    return f"{minutes:02d}:{seconds:02d}.{milliseconds_part:03d}"


def parse_lap_time_to_ms(time_string):
    """
    Parse lap time string (MM:SS.mmm) to milliseconds.
    
    Args:
        time_string (str): Time in format MM:SS.mmm
        
    Returns:
        int: Time in milliseconds, or None if invalid format
    """
    try:
        # Handle different possible formats
        time_string = time_string.strip()
        
        # Split by colon
        if ':' not in time_string:
            return None
            
        minutes_part, seconds_part = time_string.split(':', 1)
        minutes = int(minutes_part)
        
        # Handle seconds and milliseconds
        if '.' in seconds_part:
            seconds_str, ms_str = seconds_part.split('.', 1)
            seconds = int(seconds_str)
            # Pad or truncate milliseconds to 3 digits
            ms_str = ms_str.ljust(3, '0')[:3]
            milliseconds_part = int(ms_str)
        else:
            seconds = int(seconds_part)
            milliseconds_part = 0
        
        # Convert to total milliseconds
        total_ms = (minutes * 60 * 1000) + (seconds * 1000) + milliseconds_part
        return total_ms
        
    except (ValueError, IndexError) as e:
        logger.error(f"Error parsing lap time '{time_string}': {e}")
        return None