# F1 Leaderboard - Complete System Installation Guide

## 📋 **Complete System Overview**

This installer sets up the **complete F1 Leaderboard System** on each simulator rig PC, including:

### **1. Timer Client**
- Displays countdown timers on rig screens
- Automatically pauses F1 game when time expires (ESC key)
- Controlled remotely from operator admin panel

### **2. Telemetry Listener** 
- Captures lap times from F1 2024 game
- Sends lap data to central leaderboard database
- Associates lap times with assigned player names

## 🖥️ **System Requirements**

- **Windows 10/11**
- **Python 3.8+** 
- **F1 2024 game** installed and configured
- **Internet connection** (for downloading dependencies)
- **Network connection** to operator PC
- **F1 Telemetry Repository** (downloaded separately)

## 📦 **Installation Package Contents**

- `install_complete_rig.bat` - Main installer script
- `rig_timer_client.py` - Timer client application
- `rig_listener.py` - Telemetry listener for lap times
- `app_config.py` - Configuration for track mappings
- `requirements_complete.txt` - Python dependencies
- `README_COMPLETE_SYSTEM.md` - This guide

## 🚀 **Installation Steps**

### **Step 1: Install Python (if needed)**

1. Download Python 3.8+ from https://www.python.org/downloads/
2. Run the installer
3. **IMPORTANT**: Check "Add Python to PATH" during installation
4. Complete installation and restart computer if prompted

### **Step 2: Download F1 Telemetry Repository**

**This is required for lap time capture!**

1. Go to https://github.com/eSl31RoseBr/f1-24-telemetry
2. Click "Code" → "Download ZIP"
3. Extract the ZIP file
4. Move the folder to one of these locations:
   - `C:\f1-24-telemetry-application` (recommended)
   - `C:\F1Telemetry\f1-24-telemetry-application`
   - `Desktop\f1-24-telemetry-application`

### **Step 3: Run the Complete System Installer**

1. Copy the installer folder to the rig PC
2. **Right-click** `install_complete_rig.bat`
3. Select **"Run as administrator"**
4. Follow the installation prompts:
   - Choose RIG ID (RIG1, RIG2, RIG3, or RIG4)
   - Set the static IP address as instructed
   - Configure F1 2024 telemetry settings

### **Step 4: Configure Static IP Address**

The installer will tell you which IP to use:

1. Open **Windows Settings** (Windows key + I)
2. Go to **Network & Internet**
3. Click **"Change adapter options"**
4. Right-click your network connection → **Properties**
5. Select **"Internet Protocol Version 4 (TCP/IPv4)"** → **Properties**
6. Select **"Use the following IP address"**
7. Enter the IP shown by installer:
   - **RIG1**: 192.168.0.210
   - **RIG2**: 192.168.0.211
   - **RIG3**: 192.168.0.212
   - **RIG4**: 192.168.0.213
8. Set:
   - **Subnet mask**: 255.255.255.0
   - **Default gateway**: 192.168.0.1
   - **DNS**: 8.8.8.8
9. Click **OK** and restart network connection

### **Step 5: Configure F1 2024 Telemetry**

**This step is CRITICAL for lap time capture:**

1. Start **F1 2024** game
2. Go to **Settings** → **Telemetry Settings**
3. Configure these settings:
   - **UDP Telemetry**: **ON**
   - **UDP Broadcast Mode**: **ON**
   - **UDP Port**: **20777**
   - **UDP Send Rate**: **60Hz** (recommended)
   - **UDP Format**: **2024** (should be default)

### **Step 6: Start the Complete System**

1. Double-click **"Start F1 System [RIG_ID]"** on desktop
2. **Two command windows** will open:
   - Timer Client window
   - Telemetry Listener window
3. **Keep both windows open** (you can minimize them)
4. System is now ready!

## 🎮 **System Usage**

### **For Operators:**
- Access admin panel: `http://192.168.0.224:8000/admin`
- Control timers for each rig
- Assign player names to rigs
- View real-time leaderboard

### **For Players:**
- Play F1 2024 normally
- Lap times automatically appear on leaderboard
- Timer countdown appears when operator starts session timer
- Game pauses automatically when timer expires

## 🔧 **Troubleshooting**

### **Timer Not Appearing in Admin Panel**
1. Verify static IP is set correctly
2. Check timer client is running (command window open)
3. Allow Python through Windows Firewall
4. Test network: `ping 192.168.0.224`

### **Lap Times Not Appearing on Leaderboard**
1. Verify F1 2024 telemetry settings are correct
2. Check telemetry listener is running (second command window)
3. Ensure F1 telemetry repository is installed correctly
4. Verify rig is assigned a player name in admin panel
5. Check that you're completing full laps in-game

### **ESC Key Not Working in F1 Game**
1. Run timer client as Administrator
2. Change F1 game from Fullscreen to Borderless Windowed
3. Ensure F1 game is the active window when timer expires
4. Try clicking in the game window before timer expires

### **Network Connection Issues**
1. Verify all PCs are on the same network
2. Check Windows Firewall on both rig and operator PCs
3. Test connectivity: `ping 192.168.0.224` from rig PC
4. Ensure operator PC is running at 192.168.0.224

### **Python or Package Installation Issues**
1. Uninstall and reinstall Python
2. Ensure "Add Python to PATH" was checked
3. Restart computer after Python installation
4. Run Command Prompt as Admin and test: `python --version`
5. Manually install packages: `pip install flask pydirectinput requests`

### **F1 Telemetry Repository Issues**
1. Re-download from https://github.com/eSl31RoseBr/f1-24-telemetry
2. Extract to `C:\f1-24-telemetry-application`
3. Verify the folder contains Python files (.py files)
4. Update `app_config.py` if using different location

## 📊 **Network Configuration Summary**

| Device | Static IP | Purpose |
|--------|-----------|---------|
| Operator PC | 192.168.0.224 | Main server, admin panel, leaderboard display |
| RIG1 PC | 192.168.0.210 | Timer client + Telemetry listener |
| RIG2 PC | 192.168.0.211 | Timer client + Telemetry listener |
| RIG3 PC | 192.168.0.212 | Timer client + Telemetry listener |
| RIG4 PC | 192.168.0.213 | Timer client + Telemetry listener |

## 📁 **File Locations After Installation**

- **Installation folder**: `C:\F1LeaderboardRig\`
- **Desktop shortcut**: `Start F1 System [RIG_ID].bat`
- **Log files**: Created in installation folder during operation

## 🔄 **Starting/Stopping the System**

### **To Start:**
- Double-click desktop shortcut: `Start F1 System [RIG_ID]`

### **To Stop:**
- Close both command windows (Timer Client and Telemetry Listener)
- Or press Ctrl+C in each window

### **To Restart:**
- Stop the system first, then start again using desktop shortcut

## 🆘 **Support & Contact**

If you encounter issues:

1. **Check this troubleshooting guide first**
2. **Verify all installation steps were completed**
3. **Check Windows Event Viewer for detailed errors**
4. **Test individual components** (timer vs telemetry)
5. **Verify F1 game telemetry configuration**

---

**Installation Complete!** Your rig is now ready to participate in the complete F1 Leaderboard system with both timer control and automatic lap time capture. 