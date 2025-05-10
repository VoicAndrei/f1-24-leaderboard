#!/usr/bin/env python3
"""
F1 Leaderboard Application - Backend API

This module provides the FastAPI backend for the F1 Leaderboard application.
It exposes API endpoints for submitting lap times and retrieving leaderboard data.
"""

import os
import sys
import logging
from typing import List, Optional
from datetime import datetime
import uvicorn
from fastapi import FastAPI, HTTPException, Query, Path
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel, Field

# Add the project root to the Python path
root_dir = os.path.abspath(os.path.join(os.path.dirname(__file__), ".."))
sys.path.append(root_dir)

# Import app configuration and database manager
from config.app_config import API_HOST, API_PORT
from backend.database.db_manager import (
    add_lap_time,
    get_top_lap_times,
    get_rig_current_player,
    get_all_tracks
)

# Set up logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Define Pydantic models for request and response data
class LapTimeSubmit(BaseModel):
    """
    Model for lap time submission data.
    """
    rig_identifier: str = Field(..., description="Unique identifier for the simulator rig (e.g., 'RIG1')")
    track_name: str = Field(..., description="Name of the F1 track")
    lap_time_ms: int = Field(..., description="Lap time in milliseconds", gt=0)

class LapTimeDisplay(BaseModel):
    """
    Model for lap time display data.
    """
    id: int
    player_name: str
    lap_time_ms: int
    timestamp: str
    rig_identifier: str

class TrackInfo(BaseModel):
    """
    Model for track information.
    """
    id: int
    name: str

# Create FastAPI application
app = FastAPI(
    title="F1 Leaderboard API",
    description="API for the F1 Leaderboard application",
    version="1.0.0"
)

# Configure CORS to allow requests from any origin
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

@app.get("/", tags=["Root"])
async def root():
    """
    Root endpoint that returns a welcome message.
    """
    return {"message": "Welcome to the F1 Leaderboard API"}

@app.post("/api/laptime", tags=["Lap Times"])
async def submit_lap_time(lap_data: LapTimeSubmit):
    """
    Submit a new lap time.
    
    Args:
        lap_data: Lap time submission data
        
    Returns:
        dict: Success message or error
    """
    try:
        # Get the current player name for the rig
        player_name = get_rig_current_player(lap_data.rig_identifier)
        
        # Add the lap time to the database
        success = add_lap_time(
            lap_data.rig_identifier,
            lap_data.track_name,
            player_name,
            lap_data.lap_time_ms
        )
        
        if not success:
            raise HTTPException(status_code=400, detail=f"Failed to add lap time")
        
        return {
            "success": True,
            "message": f"Lap time added for {player_name} on {lap_data.track_name}",
            "lap_time_ms": lap_data.lap_time_ms,
            "formatted_time": format_lap_time(lap_data.lap_time_ms)
        }
    
    except Exception as e:
        logger.error(f"Error submitting lap time: {e}")
        raise HTTPException(status_code=500, detail=str(e))

@app.get("/api/leaderboard/{track_name}", response_model=List[LapTimeDisplay], tags=["Leaderboard"])
async def get_leaderboard(
    track_name: str = Path(..., description="Name of the F1 track"),
    limit: int = Query(10, description="Maximum number of lap times to return")
):
    """
    Get the leaderboard for a specific track.
    
    Args:
        track_name: Name of the F1 track
        limit: Maximum number of lap times to return
        
    Returns:
        list: List of lap times for the track
    """
    try:
        lap_times = get_top_lap_times(track_name, limit)
        return lap_times
    
    except Exception as e:
        logger.error(f"Error retrieving leaderboard: {e}")
        raise HTTPException(status_code=500, detail=str(e))

@app.get("/api/tracks", response_model=List[TrackInfo], tags=["Tracks"])
async def get_tracks():
    """
    Get all available tracks.
    
    Returns:
        list: List of track information
    """
    try:
        tracks = get_all_tracks()
        return tracks
    
    except Exception as e:
        logger.error(f"Error retrieving tracks: {e}")
        raise HTTPException(status_code=500, detail=str(e))

def format_lap_time(milliseconds):
    """
    Format lap time from milliseconds to MM:SS.mmm.
    
    Args:
        milliseconds (int): Lap time in milliseconds
        
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

if __name__ == "__main__":
    # Run the FastAPI app with uvicorn
    uvicorn.run(
        "main:app",
        host=API_HOST,
        port=API_PORT,
        reload=True
    ) 