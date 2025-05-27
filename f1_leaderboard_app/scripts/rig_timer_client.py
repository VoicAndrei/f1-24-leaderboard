#!/usr/bin/env python3
"""
F1 Leaderboard Application - Rig Timer Client

This script runs on each simulator rig PC and provides:
- A transparent countdown timer display
- HTTP server to receive timer commands from the central admin interface
- Automatic ESC key sending when timer expires
"""

import tkinter as tk
import threading
import time
import argparse
import sys
import logging
from flask import Flask, request, jsonify

# Import the timer functionality from our working timer_app
try:
    import pydirectinput
except ImportError:
    print("Error: pydirectinput not installed. Please run: pip install pydirectinput")
    sys.exit(1)

# Set up logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Configuration
DEFAULT_HOST = '0.0.0.0'
DEFAULT_PORT = 5001
WINDOW_WIDTH = 200
WINDOW_HEIGHT = 80
WINDOW_POSITION_X_OFFSET = 50
WINDOW_POSITION_Y_OFFSET = 50
FONT_SETTINGS = ("Arial", 30, "bold")
TRANSPARENT_COLOR = 'grey15'
TEXT_COLOR = 'white'
BACKGROUND_COLOR = TRANSPARENT_COLOR

# Global variables for timer state
timer_active = False
remaining_time = 0
timer_thread = None
root = None
timer_label = None
rig_identifier = None

# Flask App
app = Flask(__name__)

def run_flask_app(host, port):
    """Run the Flask server."""
    app.run(host=host, port=port, debug=False)

@app.route('/start_timer', methods=['POST'])
def start_timer_endpoint():
    """Start timer endpoint - receives commands from the admin interface."""
    global timer_active, remaining_time, timer_thread, root
    
    if timer_active:
        return jsonify({"status": "error", "message": "Timer is already active."}), 400

    data = request.json
    duration = data.get('duration')

    if duration is None or not isinstance(duration, (int, float)) or duration <= 0:
        return jsonify({"status": "error", "message": "Invalid duration provided."}), 400

    remaining_time = int(duration)
    timer_active = True

    if root and timer_label:
        if timer_thread and timer_thread.is_alive():
            logger.warning("Previous timer thread still alive.")
    
        timer_thread = threading.Thread(target=countdown_timer_task, daemon=True)
        timer_thread.start()
        logger.info(f"Timer started for {duration} seconds on {rig_identifier}")
        return jsonify({"status": "success", "message": f"Timer started for {duration} seconds."})
    else:
        return jsonify({"status": "error", "message": "GUI not initialized."}), 500

@app.route('/status', methods=['GET'])
def get_timer_status():
    """Get current timer status."""
    return jsonify({
        "rig_identifier": rig_identifier,
        "timer_active": timer_active,
        "remaining_time": remaining_time
    })

def countdown_timer_task():
    """Main countdown timer logic."""
    global remaining_time, timer_active, timer_label

    logger.info(f"Timer started: {remaining_time} seconds on {rig_identifier}")
    while remaining_time > 0 and timer_active:
        if timer_label:
            root.after(0, update_timer_display, format_time(remaining_time))
        time.sleep(1)
        remaining_time -= 1

    if timer_active:
        root.after(0, update_timer_display, "TIME UP!")
        logger.info(f"Time's up on {rig_identifier}! Sending ESC key.")
        try:
            pydirectinput.press('esc')
            logger.info("ESC key sent via pydirectinput.")
        except Exception as e:
            logger.error(f"Error pressing ESC key with pydirectinput: {e}")
        
        time.sleep(3) 
        root.after(0, hide_timer_window)

    timer_active = False
    remaining_time = 0
    logger.info(f"Timer finished on {rig_identifier}")

def format_time(seconds):
    """Format seconds to MM:SS display."""
    mins = seconds // 60
    secs = seconds % 60
    return f"{mins:02d}:{secs:02d}"

def update_timer_display(time_str):
    """Update the timer display."""
    global timer_label, root
    if timer_label:
        timer_label.config(text=time_str)
    if root and not root.winfo_viewable():
        root.deiconify()

def hide_timer_window():
    """Hide the timer window."""
    global root
    if root:
        root.withdraw()

def ensure_window_visible():
    """Ensure timer window is visible."""
    global root
    if root and not root.winfo_viewable():
        root.deiconify()

def setup_gui():
    """Set up the timer GUI."""
    global root, timer_label

    root = tk.Tk()
    root.title(f"Rig Timer - {rig_identifier}")
    root.attributes('-alpha', 0.85)
    root.attributes('-topmost', True)
    root.overrideredirect(True)
    root.attributes('-transparentcolor', TRANSPARENT_COLOR)

    screen_width = root.winfo_screenwidth()
    screen_height = root.winfo_screenheight()
    
    x_pos = screen_width - WINDOW_WIDTH - WINDOW_POSITION_X_OFFSET
    y_pos = WINDOW_POSITION_Y_OFFSET

    root.geometry(f"{WINDOW_WIDTH}x{WINDOW_HEIGHT}+{x_pos}+{y_pos}")
    root.configure(bg=TRANSPARENT_COLOR)

    timer_label = tk.Label(root, text="00:00", font=FONT_SETTINGS, fg=TEXT_COLOR, bg=BACKGROUND_COLOR)
    timer_label.pack(expand=True, fill='both')
    
    root.withdraw()

    def check_and_show_window():
        if timer_active and not root.winfo_viewable():
            ensure_window_visible()
        root.after(1000, check_and_show_window)

    root.after(1000, check_and_show_window)
    root.mainloop()

def main():
    """Main entry point."""
    global rig_identifier
    
    parser = argparse.ArgumentParser(description='F1 Leaderboard Rig Timer Client')
    parser.add_argument('--rig-id', required=True, help='Rig identifier (e.g., RIG1, RIG2, etc.)')
    parser.add_argument('--host', default=DEFAULT_HOST, help=f'Host to bind to (default: {DEFAULT_HOST})')
    parser.add_argument('--port', type=int, default=DEFAULT_PORT, help=f'Port to bind to (default: {DEFAULT_PORT})')
    
    args = parser.parse_args()
    rig_identifier = args.rig_id
    
    logger.info(f"Starting F1 Leaderboard Timer Client for {rig_identifier}")
    logger.info(f"Server will listen on {args.host}:{args.port}")
    
    # Start Flask app in a separate thread
    flask_thread = threading.Thread(target=run_flask_app, args=(args.host, args.port), daemon=True)
    flask_thread.start()
    logger.info(f"Timer server started for {rig_identifier}")

    # Start Tkinter GUI in the main thread
    logger.info(f"Starting Timer GUI for {rig_identifier}. Waiting for timer commands...")
    setup_gui()

if __name__ == "__main__":
    main() 