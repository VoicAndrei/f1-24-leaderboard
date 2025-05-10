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
from backend.database.db_manager import initialize_database
from config.app_config import DATABASE_URL

# Set up logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

def main():
    """
    Main function to initialize the database.
    """
    try:
        logger.info("Starting database initialization...")
        db_path = os.path.join(project_root, DATABASE_URL)
        logger.info(f"Database will be created at: {db_path}")
        
        # Initialize the database
        initialize_database()
        
        logger.info("Database initialization completed successfully.")
        return 0
    except Exception as e:
        logger.error(f"Error initializing database: {e}")
        return 1

if __name__ == "__main__":
    sys.exit(main()) 