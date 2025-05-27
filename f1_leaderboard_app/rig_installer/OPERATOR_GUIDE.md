# F1 Leaderboard - Complete System Deployment Guide

## 🎯 **Quick Deployment Steps**

### **1. Prepare the Complete Installer Package**

Copy the entire `rig_installer` folder to a USB drive or network share. The folder contains:
- `install_complete_rig.bat` - Main installer for complete system
- `rig_timer_client.py` - Timer client (session time limits)
- `rig_listener.py` - Telemetry listener (lap time capture)  
- `app_config.py` - Configuration for track mappings
- `requirements_complete.txt` - All dependencies
- `README_COMPLETE_SYSTEM.md` - Detailed installation guide

### **2. Prerequisites for Each Rig PC**

**Before starting installation:**
1. **Python 3.8+** installed with PATH enabled
2. **F1 Telemetry Repository** downloaded and extracted
   - Download: https://github.com/eSl31RoseBr/f1-24-telemetry
   - Extract to: `C:\f1-24-telemetry-application`
3. **F1 2024 game** installed
4. **Administrator access** for installation

### **3. For Each Rig PC (Complete System):**

**Installation Steps:**
1. Copy `rig_installer` folder to the rig PC desktop
2. Download F1 telemetry repository if not already done
3. Right-click `install_complete_rig.bat` → "Run as administrator"
4. Follow prompts:
   - Choose RIG ID (RIG1, RIG2, RIG3, or RIG4)
   - Set static IP as instructed
   - Confirm F1 telemetry repository location
5. Configure F1 2024 telemetry settings as prompted
6. Test by starting the complete system (desktop shortcut)

**Expected Static IPs:**
- RIG1: 192.168.0.210 (Timer + Telemetry)
- RIG2: 192.168.0.211 (Timer + Telemetry)
- RIG3: 192.168.0.212 (Timer + Telemetry)
- RIG4: 192.168.0.213 (Timer + Telemetry)

### **4. F1 2024 Game Configuration (CRITICAL)**

**On each rig PC, configure F1 2024:**
1. Start F1 2024 game
2. Go to **Settings** → **Telemetry Settings**
3. Set:
   - **UDP Telemetry**: ON
   - **UDP Broadcast Mode**: ON  
   - **UDP Port**: 20777
   - **UDP Send Rate**: 60Hz
   - **UDP Format**: 2024

### **5. System Verification**

**After installation on each rig:**
1. Start complete system (desktop shortcut "Start F1 System [RIG_ID]")
2. Verify **two command windows** open (Timer + Telemetry)
3. Go to admin panel: `http://192.168.0.224:8000/admin`
4. Check:
   - ✅ Rig appears in timer control section
   - ✅ Rig has assigned player name
   - ✅ Test short timer (30 seconds) works
   - ✅ Play F1 and verify lap times appear on leaderboard

## 🚨 **Common Issues & Quick Fixes**

| Problem | Quick Solution |
|---------|---------------|
| "Python not found" | Install Python 3.8+ with PATH, restart PC |
| "F1 telemetry repository not found" | Download from GitHub, extract to C:\f1-24-telemetry-application |
| Timer doesn't appear in admin | Check static IP, firewall, timer client running |
| Lap times not captured | Verify F1 telemetry settings, telemetry listener running |
| ESC doesn't pause F1 | Run as Administrator, use Borderless Windowed mode |
| Network connectivity issues | Check static IPs, ping test, firewall settings |

## 📋 **Complete Installation Checklist**

**For each rig PC:**
- [ ] Python 3.8+ installed with PATH
- [ ] F1 telemetry repository downloaded and extracted
- [ ] Static IP configured correctly
- [ ] Complete system installed (Timer + Telemetry)
- [ ] Desktop shortcut created
- [ ] F1 2024 telemetry settings configured
- [ ] Both system components running
- [ ] Appears in admin panel timer controls
- [ ] Player name assigned in admin panel
- [ ] Test timer functionality works
- [ ] Test lap time capture works
- [ ] ESC key pauses F1 game

## ⚡ **Quick System Test Procedure**

**For each rig after installation:**

1. **Start System**: Double-click "Start F1 System [RIG_ID]" desktop shortcut
2. **Verify Services**: Two command windows should open
   - Timer Client window
   - Telemetry Listener window
3. **Admin Panel Check**: 
   - Go to `http://192.168.0.224:8000/admin`
   - Verify rig appears in timer controls
   - Assign player name if not already done
4. **Timer Test**:
   - Start 30-second timer from admin panel
   - Verify countdown appears on rig screen
   - Verify F1 game pauses when timer expires
5. **Lap Time Test**:
   - Start F1 2024 on rig
   - Complete a lap in Time Trial mode
   - Verify lap time appears on leaderboard
   - Check correct player name is associated

## 🔧 **Troubleshooting Priority**

**If issues occur, check in this order:**

1. **Python Installation**: `python --version` in Command Prompt
2. **Network Connectivity**: `ping 192.168.0.224` from rig PC
3. **Static IP Configuration**: Network adapter settings
4. **F1 Telemetry Repository**: Verify files exist in expected location
5. **F1 Game Telemetry Settings**: UDP settings in game
6. **Windows Firewall**: Allow Python applications
7. **Services Running**: Both command windows open and active

## 📊 **Complete System Architecture**

| Component | Location | Purpose | Port |
|-----------|----------|---------|------|
| **Main Server** | 192.168.0.224 | Admin panel, leaderboard database, web interface | 8000 |
| **RIG1 Timer** | 192.168.0.210 | Session time control | 5001 |
| **RIG1 Telemetry** | 192.168.0.210 | Lap time capture | UDP 20777 |
| **RIG2 Timer** | 192.168.0.211 | Session time control | 5001 |
| **RIG2 Telemetry** | 192.168.0.211 | Lap time capture | UDP 20777 |
| **RIG3 Timer** | 192.168.0.212 | Session time control | 5001 |
| **RIG3 Telemetry** | 192.168.0.212 | Lap time capture | UDP 20777 |
| **RIG4 Timer** | 192.168.0.213 | Session time control | 5001 |
| **RIG4 Telemetry** | 192.168.0.213 | Lap time capture | UDP 20777 |

## ⏱️ **Deployment Timeline**

**Per rig PC (after prerequisites):**
- Installation: 10-15 minutes
- F1 game configuration: 2-3 minutes  
- Network setup: 5-10 minutes
- Testing: 5 minutes
- **Total: ~25-35 minutes per rig**

**For 4 rigs total: ~2-2.5 hours**

---

**Complete System Ready!** All rigs now have both timer control and automatic lap time capture integrated with the central leaderboard system. 