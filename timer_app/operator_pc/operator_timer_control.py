import requests
import json

# --- Configuration ---
# !!! IMPORTANT: Replace 'RIG1_IP_ADDRESS' with the actual IP address of Rig 1 !!!
RIG1_IP_ADDRESS = 'RIG1_IP_ADDRESS' # e.g., '192.168.1.101'
RIG_PC_PORT = 5001 # Must match the port used in rig_timer_display.py
TIMER_ENDPOINT_URL = f"http://{RIG1_IP_ADDRESS}:{RIG_PC_PORT}/start_timer"

def set_timer_for_rig1():
    if RIG1_IP_ADDRESS == 'RIG1_IP_ADDRESS':
        print("ERROR: Please update RIG1_IP_ADDRESS in the script with the actual IP of Rig 1.")
        return

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
            break
        except ValueError:
            print("Invalid input. Please enter a number (e.g., 10 or 7.5).")

    payload = {"duration": duration_seconds}

    print(f"\nSending request to {TIMER_ENDPOINT_URL} with payload: {payload}")

    try:
        response = requests.post(TIMER_ENDPOINT_URL, json=payload, timeout=10) # 10 second timeout
        response.raise_for_status() # Raise an exception for HTTP errors (4xx or 5xx)
        
        response_data = response.json()
        if response_data.get("status") == "success":
            print(f"Successfully started timer on Rig 1 for {duration_minutes} minutes.")
            print(f"Message from rig: {response_data.get('message')}")
        else:
            print(f"Rig 1 reported an error: {response_data.get('message', 'Unknown error')}")

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

if __name__ == "__main__":
    print("--- Rig 1 Timer Control ---")
    set_timer_for_rig1()
    input("\nPress Enter to exit...") 