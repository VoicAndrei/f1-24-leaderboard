#!/usr/bin/env python3
"""
Direct Timer Launcher for F1 Rig

A simplified timer solution that avoids network connectivity issues.
This works by directly launching timers for pre-set durations.
"""

import os
import sys
import tkinter as tk
from tkinter import ttk
import subprocess
import threading
import time

# Constants for the UI
WINDOW_WIDTH = 500
WINDOW_HEIGHT = 300
BUTTON_WIDTH = 15
BUTTON_HEIGHT = 2
FONT_SIZE = 14
RIG_ID = 1  # Default rig ID

# Current timer process
current_timer_process = None
timer_lock = threading.Lock()

class DirectTimerApp:
    def __init__(self, root):
        self.root = root
        self.root.title(f"F1 Simulator Timer - Rig {RIG_ID}")
        self.root.geometry(f"{WINDOW_WIDTH}x{WINDOW_HEIGHT}")
        self.root.resizable(False, False)
        
        # Set up the main frame
        main_frame = ttk.Frame(self.root, padding="20")
        main_frame.pack(fill=tk.BOTH, expand=True)
        
        # Title
        title_label = ttk.Label(
            main_frame,
            text=f"F1 Simulator Timer - Rig {RIG_ID}",
            font=('Arial', 18, 'bold')
        )
        title_label.pack(pady=(0, 20))
        
        # Current timer status
        status_frame = ttk.LabelFrame(main_frame, text="Status")
        status_frame.pack(fill=tk.X, pady=10)
        
        self.status_label = ttk.Label(
            status_frame,
            text="No timer running",
            font=('Arial', 12),
            padding=10
        )
        self.status_label.pack(fill=tk.X)
        
        # Quick timer buttons
        buttons_frame = ttk.LabelFrame(main_frame, text="Start Timer")
        buttons_frame.pack(fill=tk.X, pady=10)
        
        button_grid = ttk.Frame(buttons_frame, padding=10)
        button_grid.pack()
        
        # First row of timer buttons
        ttk.Button(
            button_grid,
            text="3 Minutes",
            command=lambda: self.start_timer(3),
            width=BUTTON_WIDTH
        ).grid(row=0, column=0, padx=10, pady=10)
        
        ttk.Button(
            button_grid,
            text="5 Minutes",
            command=lambda: self.start_timer(5),
            width=BUTTON_WIDTH
        ).grid(row=0, column=1, padx=10, pady=10)
        
        ttk.Button(
            button_grid,
            text="10 Minutes",
            command=lambda: self.start_timer(10),
            width=BUTTON_WIDTH
        ).grid(row=0, column=2, padx=10, pady=10)
        
        # Second row of timer buttons
        ttk.Button(
            button_grid,
            text="15 Minutes",
            command=lambda: self.start_timer(15),
            width=BUTTON_WIDTH
        ).grid(row=1, column=0, padx=10, pady=10)
        
        ttk.Button(
            button_grid,
            text="20 Minutes",
            command=lambda: self.start_timer(20),
            width=BUTTON_WIDTH
        ).grid(row=1, column=1, padx=10, pady=10)
        
        ttk.Button(
            button_grid,
            text="30 Minutes",
            command=lambda: self.start_timer(30),
            width=BUTTON_WIDTH
        ).grid(row=1, column=2, padx=10, pady=10)
        
        # Stop button
        stop_button = ttk.Button(
            main_frame,
            text="Stop Current Timer",
            command=self.stop_timer,
            width=BUTTON_WIDTH
        )
        stop_button.pack(pady=10)
        
        # Setup timer checker
        self.timer_running = False
        self.check_timer_status()
    
    def start_timer(self, minutes):
        """Start a new timer with the specified duration."""
        global current_timer_process
        
        # Get the current script directory
        script_dir = os.path.dirname(os.path.abspath(__file__))
        timer_script = os.path.join(script_dir, "timer.py")
        
        # Create the command
        cmd = [
            sys.executable,
            timer_script,
            "--rig", str(RIG_ID),
            "--minutes", str(minutes),
            "--position", "top-right"
        ]
        
        with timer_lock:
            # Stop any existing timer
            self.stop_timer()
            
            try:
                # Start the timer process
                current_timer_process = subprocess.Popen(cmd)
                self.timer_running = True
                self.status_label.config(
                    text=f"Timer running: {minutes} minutes",
                    foreground="#4CAF50"  # Green
                )
            except Exception as e:
                self.status_label.config(
                    text=f"Error starting timer: {e}",
                    foreground="#F44336"  # Red
                )
    
    def stop_timer(self):
        """Stop the current timer if one is running."""
        global current_timer_process
        
        with timer_lock:
            if current_timer_process is not None:
                try:
                    current_timer_process.terminate()
                    current_timer_process = None
                    self.timer_running = False
                    self.status_label.config(
                        text="Timer stopped",
                        foreground="#F44336"  # Red
                    )
                except Exception as e:
                    self.status_label.config(
                        text=f"Error stopping timer: {e}",
                        foreground="#F44336"  # Red
                    )
    
    def check_timer_status(self):
        """Check if the timer is still running."""
        global current_timer_process
        
        with timer_lock:
            if current_timer_process is not None:
                if current_timer_process.poll() is not None:
                    # Process has exited
                    current_timer_process = None
                    self.timer_running = False
                    self.status_label.config(
                        text="Timer completed",
                        foreground="#2196F3"  # Blue
                    )
        
        # Schedule next check
        self.root.after(1000, self.check_timer_status)

def main():
    """Run the direct timer application."""
    global RIG_ID
    
    # Parse command line arguments
    import argparse
    parser = argparse.ArgumentParser(description="F1 Direct Timer Launcher")
    parser.add_argument("--rig", type=int, default=1, help="The rig number (default: 1)")
    args = parser.parse_args()
    
    # Set RIG_ID from args
    RIG_ID = args.rig
    
    # Create and run the application
    root = tk.Tk()
    app = DirectTimerApp(root)
    root.mainloop()

if __name__ == "__main__":
    main() 