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

# Import app configuration - THIS NOW SETS THE PROFILE BASED ON ENV VAR
from config.app_config import (
    API_HOST, API_PORT, RIG_IP_MAPPING, F1_2024_TRACKS, 
    AUTO_CYCLE_INTERVAL_SECONDS, F1_TRACK_DISPLAY_NAMES, 
    NETWORK_CONFIG, ACTIVE_NETWORK_PROFILE, SHOP_NETWORK, MOBILE_NETWORK, # Import new/renamed vars
    print_active_network_config # Optional debug function
)

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

# Optional: Print the active network config at startup for verification
if __name__ == "__main__": # To ensure it only runs when main.py is executed directly
    print_active_network_config()

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
    phone_number: str
    email: str

class AssignPlayerRequest(BaseModel):
    """
    Model for player assignment request.
    """
    rig_identifier: str = Field(..., description="Unique identifier for the simulator rig (e.g., 'RIG1')")
    player_name: str = Field(..., description="Name of the player to assign to the rig")
    phone_number: str = Field("", description="Phone number of the player (optional)")
    email: str = Field("", description="Email address of the player (optional)")

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
        
        # Check for anonymity code - if player name is "null" (case-insensitive), ignore the lap time
        if player_name.lower() == "null":
            logger.info(f"Lap time ignored for anonymous player on rig {lap_data.rig_identifier}")
            return {
                "success": True,
                "message": f"Lap time recorded but not saved (anonymous mode)",
                "lap_time_ms": lap_data.lap_time_ms,
                "formatted_time": format_lap_time(lap_data.lap_time_ms)
            }
        
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
            assignment.player_name,
            assignment.phone_number,
            assignment.email
        )
        
        if not success:
            raise HTTPException(status_code=404, detail=f"Rig not found: {assignment.rig_identifier}")
        
        return {
            "success": True,
            "message": f"Player '{assignment.player_name}' assigned to rig '{assignment.rig_identifier}' with contact info"
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

def send_timer_command_to_rig(rig_identifier: str, action: str, duration_seconds: Optional[int] = None) -> bool:
    """
    Send a timer command (start or stop) to a specific rig's timer client.
    
    Args:
        rig_identifier: The rig identifier (e.g., 'RIG1')
        action: The command to send ('start' or 'stop')
        duration_seconds: Timer duration in seconds (only for 'start' action)
        
    Returns:
        bool: True if successful, False otherwise
    """
    try:
        rig_ip = RIG_IP_MAPPING.get(rig_identifier) # RIG_IP_MAPPING is now correctly set at import time
        if not rig_ip:
            logger.error(f"No IP mapping found for rig: {rig_identifier}")
            return False
        
        if action == "start":
            if duration_seconds is None:
                logger.error(f"Duration must be provided for start action on {rig_identifier}")
                return False
            url = f"http://{rig_ip}:5001/start_timer"
            payload = {"duration": duration_seconds}
            response = requests.post(url, json=payload, timeout=5)
        elif action == "stop":
            url = f"http://{rig_ip}:5001/stop_timer"
            # No payload needed for stop, but sending an empty JSON for consistency if client expects it
            response = requests.post(url, json={}, timeout=5) 
        else:
            logger.error(f"Invalid timer action: {action} for {rig_identifier}")
            return False
            
        response.raise_for_status()
        
        result = response.json()
        if result.get("status") == "success":
            logger.info(f"Timer {action} command successful on {rig_identifier}")
            return True
        else:
            logger.error(f"Timer {action} command failed on {rig_identifier}: {result.get('message', 'Unknown error')}")
            return False
            
    except requests.exceptions.RequestException as e:
        logger.error(f"Network error communicating with {rig_identifier} for action {action}: {e}")
        return False
    except Exception as e:
        logger.error(f"Error sending timer {action} command to {rig_identifier}: {e}")
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
    
    rig_id = timer_request.rig_identifier
    duration_minutes = timer_request.duration_minutes
    duration_seconds = int(duration_minutes * 60)

    with timer_lock:
        if rig_id in rig_timer_states and rig_timer_states[rig_id].get("timer_active", False):
            # Check if the rig client also thinks a timer is active.
            # This local check might be out of sync if backend restarted.
            # Best to rely on the command to the rig.
            logger.warning(f"Backend thinks timer is already active for {rig_id}. Attempting to start new one.")
            # Proceed to send command, rig client should handle overlapping timers if necessary
            # or we can decide to explicitly stop first. For now, let start command override.

        # Send command to rig client
        if send_timer_command_to_rig(rig_id, "start", duration_seconds):
            # If rig client confirms start, update backend state
            if rig_id in rig_timer_states and rig_timer_states[rig_id].get("timer_thread"):
                # If an old thread exists for this rig (e.g. from a previous run without clean stop)
                # it's a bit tricky. The old thread might still be running.
                # For now, we overwrite, assuming the new timer on the rig is the source of truth.
                # A more robust solution might involve ensuring old threads are properly joined or signalled.
                logger.info(f"Overwriting existing timer thread info for {rig_id} due to new start command.")

            # Define the timer countdown logic for backend state (primarily for status endpoint)
            def timer_countdown():
                current_remaining = duration_seconds
                while current_remaining > 0:
                    with timer_lock:
                        if not rig_timer_states.get(rig_id, {}).get("timer_active", False):
                            logger.info(f"Timer for {rig_id} was stopped or cleared. Exiting backend countdown thread.")
                            break 
                        rig_timer_states[rig_id]["remaining_time"] = current_remaining
                    time.sleep(1)
                    current_remaining -= 1
                
                # Timer finished or was stopped
                with timer_lock:
                    if rig_id in rig_timer_states and rig_timer_states[rig_id].get("timer_active", False): # ensure it wasn't stopped by another call
                        rig_timer_states[rig_id]["timer_active"] = False
                        rig_timer_states[rig_id]["remaining_time"] = 0
                        logger.info(f"Backend timer countdown finished for {rig_id}")
                    # Note: We don't clear the timer_thread here, it just exits.

            thread = threading.Thread(target=timer_countdown, daemon=True)
            rig_timer_states[rig_id] = {
                "timer_active": True,
                "remaining_time": duration_seconds,
                "duration_minutes": duration_minutes, # Store original requested duration
                "timer_thread": thread # Store thread for potential future management
            }
            thread.start()
            logger.info(f"Timer started for {rig_id} with duration {duration_minutes} minutes by admin.")
            return {"message": f"Timer started for {rig_id} ({duration_minutes} min)", "status": "success"}
        else:
            # Rig client failed to start the timer
            # Ensure local state reflects this
            if rig_id in rig_timer_states:
                 rig_timer_states[rig_id]["timer_active"] = False
                 rig_timer_states[rig_id]["remaining_time"] = 0
            logger.error(f"Failed to start timer on rig client for {rig_id}")
            raise HTTPException(status_code=500, detail=f"Failed to start timer on rig {rig_id}. Rig client might be offline or unresponsive.")

@app.get("/api/admin/timer/status", response_model=List[TimerStatusResponse], tags=["Admin", "Timer"])
async def get_all_timer_status():
    """
    Get the status of all rig timers.
    """
    global rig_timer_states, timer_lock
    statuses = []
    
    # It's better to get rig assignments from DB to ensure we cover all configured rigs
    try:
        rig_assignments = get_rig_assignments() 
        all_rig_ids = [rig.rig_identifier for rig in rig_assignments]
    except Exception as e:
        logger.error(f"Could not fetch rig assignments for timer status: {e}. Falling back to timer_states keys.")
        all_rig_ids = list(rig_timer_states.keys())


    with timer_lock:
        for rig_id in all_rig_ids: # Iterate over known rigs
            state = rig_timer_states.get(rig_id)
            if state and state.get("timer_active", False):
                statuses.append(TimerStatusResponse(
                    rig_identifier=rig_id,
                    timer_active=True,
                    remaining_time=state.get("remaining_time", 0),
                    duration_minutes=state.get("duration_minutes", 0)
                ))
            else:
                 # If not in active states, or explicitly inactive
                statuses.append(TimerStatusResponse(
                    rig_identifier=rig_id,
                    timer_active=False,
                    remaining_time=0,
                    duration_minutes=rig_timer_states.get(rig_id, {}).get("duration_minutes", 0) # show last duration if available
                ))
    return statuses

@app.post("/api/admin/timer/stop/{rig_identifier}", tags=["Admin", "Timer"])
async def stop_rig_timer(rig_identifier: str):
    """
    Stop the timer for a specific rig.
    """
    global rig_timer_states, timer_lock
    
    logger.info(f"Attempting to stop timer for rig: {rig_identifier}")

    # Send command to rig client to stop its timer
    if send_timer_command_to_rig(rig_identifier, "stop"):
        # If rig client confirms stop, update backend state
        with timer_lock:
            if rig_identifier in rig_timer_states:
                rig_timer_states[rig_identifier]["timer_active"] = False
                rig_timer_states[rig_identifier]["remaining_time"] = 0
                # We don't need to explicitly stop the backend thread here, 
                # it should check the 'timer_active' flag and exit.
                logger.info(f"Timer stop command sent successfully to {rig_identifier}. Backend state updated.")
                return {"message": f"Timer stop command sent to {rig_identifier}", "status": "success"}
            else:
                # Rig wasn't in backend state, but stop command was sent.
                logger.info(f"Timer stop command sent to {rig_identifier} (rig not in active backend state).")
                return {"message": f"Timer stop command sent to {rig_identifier} (rig was not in active backend state).", "status": "success"}

    else:
        # Rig client failed to stop the timer or didn't respond
        logger.error(f"Failed to send stop timer command to rig client for {rig_identifier}")
        # Even if the command fails, we should probably mark it as inactive in the backend
        # to prevent the admin UI from thinking it's still running if the rig is offline.
        # However, this could lead to a mismatch if the rig is online but the stop command failed for another reason.
        # For now, let's return an error and not change backend state if rig communication fails.
        raise HTTPException(status_code=500, detail=f"Failed to stop timer on rig {rig_identifier}. Rig client might be offline or unresponsive.")

@app.post("/api/admin/overlay/dismiss/{rig_identifier}", tags=["Admin", "Overlay"])
async def dismiss_rig_overlay(rig_identifier: str):
    """
    Dismiss the company overlay for a specific rig.
    """
    logger.info(f"Attempting to dismiss overlay for rig: {rig_identifier}")

    # Send command to rig client to dismiss its overlay
    if send_overlay_dismiss_command_to_rig(rig_identifier):
        logger.info(f"Overlay dismiss command sent successfully to {rig_identifier}")
        return {"message": f"Overlay dismiss command sent to {rig_identifier}", "status": "success"}
    else:
        # Rig client failed to dismiss the overlay or didn't respond
        logger.error(f"Failed to send dismiss overlay command to rig client for {rig_identifier}")
        raise HTTPException(status_code=500, detail=f"Failed to dismiss overlay on rig {rig_identifier}. Rig client might be offline or unresponsive.")

@app.post("/api/admin/overlay/show/{rig_identifier}", tags=["Admin", "Overlay"])
async def show_rig_overlay(rig_identifier: str):
    """
    Show the company overlay for a specific rig (manual session end).
    """
    logger.info(f"Attempting to show overlay for rig: {rig_identifier}")

    # Send command to rig client to show its overlay
    if send_overlay_show_command_to_rig(rig_identifier):
        logger.info(f"Overlay show command sent successfully to {rig_identifier}")
        return {"message": f"Overlay show command sent to {rig_identifier}", "status": "success"}
    else:
        # Rig client failed to show the overlay or didn't respond
        logger.error(f"Failed to send show overlay command to rig client for {rig_identifier}")
        raise HTTPException(status_code=500, detail=f"Failed to show overlay on rig {rig_identifier}. Rig client might be offline or unresponsive.")

@app.post("/api/admin/timer/reset/{rig_identifier}", tags=["Admin", "Timer"])
async def reset_rig_timer(rig_identifier: str):
    """
    Reset the timer for a specific rig (stop and clear to inactive state).
    """
    global rig_timer_states, timer_lock
    
    logger.info(f"Attempting to reset timer for rig: {rig_identifier}")

    # Send stop command to rig client first
    if send_timer_command_to_rig(rig_identifier, "stop"):
        # Reset backend state
        with timer_lock:
            if rig_identifier in rig_timer_states:
                rig_timer_states[rig_identifier]["timer_active"] = False
                rig_timer_states[rig_identifier]["remaining_time"] = 0
                rig_timer_states[rig_identifier]["duration_minutes"] = 0
                logger.info(f"Timer reset successfully for {rig_identifier}. Backend state cleared.")
            else:
                logger.info(f"Timer reset for {rig_identifier} (rig not in active backend state).")
                
        return {"message": f"Timer reset for {rig_identifier}", "status": "success"}
    else:
        # Rig client failed to stop the timer or didn't respond
        logger.error(f"Failed to send reset timer command to rig client for {rig_identifier}")
        # Still reset backend state in case rig is offline
        with timer_lock:
            if rig_identifier in rig_timer_states:
                rig_timer_states[rig_identifier]["timer_active"] = False
                rig_timer_states[rig_identifier]["remaining_time"] = 0
                rig_timer_states[rig_identifier]["duration_minutes"] = 0
        raise HTTPException(status_code=500, detail=f"Failed to reset timer on rig {rig_identifier}. Rig client might be offline. Backend state cleared.")

@app.post("/api/admin/esc/{rig_identifier}", tags=["Admin", "Utility"])
async def press_esc_rig(rig_identifier: str):
    """
    Press ESC key on a specific rig (utility function).
    """
    logger.info(f"Attempting to press ESC on rig: {rig_identifier}")

    # Send command to rig client to press ESC
    if send_esc_command_to_rig(rig_identifier):
        logger.info(f"ESC command sent successfully to {rig_identifier}")
        return {"message": f"ESC key pressed on {rig_identifier}", "status": "success"}
    else:
        # Rig client failed to press ESC or didn't respond
        logger.error(f"Failed to send ESC command to rig client for {rig_identifier}")
        raise HTTPException(status_code=500, detail=f"Failed to press ESC on rig {rig_identifier}. Rig client might be offline or unresponsive.")

def send_esc_command_to_rig(rig_identifier: str) -> bool:
    """
    Send an ESC key press command to a specific rig's timer client.
    
    Args:
        rig_identifier: The rig identifier (e.g., 'RIG1')
        
    Returns:
        bool: True if successful, False otherwise
    """
    try:
        rig_ip = RIG_IP_MAPPING.get(rig_identifier) # RIG_IP_MAPPING is now correctly set at import time
        if not rig_ip:
            logger.error(f"No IP mapping found for rig: {rig_identifier}")
            return False
        
        url = f"http://{rig_ip}:5001/press_esc"
        response = requests.post(url, json={}, timeout=5) 
            
        response.raise_for_status()
        
        result = response.json()
        if result.get("status") == "success":
            logger.info(f"ESC command successful on {rig_identifier}")
            return True
        else:
            logger.error(f"ESC command failed on {rig_identifier}: {result.get('message', 'Unknown error')}")
            return False
            
    except requests.exceptions.RequestException as e:
        logger.error(f"Network error communicating with {rig_identifier} for ESC command: {e}")
        return False
    except Exception as e:
        logger.error(f"Error sending ESC command to {rig_identifier}: {e}")
        return False

def send_overlay_show_command_to_rig(rig_identifier: str) -> bool:
    """
    Send an overlay show command to a specific rig's timer client.
    
    Args:
        rig_identifier: The rig identifier (e.g., 'RIG1')
        
    Returns:
        bool: True if successful, False otherwise
    """
    try:
        rig_ip = RIG_IP_MAPPING.get(rig_identifier) # RIG_IP_MAPPING is now correctly set at import time
        if not rig_ip:
            logger.error(f"No IP mapping found for rig: {rig_identifier}")
            return False
        
        url = f"http://{rig_ip}:5001/show_overlay"
        response = requests.post(url, json={}, timeout=5) 
            
        response.raise_for_status()
        
        result = response.json()
        if result.get("status") == "success":
            logger.info(f"Overlay show command successful on {rig_identifier}")
            return True
        else:
            logger.error(f"Overlay show command failed on {rig_identifier}: {result.get('message', 'Unknown error')}")
            return False
            
    except requests.exceptions.RequestException as e:
        logger.error(f"Network error communicating with {rig_identifier} for overlay show: {e}")
        return False
    except Exception as e:
        logger.error(f"Error sending overlay show command to {rig_identifier}: {e}")
        return False

def send_overlay_dismiss_command_to_rig(rig_identifier: str) -> bool:
    """
    Send an overlay dismiss command to a specific rig's timer client.
    
    Args:
        rig_identifier: The rig identifier (e.g., 'RIG1')
        
    Returns:
        bool: True if successful, False otherwise
    """
    try:
        rig_ip = RIG_IP_MAPPING.get(rig_identifier) # RIG_IP_MAPPING is now correctly set at import time
        if not rig_ip:
            logger.error(f"No IP mapping found for rig: {rig_identifier}")
            return False
        
        url = f"http://{rig_ip}:5001/dismiss_overlay"
        response = requests.post(url, json={}, timeout=5) 
            
        response.raise_for_status()
        
        result = response.json()
        if result.get("status") == "success":
            logger.info(f"Overlay dismiss command successful on {rig_identifier}")
            return True
        else:
            logger.error(f"Overlay dismiss command failed on {rig_identifier}: {result.get('message', 'Unknown error')}")
            return False
            
    except requests.exceptions.RequestException as e:
        logger.error(f"Network error communicating with {rig_identifier} for overlay dismiss: {e}")
        return False
    except Exception as e:
        logger.error(f"Error sending overlay dismiss command to {rig_identifier}: {e}")
        return False

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
    # The API_HOST is now set correctly by app_config.py at import time
    logger.info(f"MAIN.PY: Starting server with API_HOST: {API_HOST} for profile: {ACTIVE_NETWORK_PROFILE}")
    logger.info(f"MAIN.PY: Rig IPs will be: {RIG_IP_MAPPING}")
    
    uvicorn.run(
        "main:app", 
        host=API_HOST, 
        port=API_PORT,
        reload=True
    ) 