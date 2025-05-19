#!/usr/bin/env python3
"""
F1 Simulator Timer Server

This script runs on the rig PC and listens for timer commands from the operator PC.
"""

import socket
import json
import threading
import subprocess
import sys
import os
import logging
from datetime import datetime, timedelta

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s',
    filename='timer_server.log',
    filemode='a'
)
logger = logging.getLogger(__name__)

# Server configuration
HOST = '0.0.0.0'  # Listen on all interfaces
PORT = 5678  # Port to listen on
RIG_ID = 1  # Default rig ID (can be overridden by command-line args)

# Track the current timer process
current_timer_process = None
timer_lock = threading.Lock()

# Timer state information
timer_state = {
    "start_time": None,
    "end_time": None,
    "duration_minutes": 0,
    "position": "top-right"
}

def format_time(seconds):
    """Format seconds into MM:SS format."""
    if seconds <= 0:
        return "00:00"
    
    minutes = int(seconds // 60)
    secs = int(seconds % 60)
    return f"{minutes:02d}:{secs:02d}"

def start_timer(minutes, position="top-right"):
    """Start a new timer process."""
    global current_timer_process, timer_state
    
    with timer_lock:
        # Kill any existing timer first
        stop_timer()
        
        # Record timer state information
        now = datetime.now()
        timer_state = {
            "start_time": now,
            "end_time": now + timedelta(minutes=minutes),
            "duration_minutes": minutes,
            "position": position
        }
        
        # Get the directory of the current script
        script_dir = os.path.dirname(os.path.abspath(__file__))
        timer_script = os.path.join(script_dir, "timer.py")
        
        # Create the command
        cmd = [
            sys.executable,
            timer_script,
            "--rig", str(RIG_ID),
            "--minutes", str(minutes),
            "--position", position
        ]
        
        # Start the timer process
        try:
            logger.info(f"Starting timer: {minutes} minutes, position: {position}")
            current_timer_process = subprocess.Popen(cmd)
            return True
        except Exception as e:
            logger.error(f"Error starting timer: {e}")
            timer_state = {"start_time": None, "end_time": None, "duration_minutes": 0, "position": "top-right"}
            return False

def stop_timer():
    """Stop the current timer if one is running."""
    global current_timer_process, timer_state
    
    with timer_lock:
        if current_timer_process is not None:
            try:
                logger.info("Stopping current timer")
                current_timer_process.terminate()
                current_timer_process = None
                timer_state = {"start_time": None, "end_time": None, "duration_minutes": 0, "position": "top-right"}
                return True
            except Exception as e:
                logger.error(f"Error stopping timer: {e}")
                return False
        return True  # No timer running is still a success

def handle_client(client_socket):
    """Handle communication with a client (operator PC)."""
    try:
        # Receive data from the client
        data = client_socket.recv(1024).decode('utf-8')
        
        if not data:
            return
        
        # Parse the JSON command
        try:
            command = json.loads(data)
            logger.info(f"Received command: {command}")
            
            # Process the command
            if command.get('action') == 'start':
                minutes = int(command.get('minutes', 10))
                position = command.get('position', 'top-right')
                success = start_timer(minutes, position)
                
                response = {
                    'status': 'success' if success else 'error',
                    'message': f"Timer started: {minutes} minutes" if success else "Failed to start timer",
                    'timestamp': str(datetime.now())
                }
            
            elif command.get('action') == 'stop':
                success = stop_timer()
                
                response = {
                    'status': 'success' if success else 'error',
                    'message': "Timer stopped" if success else "Failed to stop timer",
                    'timestamp': str(datetime.now())
                }
            
            elif command.get('action') == 'status':
                # Calculate remaining time if timer is running
                remaining_seconds = 0
                total_seconds = 0
                progress_percent = 0
                
                if current_timer_process is not None and timer_state["end_time"] is not None:
                    now = datetime.now()
                    if now < timer_state["end_time"]:
                        remaining_seconds = (timer_state["end_time"] - now).total_seconds()
                        total_seconds = timer_state["duration_minutes"] * 60
                        progress_percent = 100 - (remaining_seconds / total_seconds * 100)
                
                response = {
                    'status': 'success',
                    'timer_running': current_timer_process is not None,
                    'rig_id': RIG_ID,
                    'remaining_seconds': int(remaining_seconds),
                    'total_seconds': int(total_seconds),
                    'progress_percent': int(progress_percent),
                    'formatted_remaining': format_time(remaining_seconds),
                    'timestamp': str(datetime.now())
                }
            
            else:
                response = {
                    'status': 'error',
                    'message': "Unknown command",
                    'timestamp': str(datetime.now())
                }
        
        except json.JSONDecodeError:
            logger.error(f"Invalid JSON: {data}")
            response = {
                'status': 'error',
                'message': "Invalid command format",
                'timestamp': str(datetime.now())
            }
        
        except Exception as e:
            logger.error(f"Error processing command: {e}")
            response = {
                'status': 'error',
                'message': str(e),
                'timestamp': str(datetime.now())
            }
        
        # Send response back to client
        client_socket.send(json.dumps(response).encode('utf-8'))
    
    except Exception as e:
        logger.error(f"Error handling client: {e}")
    
    finally:
        # Close the connection
        client_socket.close()

def start_server():
    """Start the timer server."""
    server = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    server.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
    
    try:
        server.bind((HOST, PORT))
        server.listen(5)
        
        print(f"Timer Server started on Rig {RIG_ID}")
        print(f"Listening on {HOST}:{PORT}")
        print("Waiting for operator commands...")
        logger.info(f"Server started on {HOST}:{PORT} for Rig {RIG_ID}")
        
        while True:
            client_sock, address = server.accept()
            logger.info(f"Accepted connection from {address[0]}:{address[1]}")
            
            # Handle client in a separate thread
            client_handler = threading.Thread(target=handle_client, args=(client_sock,))
            client_handler.daemon = True
            client_handler.start()
    
    except KeyboardInterrupt:
        print("Server shutting down...")
        logger.info("Server shutting down (KeyboardInterrupt)")
    
    except Exception as e:
        print(f"Server error: {e}")
        logger.error(f"Server error: {e}")
    
    finally:
        server.close()
        stop_timer()  # Make sure to clean up any running timer

if __name__ == "__main__":
    import argparse
    
    # Parse command-line arguments
    parser = argparse.ArgumentParser(description="F1 Simulator Timer Server")
    parser.add_argument("--rig", type=int, default=1, help="The rig number (default: 1)")
    parser.add_argument("--port", type=int, default=PORT, help=f"Port to listen on (default: {PORT})")
    
    args = parser.parse_args()
    
    # Set global variables based on args
    RIG_ID = args.rig
    PORT = args.port
    
    # Start the server
    start_server() 