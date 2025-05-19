import requests
import json
import sys # Added for command-line arguments

# --- Configuration ---
# !!! IMPORTANT: Replace 'RIG1_IP_ADDRESS' with the actual IP address of Rig 1 !!!
RIG1_IP_ADDRESS = '192.168.0.204' # e.g., '192.168.1.101'
RIG_PC_PORT = 5001 # Must match the port used in rig_timer_display.py
TIMER_ENDPOINT_URL = f"http://{RIG1_IP_ADDRESS}:{RIG_PC_PORT}/start_timer"

def send_timer_request(duration_seconds, duration_minutes_display):
    """Sends the timer request to the rig PC."""
    if RIG1_IP_ADDRESS == 'RIG1_IP_ADDRESS': # Check if placeholder is still there
        print("ERROR: Please update RIG1_IP_ADDRESS in the script with the actual IP of Rig 1.")
        return False

    payload = {"duration": duration_seconds}
    print(f"\nSending request to {TIMER_ENDPOINT_URL} for {duration_minutes_display} minutes with payload: {payload}")

    try:
        response = requests.post(TIMER_ENDPOINT_URL, json=payload, timeout=10) # 10 second timeout
        response.raise_for_status() # Raise an exception for HTTP errors (4xx or 5xx)
        
        response_data = response.json()
        if response_data.get("status") == "success":
            print(f"Successfully started timer on Rig 1 for {duration_minutes_display} minutes.")
            print(f"Message from rig: {response_data.get('message')}")
            return True
        else:
            print(f"Rig 1 reported an error: {response_data.get('message', 'Unknown error')}")
            return False

    except requests.exceptions.ConnectionError:
        print(f"Error: Could not connect to Rig 1 at {RIG1_IP_ADDRESS}:{RIG_PC_PORT}. Is the timer script running on Rig 1?")
    except requests.exceptions.Timeout:
        print(f"Error: Request to Rig 1 timed out. Check network connection and if the rig script is responsive.")
    except requests.exceptions.HTTPError as e:
        print(f"Error: HTTP error from Rig 1: {e.response.status_code} {e.response.reason}")
        try:
            error_details = e.response.json()
            print(f"Details: {error_details.get('message', 'No additional details')}")
        except json.JSONDecodeError:
            print(f"Details: {e.response.text}")
    except requests.exceptions.RequestException as e:
        print(f"An unexpected error occurred: {e}")
    except Exception as e:
        print(f"An unexpected error occurred during the request: {e}")
    return False

def set_timer_interactive():
    """Handles interactive timer setting."""
    while True:
        try:
            duration_minutes_str = input("Enter timer duration for Rig 1 in minutes (e.g., 10): ")
            if not duration_minutes_str:
                print("No input provided. Please try again.")
                continue
            duration_minutes = float(duration_minutes_str)
            if duration_minutes <= 0:
                print("Duration must be positive. Please try again.")
                continue
            duration_seconds = int(duration_minutes * 60)
            send_timer_request(duration_seconds, duration_minutes)
            break # Exit loop after attempting to send
        except ValueError:
            print("Invalid input. Please enter a number (e.g., 10 or 7.5).")

if __name__ == "__main__":
    quick_start_triggered = False
    if len(sys.argv) > 1 and sys.argv[1] == '--quick10':
        print("--- Rig 1 Timer Control (Quick Start: 10 Minutes) ---")
        if send_timer_request(600, 10): # 10 minutes = 600 seconds
            print("Quick start command sent.")
        else:
            print("Quick start command failed.")
        quick_start_triggered = True
        # For quick start, exit immediately after attempting.
        # If you want it to stay open, remove the 'sys.exit()' or adjust logic.
        # For now, let's let it fall through to the input() for consistency,
        # or user can close the window.
    else:
        print("--- Rig 1 Timer Control (Interactive Mode) ---")
        if RIG1_IP_ADDRESS == 'RIG1_IP_ADDRESS': # Check placeholder before interactive mode
            print("ERROR: Please update RIG1_IP_ADDRESS in the script with the actual IP of Rig 1 before proceeding.")
        else:
            set_timer_interactive()

    if not quick_start_triggered: # Only ask for input if not a quick start
        input("\nPress Enter to exit...")
    else:
        # In case of quick start, a small delay might be good if the user wants to see the message
        # Or we can print a message like "Exiting in 3 seconds..." and then time.sleep(3)
        # For now, keeping it simple. If the .bat file is used, the window might close quickly.
        print("\nQuick start finished. Window will close or press Enter.")
        input() # Still wait for Enter so user can see output if run from cmd directly 