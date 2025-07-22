#!/usr/bin/env python3
"""
F1 Leaderboard Application - Database Initialization Script

This script initializes the database for the F1 Leaderboard application.
It creates the required tables and populates them with initial data.

Usage:
    python scripts/init_db.py
"""

import os
import sys
import logging

# Add the project root to the Python path
script_dir = os.path.dirname(os.path.abspath(__file__))
project_root = os.path.abspath(os.path.join(script_dir, ".."))
sys.path.append(project_root)

# Import database manager
from backend.database.db_manager import initialize_database, get_db_connection
from config.app_config import DATABASE_URL

# Set up logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

def migrate_existing_database():
    """
    Migrate existing database to add new columns if they don't exist.
    """
    try:
        conn = get_db_connection()
        
        # Check if the new columns exist
        cursor = conn.execute("PRAGMA table_info(rigs)")
        columns = [column[1] for column in cursor.fetchall()]
        
        needs_migration = False
        
        # Add phone_number column if it doesn't exist
        if 'phone_number' not in columns:
            logger.info("Adding phone_number column to rigs table...")
            conn.execute("ALTER TABLE rigs ADD COLUMN phone_number TEXT DEFAULT ''")
            needs_migration = True
        
        # Add email column if it doesn't exist
        if 'email' not in columns:
            logger.info("Adding email column to rigs table...")
            conn.execute("ALTER TABLE rigs ADD COLUMN email TEXT DEFAULT ''")
            needs_migration = True
        
        if needs_migration:
            conn.commit()
            logger.info("Database migration completed successfully.")
        else:
            logger.info("Database schema is already up to date.")
        
    except Exception as e:
        logger.error(f"Error during database migration: {e}")
        conn.rollback()
        raise
    finally:
        conn.close()

def main():
    """
    Main function to initialize the database.
    """
    try:
        logger.info("Starting database initialization...")
        db_path = os.path.join(project_root, DATABASE_URL)
        logger.info(f"Database will be created at: {db_path}")
        
        # Check if database exists for migration
        db_exists = os.path.exists(db_path)
        
        # Initialize the database
        initialize_database()
        
        # If database already existed, run migration
        if db_exists:
            logger.info("Existing database detected, checking for migrations...")
            migrate_existing_database()
        else:
            logger.info("New database created with latest schema.")
        
        logger.info("Database initialization completed successfully.")
        return 0
    except Exception as e:
        logger.error(f"Error initializing database: {e}")
        return 1

if __name__ == "__main__":
    sys.exit(main()) 