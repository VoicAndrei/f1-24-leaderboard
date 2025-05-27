#!/usr/bin/env python3
"""
F1 Leaderboard Application - Backend API

This module provides the FastAPI backend for the F1 Leaderboard application.
It exposes API endpoints for submitting lap times and retrieving leaderboard data.
"""

import os
import sys
import logging
import time
import threading
import requests  # Added for communicating with rig timer clients
from typing import List, Optional, Dict, Any
from datetime import datetime
import uvicorn
from fastapi import FastAPI, HTTPException, Query, Path, Request
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles
from fastapi.templating import Jinja2Templates
from fastapi.responses import HTMLResponse
from pydantic import BaseModel, Field

# Add the project root to the Python path
root_dir = os.path.abspath(os.path.join(os.path.dirname(__file__), ".."))
sys.path.append(root_dir)

# Import app configuration and database manager
from config.app_config import API_HOST, API_PORT, F1_2024_TRACKS, AUTO_CYCLE_INTERVAL_SECONDS, F1_TRACK_DISPLAY_NAMES
from backend.database.db_manager import (
    add_lap_time,
    get_top_lap_times,
    get_rig_current_player,
    get_all_tracks,
    get_rig_assignments,
    assign_player_to_rig
)

# Set up logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Leaderboard display state management
current_track_index = 0
auto_cycle_enabled = True
last_cycle_time = time.time()
manual_track_selection = None

# Timer state management (in-memory for now)
# Structure: {rig_id: {"timer_active": bool, "remaining_time": int, "timer_thread": Thread}}
rig_timer_states = {}
timer_lock = threading.Lock()

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

class RigAssignment(BaseModel):
    """
    Model for rig assignment data.
    """
    id: int
    rig_identifier: str
    current_player_name: str

class AssignPlayerRequest(BaseModel):
    """
    Model for player assignment request.
    """
    rig_identifier: str = Field(..., description="Unique identifier for the simulator rig (e.g., 'RIG1')")
    player_name: str = Field(..., description="Name of the player to assign to the rig")

class TrackSelectRequest(BaseModel):
    """
    Model for track selection request.
    """
    track_name: str = Field(..., description="Name of the track to display on the leaderboard")

class TimerStartRequest(BaseModel):
    """
    Model for timer start request.
    """
    rig_identifier: str = Field(..., description="Unique identifier for the simulator rig (e.g., 'RIG1')")
    duration_minutes: float = Field(..., description="Timer duration in minutes", gt=0)

class TimerStatusResponse(BaseModel):
    """
    Model for timer status response.
    """
    rig_identifier: str
    timer_active: bool
    remaining_time: int = 0
    duration_minutes: float = 0

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

# Mount static files
app.mount("/static", StaticFiles(directory="backend/static"), name="static")

# Set up templates
templates = Jinja2Templates(directory="backend/templates")

def get_current_leaderboard_track() -> str:
    """
    Determine the current track to display on the leaderboard.
    
    This function handles auto-cycling between tracks at regular intervals
    or returns a manually selected track if one is set.
    
    Returns:
        str: The *full official name* of the track to display
    """
    global current_track_index, last_cycle_time, manual_track_selection
    
    # If a track has been manually selected, return it
    if manual_track_selection:
        return manual_track_selection
    
    # Check if it's time to cycle to the next track
    if auto_cycle_enabled and time.time() - last_cycle_time >= AUTO_CYCLE_INTERVAL_SECONDS:
        # Advance to the next track
        current_track_index = (current_track_index + 1) % len(F1_2024_TRACKS)
        last_cycle_time = time.time()
        logger.info(f"Auto-cycling to track: {F1_2024_TRACKS[current_track_index]}")
    
    # Return the current official track name
    return F1_2024_TRACKS[current_track_index]

@app.get("/", response_class=HTMLResponse, tags=["UI"])
async def root(request: Request):
    """
    Root endpoint that returns the leaderboard HTML page.
    """
    return templates.TemplateResponse("leaderboard.html", {"request": request})

@app.get("/admin", response_class=HTMLResponse, tags=["UI"])
async def admin(request: Request):
    """
    Admin endpoint that returns the admin panel HTML page.
    """
    return templates.TemplateResponse("admin.html", {
        "request": request,
        "f1_tracks": F1_2024_TRACKS
    })

@app.get("/api", tags=["Root"])
async def api_root():
    """
    API root endpoint that returns a welcome message.
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

@app.get("/api/display/current_leaderboard_data", tags=["Display"])
async def get_current_leaderboard_data():
    """
    Get the current leaderboard data to display.
    
    This endpoint handles the logic for determining which track's leaderboard to show,
    including auto-cycling through tracks and manual track selection.
    
    Returns:
        dict: Current track name, leaderboard data, and auto-cycle status
    """
    try:
        # Get the current track to display (full official name)
        official_track_name = get_current_leaderboard_track()
        
        # Get the leaderboard data for the track using the official name
        leaderboard_data = get_top_lap_times(official_track_name)

        # Get the simplified display name for the frontend
        display_track_name = F1_TRACK_DISPLAY_NAMES.get(official_track_name, official_track_name)
        
        # Return the current display data
        return {
            "track_name": display_track_name, # Send the simplified name to frontend
            "leaderboard": leaderboard_data,
            "auto_cycle_enabled": auto_cycle_enabled
        }
    
    except Exception as e:
        logger.error(f"Error getting current leaderboard data: {e}")
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

@app.get("/api/admin/rigs", response_model=List[RigAssignment], tags=["Admin"])
async def get_rigs():
    """
    Get all simulator rigs and their current player assignments.
    
    Returns:
        list: List of rig assignments
    """
    try:
        rigs = get_rig_assignments()
        return rigs
    
    except Exception as e:
        logger.error(f"Error retrieving rig assignments: {e}")
        raise HTTPException(status_code=500, detail=str(e))

@app.post("/api/admin/rigs/assign_player", tags=["Admin"])
async def admin_assign_player(assignment: AssignPlayerRequest):
    """
    Assign a player to a simulator rig.
    
    Args:
        assignment: Player assignment request data
        
    Returns:
        dict: Success message or error
    """
    try:
        success = assign_player_to_rig(
            assignment.rig_identifier,
            assignment.player_name
        )
        
        if not success:
            raise HTTPException(status_code=404, detail=f"Rig not found: {assignment.rig_identifier}")
        
        return {
            "success": True,
            "message": f"Player '{assignment.player_name}' assigned to rig '{assignment.rig_identifier}'"
        }
    
    except HTTPException:
        raise
    
    except Exception as e:
        logger.error(f"Error assigning player to rig: {e}")
        raise HTTPException(status_code=500, detail=str(e))

@app.post("/api/admin/track/select", tags=["Admin"])
async def select_track(track_request: TrackSelectRequest):
    """
    Manually select a track to display on the leaderboard.
    
    Args:
        track_request: Track selection request data
        
    Returns:
        dict: Success message or error
    """
    global current_track_index, manual_track_selection
    
    try:
        # Validate the track name
        if track_request.track_name not in F1_2024_TRACKS:
            raise HTTPException(status_code=400, detail=f"Invalid track name: {track_request.track_name}")
        
        # Set the manual track selection
        manual_track_selection = track_request.track_name
        
        # Update the current track index to match
        current_track_index = F1_2024_TRACKS.index(track_request.track_name)
        
        logger.info(f"Track manually selected: {track_request.track_name}")
        
        return {
            "success": True,
            "message": f"Track '{track_request.track_name}' selected for display",
            "track_name": track_request.track_name
        }
    
    except HTTPException:
        raise
    
    except Exception as e:
        logger.error(f"Error selecting track: {e}")
        raise HTTPException(status_code=500, detail=str(e))

@app.post("/api/admin/track/toggle_autocycle", tags=["Admin"])
async def toggle_autocycle():
    """
    Toggle the auto-cycle feature on or off.
    
    Returns:
        dict: Current auto-cycle status
    """
    global auto_cycle_enabled, manual_track_selection, last_cycle_time
    
    try:
        # Toggle the auto-cycle flag
        auto_cycle_enabled = not auto_cycle_enabled
        
        if auto_cycle_enabled:
            # If enabling auto-cycle, clear any manual track selection
            manual_track_selection = None
            # Reset the cycle timer
            last_cycle_time = time.time()
            
            logger.info("Auto-cycle enabled")
        else:
            logger.info("Auto-cycle disabled")
        
        return {
            "auto_cycle_enabled": auto_cycle_enabled
        }
    
    except Exception as e:
        logger.error(f"Error toggling auto-cycle: {e}")
        raise HTTPException(status_code=500, detail=str(e))

@app.get("/api/admin/track/status", tags=["Admin"])
async def get_track_status():
    """
    Get the current status of the leaderboard display.
    
    Returns:
        dict: Current display status including track, selection mode, and auto-cycle status
    """
    try:
        current_track = get_current_leaderboard_track()
        
        return {
            "current_display_track": current_track,
            "manual_selection_active": manual_track_selection is not None,
            "manual_selection": manual_track_selection,
            "auto_cycle_enabled": auto_cycle_enabled,
            "current_track_index": current_track_index,
            "time_until_next_cycle": max(0, AUTO_CYCLE_INTERVAL_SECONDS - (time.time() - last_cycle_time)) if auto_cycle_enabled and not manual_track_selection else None
        }
    
    except Exception as e:
        logger.error(f"Error getting track status: {e}")
        raise HTTPException(status_code=500, detail=str(e))

# ===== TIMER API ENDPOINTS =====

def send_timer_command_to_rig(rig_identifier: str, duration_seconds: int) -> bool:
    """
    Send a timer start command to a specific rig's timer client.
    
    Args:
        rig_identifier: The rig identifier (e.g., 'RIG1')
        duration_seconds: Timer duration in seconds
        
    Returns:
        bool: True if successful, False otherwise
    """
    try:
        # IP mapping for all rigs - Update these with actual static IPs assigned to each rig PC
        rig_ip_mapping = {
            'RIG1': '192.168.0.210',  # Assign this static IP to RIG1 PC
            'RIG2': '192.168.0.211',  # Assign this static IP to RIG2 PC
            'RIG3': '192.168.0.212',  # Assign this static IP to RIG3 PC  
            'RIG4': '192.168.0.213',  # Assign this static IP to RIG4 PC
        }
        
        rig_ip = rig_ip_mapping.get(rig_identifier)
        if not rig_ip:
            logger.error(f"No IP mapping found for rig: {rig_identifier}")
            return False
        
        url = f"http://{rig_ip}:5001/start_timer"
        payload = {"duration": duration_seconds}
        
        response = requests.post(url, json=payload, timeout=5)
        response.raise_for_status()
        
        result = response.json()
        if result.get("status") == "success":
            logger.info(f"Timer started successfully on {rig_identifier}")
            return True
        else:
            logger.error(f"Timer failed on {rig_identifier}: {result.get('message', 'Unknown error')}")
            return False
            
    except requests.exceptions.RequestException as e:
        logger.error(f"Network error communicating with {rig_identifier}: {e}")
        return False
    except Exception as e:
        logger.error(f"Error sending timer command to {rig_identifier}: {e}")
        return False

@app.post("/api/admin/timer/start", tags=["Admin", "Timer"])
async def start_rig_timer(timer_request: TimerStartRequest):
    """
    Start a timer for a specific rig.
    
    Args:
        timer_request: Timer start request data
        
    Returns:
        dict: Success message or error
    """
    global rig_timer_states, timer_lock
    
    try:
        rig_id = timer_request.rig_identifier
        duration_seconds = int(timer_request.duration_minutes * 60)
        
        # Check if timer is already active for this rig
        with timer_lock:
            if rig_id in rig_timer_states and rig_timer_states[rig_id].get("timer_active", False):
                raise HTTPException(status_code=400, detail=f"Timer already active for {rig_id}")
        
        # Send command to rig's timer client
        success = send_timer_command_to_rig(rig_id, duration_seconds)
        
        if not success:
            raise HTTPException(status_code=500, detail=f"Failed to start timer on {rig_id}. Is the timer client running?")
        
        # Update local state
        with timer_lock:
            rig_timer_states[rig_id] = {
                "timer_active": True,
                "remaining_time": duration_seconds,
                "start_time": time.time(),
                "duration_minutes": timer_request.duration_minutes
            }
        
        logger.info(f"Timer started for {rig_id}: {timer_request.duration_minutes} minutes")
        
        return {
            "success": True,
            "message": f"Timer started for {rig_id} ({timer_request.duration_minutes} minutes)",
            "rig_identifier": rig_id,
            "duration_minutes": timer_request.duration_minutes
        }
    
    except HTTPException:
        raise
    
    except Exception as e:
        logger.error(f"Error starting timer: {e}")
        raise HTTPException(status_code=500, detail=str(e))

@app.get("/api/admin/timer/status", response_model=List[TimerStatusResponse], tags=["Admin", "Timer"])
async def get_all_timer_status():
    """
    Get timer status for all rigs.
    
    Returns:
        list: Timer status for all rigs
    """
    global rig_timer_states, timer_lock
    
    try:
        # Get all rig identifiers from the database
        rigs = get_rig_assignments()
        timer_statuses = []
        
        with timer_lock:
            for rig in rigs:
                rig_id = rig['rig_identifier']
                
                if rig_id in rig_timer_states:
                    timer_state = rig_timer_states[rig_id]
                    
                    # Calculate remaining time
                    if timer_state.get("timer_active", False):
                        elapsed_time = time.time() - timer_state.get("start_time", 0)
                        remaining_time = max(0, timer_state.get("remaining_time", 0) - int(elapsed_time))
                        
                        # Check if timer has expired
                        if remaining_time <= 0:
                            timer_state["timer_active"] = False
                            remaining_time = 0
                    else:
                        remaining_time = 0
                    
                    timer_statuses.append(TimerStatusResponse(
                        rig_identifier=rig_id,
                        timer_active=timer_state.get("timer_active", False),
                        remaining_time=remaining_time,
                        duration_minutes=timer_state.get("duration_minutes", 0)
                    ))
                else:
                    # No timer state for this rig
                    timer_statuses.append(TimerStatusResponse(
                        rig_identifier=rig_id,
                        timer_active=False,
                        remaining_time=0,
                        duration_minutes=0
                    ))
        
        return timer_statuses
    
    except Exception as e:
        logger.error(f"Error getting timer status: {e}")
        raise HTTPException(status_code=500, detail=str(e))

@app.post("/api/admin/timer/stop/{rig_identifier}", tags=["Admin", "Timer"])
async def stop_rig_timer(rig_identifier: str):
    """
    Stop a timer for a specific rig.
    
    Args:
        rig_identifier: Unique identifier for the rig (e.g., 'RIG1')
        
    Returns:
        dict: Success message or error
    """
    global rig_timer_states, timer_lock
    
    try:
        with timer_lock:
            if rig_identifier not in rig_timer_states:
                raise HTTPException(status_code=404, detail=f"No timer found for {rig_identifier}")
            
            timer_state = rig_timer_states[rig_identifier]
            if not timer_state.get("timer_active", False):
                raise HTTPException(status_code=400, detail=f"No active timer for {rig_identifier}")
            
            # Stop the timer
            timer_state["timer_active"] = False
            timer_state["remaining_time"] = 0
        
        logger.info(f"Timer stopped for {rig_identifier}")
        
        return {
            "success": True,
            "message": f"Timer stopped for {rig_identifier}",
            "rig_identifier": rig_identifier
        }
    
    except HTTPException:
        raise
    
    except Exception as e:
        logger.error(f"Error stopping timer: {e}")
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