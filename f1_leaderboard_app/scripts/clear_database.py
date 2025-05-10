#!/usr/bin/env python3
"""
F1 Leaderboard - Database Clearing Script

This script allows you to clear database entries for testing purposes.
You can choose to clear:
- Lap times only
- Rig assignments only  
- All data (reset to initial state)

Usage:
$ python scripts/clear_database.py --lap-times  # Clear only lap times
$ python scripts/clear_database.py --rigs       # Clear only rig assignments
$ python scripts/clear_database.py --all        # Clear everything
"""

import os
import sys
import sqlite3
import argparse
import logging

# Add the project root to the Python path
script_dir = os.path.dirname(os.path.abspath(__file__))
project_root = os.path.dirname(script_dir)
sys.path.append(project_root)

# Import app configuration
try:
    from config.app_config import DATABASE_URL, DEFAULT_RIG_NAMES
except ImportError as e:
    print(f"Error importing app configuration: {e}")
    print("Make sure you're running this script from the project root directory.")
    sys.exit(1)

# Set up logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

def get_db_connection():
    """Get a connection to the SQLite database."""
    db_path = os.path.join(project_root, DATABASE_URL)
    
    if not os.path.exists(db_path):
        logger.error(f"Database file not found at: {db_path}")
        sys.exit(1)
        
    try:
        conn = sqlite3.connect(db_path)
        conn.row_factory = sqlite3.Row
        return conn
    except sqlite3.Error as e:
        logger.error(f"Error connecting to database: {e}")
        sys.exit(1)

def clear_lap_times(conn):
    """Clear all lap time records from the database."""
    try:
        cursor = conn.cursor()
        cursor.execute("DELETE FROM lap_times")
        conn.commit()
        
        # Get number of rows deleted
        rows_deleted = cursor.rowcount
        logger.info(f"Cleared {rows_deleted} lap time records")
        
        return True
    except sqlite3.Error as e:
        logger.error(f"Error clearing lap times: {e}")
        conn.rollback()
        return False

def clear_rig_assignments(conn):
    """Clear rig assignments and reset to defaults."""
    try:
        cursor = conn.cursor()
        
        # First check if we need to create the default rigs
        cursor.execute("SELECT COUNT(*) FROM rigs")
        rig_count = cursor.fetchone()[0]
        
        # Clear current assignments
        cursor.execute("DELETE FROM rigs")
        
        # Re-create default rig assignments
        for rig_id, default_name in DEFAULT_RIG_NAMES.items():
            cursor.execute(
                "INSERT INTO rigs (rig_identifier, current_player_name) VALUES (?, ?)",
                (rig_id, default_name)
            )
            
        conn.commit()
        logger.info(f"Reset {len(DEFAULT_RIG_NAMES)} rig assignments to default values")
        
        return True
    except sqlite3.Error as e:
        logger.error(f"Error resetting rig assignments: {e}")
        conn.rollback()
        return False

def reset_all(conn):
    """Reset the entire database to initial state."""
    success = True
    
    if not clear_lap_times(conn):
        success = False
        
    if not clear_rig_assignments(conn):
        success = False
        
    return success

def main():
    parser = argparse.ArgumentParser(
        description="Clear F1 Leaderboard database entries for testing",
        formatter_class=argparse.ArgumentDefaultsHelpFormatter
    )
    
    # Create mutually exclusive group for clearing options
    group = parser.add_mutually_exclusive_group(required=True)
    group.add_argument("--lap-times", action="store_true", help="Clear lap time records only")
    group.add_argument("--rigs", action="store_true", help="Reset rig assignments to defaults")
    group.add_argument("--all", action="store_true", help="Clear all data (reset to initial state)")
    
    # Parse arguments
    args = parser.parse_args()
    
    # Connect to database
    logger.info("Connecting to database...")
    conn = get_db_connection()
    
    try:
        if args.lap_times:
            logger.info("Clearing lap time records...")
            if clear_lap_times(conn):
                logger.info("Lap time records cleared successfully")
                
        elif args.rigs:
            logger.info("Resetting rig assignments...")
            if clear_rig_assignments(conn):
                logger.info("Rig assignments reset successfully")
                
        elif args.all:
            logger.info("Resetting entire database...")
            if reset_all(conn):
                logger.info("Database reset successfully")
    finally:
        conn.close()
    
    logger.info("Done!")

if __name__ == "__main__":
    main() 