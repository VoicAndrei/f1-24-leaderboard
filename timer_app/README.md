# F1 Simulator Timer Application

A simple application that displays a transparent countdown timer and sends an ESC key when the timer expires to pause the F1 2024 game.

## Requirements

Before running the application, you need to install the required dependencies:

```bash
pip install pyautogui
```

Tkinter should be included with your Python installation.

## Usage

### Graphical User Interface (Recommended)

The easiest way to use the timer is with the GUI launcher:

1. Double-click the `start_timer.bat` file
   - OR run `python timer_launcher.py` from the command line
2. Select the rig number, timer duration, and position
3. Click "Start Timer"

### Command-line Usage (Advanced)

Run the timer directly with custom settings:

```bash
python timer.py --rig 1 --minutes 5 --position top-right
```

#### Command-line arguments

- `--rig`: The rig number (default: 1)
- `--minutes`: Timer duration in minutes (default: 10)
- `--position`: Position of the timer on screen (default: top-right)
  - Options: top-right, top-left, bottom-right, bottom-left

## How it works

1. The script creates a transparent overlay window in the specified corner of the screen
2. The overlay displays a countdown timer for the specified rig
3. When the timer expires, it sends an ESC key to pause the game
4. The overlay will close 5 seconds after the timer expires

## For future integration

To integrate this with the admin interface after the event, consider:

1. Adding a timer control section to the admin panel
2. Using WebSocket to communicate between the admin interface and the timer application
3. Creating a mechanism to start/stop timers remotely 