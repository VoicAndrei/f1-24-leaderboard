#!/usr/bin/env python3
"""
F1 Simulator Timer Launcher

A GUI application to configure and launch the timer.
"""

import os
import sys
import tkinter as tk
from tkinter import ttk
import subprocess

class TimerLauncher:
    def __init__(self):
        self.root = tk.Tk()
        self.root.title("F1 Simulator Timer Launcher")
        self.root.geometry("400x350")
        self.root.resizable(False, False)
        
        # Set the icon if available
        try:
            self.root.iconbitmap("timer_icon.ico")
        except tk.TclError:
            pass
        
        self.setup_ui()
        self.root.mainloop()
    
    def setup_ui(self):
        """Set up the user interface."""
        # Main frame with padding
        main_frame = ttk.Frame(self.root, padding="20 20 20 20")
        main_frame.pack(fill=tk.BOTH, expand=True)
        
        # Title
        title_label = ttk.Label(
            main_frame, 
            text="F1 Simulator Timer", 
            font=('Arial', 16, 'bold')
        )
        title_label.pack(pady=(0, 20))
        
        # Rig selection
        rig_frame = ttk.Frame(main_frame)
        rig_frame.pack(fill=tk.X, pady=5)
        
        ttk.Label(rig_frame, text="Rig Number:").pack(side=tk.LEFT)
        
        self.rig_var = tk.IntVar(value=1)
        rig_combo = ttk.Combobox(
            rig_frame, 
            textvariable=self.rig_var,
            values=[1, 2, 3],
            width=5,
            state="readonly"
        )
        rig_combo.pack(side=tk.RIGHT)
        
        # Time selection
        time_frame = ttk.Frame(main_frame)
        time_frame.pack(fill=tk.X, pady=5)
        
        ttk.Label(time_frame, text="Timer Duration (minutes):").pack(side=tk.LEFT)
        
        self.time_var = tk.IntVar(value=10)
        time_options = [1, 2, 3, 5, 10, 15, 20, 30]
        time_combo = ttk.Combobox(
            time_frame, 
            textvariable=self.time_var,
            values=time_options,
            width=5,
            state="readonly"
        )
        time_combo.pack(side=tk.RIGHT)
        
        # Position selection
        position_frame = ttk.Frame(main_frame)
        position_frame.pack(fill=tk.X, pady=5)
        
        ttk.Label(position_frame, text="Timer Position:").pack(side=tk.LEFT)
        
        self.position_var = tk.StringVar(value="top-right")
        position_options = ["top-right", "top-left", "bottom-right", "bottom-left"]
        position_combo = ttk.Combobox(
            position_frame, 
            textvariable=self.position_var,
            values=position_options,
            width=12,
            state="readonly"
        )
        position_combo.pack(side=tk.RIGHT)
        
        # Preset buttons
        presets_frame = ttk.LabelFrame(main_frame, text="Quick Presets")
        presets_frame.pack(fill=tk.X, pady=15)
        
        presets_grid = ttk.Frame(presets_frame)
        presets_grid.pack(padx=10, pady=10)
        
        # First row of presets
        ttk.Button(
            presets_grid, 
            text="3 Minutes",
            command=lambda: self.set_preset(3)
        ).grid(row=0, column=0, padx=5, pady=5)
        
        ttk.Button(
            presets_grid, 
            text="5 Minutes",
            command=lambda: self.set_preset(5)
        ).grid(row=0, column=1, padx=5, pady=5)
        
        ttk.Button(
            presets_grid, 
            text="10 Minutes",
            command=lambda: self.set_preset(10)
        ).grid(row=0, column=2, padx=5, pady=5)
        
        # Start button
        start_button = ttk.Button(
            main_frame,
            text="Start Timer",
            command=self.start_timer,
            style="Accent.TButton"
        )
        start_button.pack(pady=20, ipadx=10, ipady=5)
        
        # Register custom style for accent button
        self.register_styles()
    
    def register_styles(self):
        """Register custom styles for buttons."""
        style = ttk.Style()
        if "Accent.TButton" not in style.theme_names():
            style.configure("Accent.TButton", 
                            font=('Arial', 12, 'bold'),
                            foreground='white',
                            background='#4CAF50')
    
    def set_preset(self, minutes):
        """Set a preset time value."""
        self.time_var.set(minutes)
    
    def start_timer(self):
        """Start the timer with the selected settings."""
        rig = self.rig_var.get()
        minutes = self.time_var.get()
        position = self.position_var.get()
        
        # Get the directory of the current script
        script_dir = os.path.dirname(os.path.abspath(__file__))
        timer_script = os.path.join(script_dir, "timer.py")
        
        # Create the command
        cmd = [
            sys.executable,
            timer_script,
            "--rig", str(rig),
            "--minutes", str(minutes),
            "--position", position
        ]
        
        # Launch the timer in a separate process
        subprocess.Popen(cmd)
        
        # Close the launcher
        self.root.destroy()

if __name__ == "__main__":
    TimerLauncher() 