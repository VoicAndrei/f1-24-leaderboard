#!/usr/bin/env python3
"""
F1 Simulator Timer Control

A GUI application for the operator to control the timers on the rig PCs.
"""

import tkinter as tk
from tkinter import ttk, messagebox
import socket
import json
import threading
import time
import os
import configparser

# Default configuration
DEFAULT_RIG_IP = "127.0.0.1"  # Default to localhost for testing
DEFAULT_PORT = 5678

class TimerControl:
    def __init__(self):
        self.root = tk.Tk()
        self.root.title("F1 Simulator Timer Control")
        self.root.geometry("450x420")
        self.root.resizable(False, False)
        
        # Set the icon if available
        try:
            self.root.iconbitmap("timer_icon.ico")
        except tk.TclError:
            pass
        
        # Load rig configuration
        self.config = self.load_config()
        
        # Setup UI
        self.setup_ui()
        
        # Initialize status polling
        self.timer_status = {"running": False}
        self.status_thread = None
        self.stop_polling = False
        
        # Start status polling
        self.start_status_polling()
        
        # Handle window close
        self.root.protocol("WM_DELETE_WINDOW", self.on_close)
        
        # Start the main loop
        self.root.mainloop()
    
    def load_config(self):
        """Load the configuration from file or create default if not exists."""
        config = configparser.ConfigParser()
        config_file = os.path.join(os.path.dirname(os.path.abspath(__file__)), "timer_config.ini")
        
        if os.path.exists(config_file):
            config.read(config_file)
        else:
            # Create default config
            config["RIG1"] = {
                "ip": DEFAULT_RIG_IP,
                "port": str(DEFAULT_PORT),
                "name": "Rig 1"
            }
            config["RIG2"] = {
                "ip": DEFAULT_RIG_IP,
                "port": str(DEFAULT_PORT + 1),
                "name": "Rig 2"
            }
            config["RIG3"] = {
                "ip": DEFAULT_RIG_IP,
                "port": str(DEFAULT_PORT + 2),
                "name": "Rig 3"
            }
            
            with open(config_file, "w") as f:
                config.write(f)
        
        return config
    
    def setup_ui(self):
        """Set up the user interface."""
        # Main frame with padding
        main_frame = ttk.Frame(self.root, padding="20 20 20 20")
        main_frame.pack(fill=tk.BOTH, expand=True)
        
        # Title
        title_label = ttk.Label(
            main_frame, 
            text="F1 Simulator Timer Control", 
            font=('Arial', 16, 'bold')
        )
        title_label.pack(pady=(0, 20))
        
        # Rig selection
        rig_frame = ttk.LabelFrame(main_frame, text="Select Rig")
        rig_frame.pack(fill=tk.X, pady=10)
        
        rig_inner_frame = ttk.Frame(rig_frame, padding=10)
        rig_inner_frame.pack(fill=tk.X)
        
        # Set up rig selection radiobuttons
        self.rig_var = tk.StringVar(value="RIG1")  # Default to RIG1
        
        rig_options = []
        for section in self.config.sections():
            if section.startswith("RIG"):
                rig_name = self.config[section]["name"]
                rig_ip = self.config[section]["ip"]
                option_text = f"{rig_name} ({rig_ip})"
                rig_options.append((option_text, section))
        
        # Create a radiobutton for each rig
        for i, (text, value) in enumerate(rig_options):
            ttk.Radiobutton(
                rig_inner_frame,
                text=text,
                value=value,
                variable=self.rig_var
            ).grid(row=0, column=i, padx=10)
        
        # Timer configuration
        timer_frame = ttk.LabelFrame(main_frame, text="Timer Settings")
        timer_frame.pack(fill=tk.X, pady=10)
        
        timer_inner_frame = ttk.Frame(timer_frame, padding=10)
        timer_inner_frame.pack(fill=tk.X)
        
        # Time selection
        time_frame = ttk.Frame(timer_inner_frame)
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
        position_frame = ttk.Frame(timer_inner_frame)
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
        presets_frame.pack(fill=tk.X, pady=10)
        
        presets_grid = ttk.Frame(presets_frame, padding=10)
        presets_grid.pack(fill=tk.X)
        
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
        
        # Control buttons
        controls_frame = ttk.Frame(main_frame)
        controls_frame.pack(fill=tk.X, pady=10)
        
        # Start button
        self.start_button = ttk.Button(
            controls_frame,
            text="Start Timer",
            command=self.start_timer,
            style="Start.TButton"
        )
        self.start_button.pack(side=tk.LEFT, expand=True, fill=tk.X, padx=5)
        
        # Stop button
        self.stop_button = ttk.Button(
            controls_frame,
            text="Stop Timer",
            command=self.stop_timer,
            style="Stop.TButton"
        )
        self.stop_button.pack(side=tk.RIGHT, expand=True, fill=tk.X, padx=5)
        
        # Status frame
        status_frame = ttk.LabelFrame(main_frame, text="Status")
        status_frame.pack(fill=tk.X, pady=10)
        
        status_inner_frame = ttk.Frame(status_frame, padding=10)
        status_inner_frame.pack(fill=tk.X)
        
        # Connection status
        self.status_label = ttk.Label(
            status_inner_frame,
            text="Not connected",
            padding=(0, 0, 0, 5)
        )
        self.status_label.pack(fill=tk.X)
        
        # Remaining time display
        time_display_frame = ttk.Frame(status_inner_frame)
        time_display_frame.pack(fill=tk.X, pady=(5, 0))
        
        ttk.Label(
            time_display_frame,
            text="Remaining Time:",
            font=('Arial', 10, 'bold')
        ).pack(side=tk.LEFT)
        
        self.remaining_time_label = ttk.Label(
            time_display_frame,
            text="00:00",
            font=('Arial', 12, 'bold'),
            padding=(10, 0, 0, 0)
        )
        self.remaining_time_label.pack(side=tk.LEFT)
        
        # Progress bar
        self.progress_var = tk.IntVar(value=0)
        self.progress_bar = ttk.Progressbar(
            status_inner_frame,
            variable=self.progress_var,
            maximum=100,
            mode='determinate',
            length=200
        )
        self.progress_bar.pack(fill=tk.X, pady=(5, 0))
        
        # Register custom button styles
        self.register_styles()
    
    def register_styles(self):
        """Register custom styles for buttons."""
        style = ttk.Style()
        
        # Start button style (green)
        style.configure("Start.TButton", 
                        font=('Arial', 11, 'bold'),
                        foreground='white',
                        background='#4CAF50')
        
        # Stop button style (red)
        style.configure("Stop.TButton", 
                        font=('Arial', 11, 'bold'),
                        foreground='white',
                        background='#F44336')
    
    def set_preset(self, minutes):
        """Set a preset time value."""
        self.time_var.set(minutes)
    
    def get_rig_info(self):
        """Get the IP and port for the selected rig."""
        rig_id = self.rig_var.get()
        if rig_id in self.config:
            return {
                "ip": self.config[rig_id]["ip"],
                "port": int(self.config[rig_id]["port"]),
                "name": self.config[rig_id]["name"]
            }
        return None
    
    def send_command(self, command):
        """Send a command to the selected rig."""
        rig_info = self.get_rig_info()
        if not rig_info:
            messagebox.showerror("Error", "Invalid rig selection")
            return None
        
        try:
            # Create socket connection
            client_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
            client_socket.settimeout(5)  # 5 second timeout
            client_socket.connect((rig_info["ip"], rig_info["port"]))
            
            # Send the command
            client_socket.send(json.dumps(command).encode('utf-8'))
            
            # Receive the response
            response_data = client_socket.recv(1024).decode('utf-8')
            response = json.loads(response_data)
            
            # Close the connection
            client_socket.close()
            
            return response
        
        except socket.timeout:
            messagebox.showerror("Connection Error", f"Connection to {rig_info['name']} timed out")
            return None
        
        except ConnectionRefusedError:
            messagebox.showerror(
                "Connection Error", 
                f"Connection to {rig_info['name']} refused.\nIs the timer server running?"
            )
            return None
        
        except Exception as e:
            messagebox.showerror("Error", f"Failed to send command: {str(e)}")
            return None
    
    def start_timer(self):
        """Start the timer on the selected rig."""
        minutes = self.time_var.get()
        position = self.position_var.get()
        rig_info = self.get_rig_info()
        
        if not rig_info:
            return
        
        # Confirm the action
        result = messagebox.askyesno(
            "Confirm Start Timer",
            f"Start a {minutes} minute timer on {rig_info['name']}?"
        )
        
        if not result:
            return
        
        # Send the start command
        command = {
            "action": "start",
            "minutes": minutes,
            "position": position
        }
        
        response = self.send_command(command)
        
        if response and response.get("status") == "success":
            messagebox.showinfo("Success", response.get("message", "Timer started"))
            self.update_status({"running": True})
        elif response:
            messagebox.showerror("Error", response.get("message", "Unknown error"))
    
    def stop_timer(self):
        """Stop the timer on the selected rig."""
        rig_info = self.get_rig_info()
        
        if not rig_info:
            return
        
        # Confirm the action
        result = messagebox.askyesno(
            "Confirm Stop Timer",
            f"Stop the timer on {rig_info['name']}?"
        )
        
        if not result:
            return
        
        # Send the stop command
        command = {
            "action": "stop"
        }
        
        response = self.send_command(command)
        
        if response and response.get("status") == "success":
            messagebox.showinfo("Success", response.get("message", "Timer stopped"))
            self.update_status({"running": False})
        elif response:
            messagebox.showerror("Error", response.get("message", "Unknown error"))
    
    def check_status(self):
        """Check the status of the timer on the selected rig."""
        # Send the status command
        command = {
            "action": "status"
        }
        
        response = self.send_command(command)
        
        if response and response.get("status") == "success":
            self.update_status({
                "running": response.get("timer_running", False),
                "rig_id": response.get("rig_id", "Unknown"),
                "timestamp": response.get("timestamp", "")
            })
            return True
        return False
    
    def update_status(self, status):
        """Update the UI with the current status."""
        self.timer_status = status
        rig_info = self.get_rig_info()
        
        if rig_info:
            if status.get("running", False):
                # Update connection status
                self.status_label.config(
                    text=f"Timer is RUNNING on {rig_info['name']}",
                    foreground="#4CAF50"  # Green
                )
                
                # Update remaining time
                remaining_time = status.get("formatted_remaining", "00:00")
                self.remaining_time_label.config(
                    text=remaining_time,
                    foreground="#4CAF50" if status.get("remaining_seconds", 0) > 30 else "#FF9800"
                )
                
                # Update progress bar
                progress = status.get("progress_percent", 0)
                self.progress_var.set(progress)
                
                # Make remaining time and progress bar visible
                self.remaining_time_label.pack(side=tk.LEFT)
                self.progress_bar.pack(fill=tk.X, pady=(5, 0))
            else:
                # Update connection status
                self.status_label.config(
                    text=f"Timer is STOPPED on {rig_info['name']}",
                    foreground="#F44336"  # Red
                )
                
                # Update remaining time
                self.remaining_time_label.config(
                    text="00:00",
                    foreground="#000000"
                )
                
                # Reset progress bar
                self.progress_var.set(0)
        else:
            self.status_label.config(
                text="Not connected",
                foreground="black"
            )
            
            # Reset remaining time
            self.remaining_time_label.config(
                text="00:00",
                foreground="#000000"
            )
            
            # Reset progress bar
            self.progress_var.set(0)
    
    def start_status_polling(self):
        """Start a background thread to poll for status updates."""
        self.stop_polling = False
        
        def poll_status():
            while not self.stop_polling:
                try:
                    # Only poll if window is still open
                    if self.root.winfo_exists():
                        self.check_status()
                    else:
                        break
                except:
                    pass
                
                # Wait before polling again
                time.sleep(5)
        
        self.status_thread = threading.Thread(target=poll_status)
        self.status_thread.daemon = True
        self.status_thread.start()
    
    def on_close(self):
        """Handle window close event."""
        # Stop the status polling thread
        self.stop_polling = True
        if self.status_thread:
            self.status_thread.join(0.1)
        
        # Close the window
        self.root.destroy()

if __name__ == "__main__":
    TimerControl() 