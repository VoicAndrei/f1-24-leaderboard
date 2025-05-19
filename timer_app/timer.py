#!/usr/bin/env python3
"""
F1 Simulator Timer Application

A simple application that displays a transparent countdown timer
and sends an ESC key when the timer expires to pause the game.

Usage:
    python timer.py --rig RIG_NUMBER --minutes MINUTES

Example:
    python timer.py --rig 1 --minutes 10
"""

import argparse
import time
import tkinter as tk
import pyautogui
from datetime import datetime, timedelta

# Constants
DEFAULT_MINUTES = 10
DEFAULT_RIG = 1
FONT_SIZE = 36
REFRESH_RATE_MS = 100  # Refresh rate in milliseconds
OVERLAY_BG_COLOR = "#000000"  # Black
OVERLAY_FG_COLOR = "#00FF00"  # Green
OVERLAY_OPACITY = 0.7  # 70% opacity
OVERLAY_PADDING = 20
POSITION = "top-right"  # Options: top-right, top-left, bottom-right, bottom-left

class CountdownTimer:
    def __init__(self, rig_id, minutes, position=POSITION):
        self.rig_id = rig_id
        self.position = position
        self.end_time = datetime.now() + timedelta(minutes=minutes)
        
        # Create the main window
        self.root = tk.Tk()
        self.root.overrideredirect(True)  # Remove window decorations
        self.root.wm_attributes("-topmost", True)  # Keep on top of other windows
        self.root.wm_attributes("-transparentcolor", OVERLAY_BG_COLOR)  # Make background transparent
        self.root.wm_attributes("-alpha", OVERLAY_OPACITY)  # Set window opacity
        
        # Set window position
        self.set_window_position()
        
        # Create the label for time display
        self.time_label = tk.Label(
            self.root,
            text="00:00",
            font=("Arial", FONT_SIZE, "bold"),
            bg=OVERLAY_BG_COLOR,
            fg=OVERLAY_FG_COLOR,
            padx=OVERLAY_PADDING,
            pady=OVERLAY_PADDING
        )
        self.time_label.pack()
        
        # Start the timer
        self.update_timer()
        
        # Start the main loop
        self.root.mainloop()
    
    def set_window_position(self):
        """Position the window in the specified corner of the screen."""
        screen_width = self.root.winfo_screenwidth()
        screen_height = self.root.winfo_screenheight()
        
        window_width = 200  # Approximate width
        window_height = 100  # Approximate height
        
        if self.position == "top-right":
            x = screen_width - window_width - 50
            y = 50
        elif self.position == "top-left":
            x = 50
            y = 50
        elif self.position == "bottom-right":
            x = screen_width - window_width - 50
            y = screen_height - window_height - 50
        elif self.position == "bottom-left":
            x = 50
            y = screen_height - window_height - 50
        else:
            # Default to top-right
            x = screen_width - window_width - 50
            y = 50
        
        self.root.geometry(f"+{x}+{y}")
    
    def update_timer(self):
        """Update the timer display and check if time has expired."""
        time_remaining = self.end_time - datetime.now()
        
        if time_remaining.total_seconds() <= 0:
            # Time expired
            self.time_label.config(text="TIME UP!", fg="#FF0000")  # Red text
            self.send_escape_key()
            # Wait 5 seconds before closing
            self.root.after(5000, self.root.destroy)
            return
        
        # Format the time remaining
        minutes = int(time_remaining.total_seconds() // 60)
        seconds = int(time_remaining.total_seconds() % 60)
        time_str = f"{minutes:02d}:{seconds:02d}"
        
        # Update the label
        self.time_label.config(text=f"RIG {self.rig_id}: {time_str}")
        
        # Schedule the next update
        self.root.after(REFRESH_RATE_MS, self.update_timer)
    
    def send_escape_key(self):
        """Send the ESC key to pause the game."""
        print(f"Time expired for RIG {self.rig_id}. Sending ESC key...")
        try:
            pyautogui.press('esc')
            print("ESC key sent successfully.")
        except Exception as e:
            print(f"Error sending ESC key: {e}")

def parse_arguments():
    """Parse command line arguments."""
    parser = argparse.ArgumentParser(description="F1 Simulator Timer Application")
    parser.add_argument("--rig", type=int, default=DEFAULT_RIG, help="The rig number (default: 1)")
    parser.add_argument("--minutes", type=int, default=DEFAULT_MINUTES, help="Timer duration in minutes (default: 10)")
    parser.add_argument("--position", type=str, default=POSITION, 
                        choices=["top-right", "top-left", "bottom-right", "bottom-left"],
                        help="Position of the timer on screen (default: top-right)")
    return parser.parse_args()

if __name__ == "__main__":
    args = parse_arguments()
    print(f"Starting timer for RIG {args.rig} for {args.minutes} minutes")
    CountdownTimer(args.rig, args.minutes, args.position) 