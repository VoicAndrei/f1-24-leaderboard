# F1 Leaderboard - Network Setup Guide

## 🌐 Two-Profile Network System

The F1 Leaderboard application supports **two predefined network configurations** to make it easy to move between different environments:

### **Profile 1: SHOP (Default)**
- **Network Range:** `192.168.0.x`
- **Reception Laptop:** `192.168.0.224`
- **Gateway:** `192.168.0.1`
- **Rig IPs:**
  - RIG1: `192.168.0.210`
  - RIG2: `192.168.0.211`
  - RIG3: `192.168.0.212`
  - RIG4: `192.168.0.213`

### **Profile 2: MOBILE**  
- **Network Range:** `192.168.1.x`
- **Reception Laptop:** `192.168.1.224`
- **Gateway:** `192.168.1.1`
- **Rig IPs:**
  - RIG1: `192.168.1.210`
  - RIG2: `192.168.1.211`
  - RIG3: `192.168.1.212`
  - RIG4: `192.168.1.213`

---

## 🔧 Quick Setup Commands

### **Check Current Configuration**
```bash
python scripts/network_config_helper.py --show-current
```

### **Switch Between Profiles**
```bash
# Switch to shop/home network
python scripts/network_config_helper.py --set-profile SHOP

# Switch to mobile/event network  
python scripts/network_config_helper.py --set-profile MOBILE
```

### **Generate Rig Configuration Files**
```bash
# Generate batch file for RIG1 (current profile)
python scripts/network_config_helper.py --generate-batch RIG1
```

---

## 📋 Complete Setup Process

### **For Shop/Home Setup:**

1. **Set Profile to SHOP:**
   ```bash
   python scripts/network_config_helper.py --set-profile SHOP
   ```

2. **Configure Reception Laptop:**
   - Static IP: `192.168.0.224`
   - Subnet: `255.255.255.0`
   - Gateway: `192.168.0.1`

3. **Configure Each Rig PC:**
   ```bash
   # Generate config files for each rig
   python scripts/network_config_helper.py --generate-batch RIG1
   python scripts/network_config_helper.py --generate-batch RIG2
   python scripts/network_config_helper.py --generate-batch RIG3
   ```
   
4. **Run the batch files as administrator on each rig PC**

5. **Restart the backend server**

### **For Mobile/Event Setup:**

1. **Set Profile to MOBILE:**
   ```bash
   python scripts/network_config_helper.py --set-profile MOBILE
   ```

2. **Configure your portable router to use `192.168.1.x` network**

3. **Follow steps 2-5 from above (using the new IP ranges)**

---

## 🚀 Event Day Workflow

### **Going to an Event:**

1. **Before leaving:** Switch to MOBILE profile and generate new batch files
2. **At the event:** Connect all equipment to your portable router
3. **Run the batch files** on each rig PC to update their IPs
4. **Start the backend** - everything should work on the new network

### **Back at Shop:**

1. **Switch back to SHOP profile**
2. **Connect to shop network** 
3. **Run the SHOP batch files** on each rig PC
4. **Restart backend** - back to normal operation

---

## 💡 Pro Tips

- **Always use the same router for events** to avoid network configuration changes
- **Generate batch files before traveling** to avoid dependency issues
- **Test the mobile configuration** at the shop before traveling
- **Keep backup batch files** for both profiles on a USB drive
- **Only change the profile setting on the reception laptop** - rig PCs just need IP updates

---

## 🔍 Troubleshooting

### **"Can't connect to rigs"**
1. Check that profile matches the actual network you're using
2. Verify rig PCs have correct static IP addresses
3. Test network connectivity: `ping 192.168.X.210` (where X is 0 or 1)

### **"Backend won't start after profile change"**
1. Make sure you restarted the backend server after switching profiles
2. Check that reception laptop has the correct IP for the current profile

### **"Batch file doesn't work"**
1. Run batch file as administrator
2. Make sure you generated it with the correct profile active
3. Check that the network adapter is connected

---

## 📞 Quick Reference

| Task | Command |
|------|---------|
| Check current config | `--show-current` |
| See all profiles | `--show-all` |
| Switch to shop | `--set-profile SHOP` |
| Switch to mobile | `--set-profile MOBILE` |
| Generate rig config | `--generate-batch RIG1` |

**Remember:** Always restart the backend server after switching profiles! 