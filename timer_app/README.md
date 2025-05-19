# F1 Simulator Timer Application

A networked timer application that displays a transparent countdown timer on simulator rigs and allows remote control from an operator PC.

## Overview

This application consists of:

1. **Timer Server** - Runs on each simulator rig PC
2. **Timer Control** - Runs on the operator's PC to control timers remotely
3. **Timer Display** - Transparent overlay showing the countdown

## Setup

### On Each Simulator Rig PC:

1. Copy the `timer_app` folder to the rig PC
2. Run `start_timer_server.bat` to start the timer server
3. The server will listen for commands from the operator's PC

### On the Operator's PC:

1. Copy the `timer_app` folder to the operator's PC
2. Edit `timer_config.ini` to set the correct IP addresses for your rig PCs
3. Run `start_timer_control.bat` to open the control interface
4. Use the interface to start/stop timers on any connected rig

## Requirements

- Python 3.6 or higher on all PCs
- Network connectivity between the operator PC and rig PCs
- Dependencies (automatically installed):
  - pyautogui

## Configuration

The `timer_config.ini` file contains the network configuration:

```ini
[RIG1]
ip = 192.168.1.101  # Change to the actual IP of Rig 1
port = 5678
name = Rig 1
```

Update the IP addresses to match your actual network setup before use.

## How it Works

1. The **Timer Server** on each rig listens for commands over the network
2. The **Timer Control** interface on the operator's PC sends commands to control timers
3. When a timer is started, the rig displays a transparent countdown in the specified corner
4. When the timer expires, it sends an ESC key to pause the game
5. The timer can be stopped at any time from the operator's PC

## For Saturday's Event

For your Saturday event with only Rig 1:

1. Start the **Timer Server** on Rig 1 using `start_timer_server.bat`
2. On the operator's PC, update `timer_config.ini` with Rig 1's correct IP address
3. Use the **Timer Control** interface to set and start timers for Rig 1
