import tkinter as tk
import threading
import time
# import pyautogui # We'll replace this for the key press
import pydirectinput # Added for more reliable game input
from flask import Flask, request, jsonify

# --- Configuration ---
RIG_PC_HOST = '0.0.0.0'  # Listen on all available network interfaces
RIG_PC_PORT = 5001
WINDOW_WIDTH = 200
WINDOW_HEIGHT = 80
WINDOW_POSITION_X_OFFSET = 50  # Offset from right edge
WINDOW_POSITION_Y_OFFSET = 50  # Offset from top edge
FONT_SETTINGS = ("Arial", 30, "bold")
TRANSPARENT_COLOR = 'grey15'  # A color to make transparent
TEXT_COLOR = 'white'
BACKGROUND_COLOR = TRANSPARENT_COLOR # Make background same as transparent color

# --- Global variables for timer state ---
timer_active = False
remaining_time = 0
timer_thread = None
root = None
timer_label = None

# --- Flask App ---
app = Flask(__name__)

def run_flask_app():
    app.run(host=RIG_PC_HOST, port=RIG_PC_PORT)

@app.route('/start_timer', methods=['POST'])
def start_timer_endpoint():
    global timer_active, remaining_time, timer_thread, root
    if timer_active:
        return jsonify({"status": "error", "message": "Timer is already active."}), 400

    data = request.json
    duration = data.get('duration')

    if duration is None or not isinstance(duration, (int, float)) or duration <= 0:
        return jsonify({"status": "error", "message": "Invalid duration provided."}), 400

    remaining_time = int(duration)
    timer_active = True

    if root and timer_label: # Ensure GUI is initialized
        if timer_thread and timer_thread.is_alive():
            # Should not happen if timer_active is managed correctly
            print("Warning: Previous timer thread still alive.")
    
        timer_thread = threading.Thread(target=countdown_timer_task, daemon=True)
        timer_thread.start()
        return jsonify({"status": "success", "message": f"Timer started for {duration} seconds."})
    else:
        # This case should ideally not be hit if GUI starts first
        return jsonify({"status": "error", "message": "GUI not initialized."}), 500


# --- Timer Logic ---
def countdown_timer_task():
    global remaining_time, timer_active, timer_label

    print(f"Timer started: {remaining_time} seconds.")
    while remaining_time > 0 and timer_active:
        if timer_label:
            # Update GUI from the main thread using 'after'
            root.after(0, update_timer_display, format_time(remaining_time))
        time.sleep(1)
        remaining_time -= 1

    if timer_active: # Ensures action only if timer completed normally
        root.after(0, update_timer_display, "TIME UP!")
        print("Time's up! Sending ESC key.")
        try:
            # pyautogui.press('esc') # Old method
            pydirectinput.press('esc') # New method using pydirectinput
            print("ESC key sent via pydirectinput.")
        except Exception as e:
            print(f"Error pressing ESC key with pydirectinput: {e}")
        
        # Give a moment for "TIME UP!" message before hiding/resetting
        time.sleep(3) 
        root.after(0, hide_timer_window) # Or reset

    timer_active = False
    remaining_time = 0
    print("Timer finished.")

def format_time(seconds):
    mins = seconds // 60
    secs = seconds % 60
    return f"{mins:02d}:{secs:02d}"

def update_timer_display(time_str):
    global timer_label, root
    if timer_label:
        timer_label.config(text=time_str)
    if root and not root.winfo_viewable(): # if hidden, show it
        root.deiconify()


def hide_timer_window():
    global root
    if root:
        root.withdraw() # Hide the window

def ensure_window_visible():
    global root
    if root and not root.winfo_viewable():
        root.deiconify()

# --- Tkinter GUI ---
def setup_gui():
    global root, timer_label

    root = tk.Tk()
    root.title("Rig Timer")
    root.attributes('-alpha', 0.85)  # Overall window transparency (0.0 fully transparent, 1.0 opaque)
    root.attributes('-topmost', True) # Keep window on top
    root.overrideredirect(True) # Remove window decorations (title bar, borders)

    # Make a specific color transparent (works best on Windows)
    # On some systems, this might make the whole window click-through for that color
    root.attributes('-transparentcolor', TRANSPARENT_COLOR)

    screen_width = root.winfo_screenwidth()
    screen_height = root.winfo_screenheight()
    
    x_pos = screen_width - WINDOW_WIDTH - WINDOW_POSITION_X_OFFSET
    y_pos = WINDOW_POSITION_Y_OFFSET

    root.geometry(f"{WINDOW_WIDTH}x{WINDOW_HEIGHT}+{x_pos}+{y_pos}")
    root.configure(bg=TRANSPARENT_COLOR) # Set background color

    timer_label = tk.Label(root, text="00:00", font=FONT_SETTINGS, fg=TEXT_COLOR, bg=BACKGROUND_COLOR)
    timer_label.pack(expand=True, fill='both')
    
    root.withdraw() # Start hidden, show when timer starts

    # Periodically check if timer is active and window should be shown
    def check_and_show_window():
        if timer_active and not root.winfo_viewable():
            ensure_window_visible()
        root.after(1000, check_and_show_window) # Check every second

    root.after(1000, check_and_show_window)
    root.mainloop()


if __name__ == "__main__":
    # Start Flask app in a separate thread
    flask_thread = threading.Thread(target=run_flask_app, daemon=True)
    flask_thread.start()
    print(f"Flask server starting on http://{RIG_PC_HOST}:{RIG_PC_PORT}")

    # Start Tkinter GUI in the main thread
    print("Starting Rig Timer GUI. Waiting for timer commands...")
    setup_gui() 