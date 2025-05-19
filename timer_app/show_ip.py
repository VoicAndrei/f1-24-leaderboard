#!/usr/bin/env python3
"""
IP Address Display Utility

Shows the IP addresses of the current machine to help with timer configuration.
"""

import socket
import tkinter as tk
from tkinter import ttk
import platform
import subprocess

def get_ip_addresses():
    """Get all IP addresses for this machine."""
    hostname = socket.gethostname()
    ip_list = []
    
    # Get the primary IP address
    try:
        # This gets the IP address used to connect to external networks
        s = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
        # Doesn't need to be reachable
        s.connect(('8.8.8.8', 1))
        primary_ip = s.getsockname()[0]
        s.close()
        ip_list.append(("Primary IP (recommended)", primary_ip))
    except:
        pass
    
    # Get all IP addresses
    try:
        # Get all addresses associated with the hostname
        host_info = socket.getaddrinfo(hostname, None)
        for h in host_info:
            if h[0] == socket.AF_INET:  # Only IPv4
                ip = h[4][0]
                if ip not in [x[1] for x in ip_list] and not ip.startswith('127.'):
                    ip_list.append(("Additional IP", ip))
    except:
        pass
    
    # If no IPs found, add localhost
    if not ip_list:
        ip_list.append(("Localhost", "127.0.0.1"))
    
    return hostname, ip_list

def copy_to_clipboard(text):
    """Copy text to clipboard."""
    root.clipboard_clear()
    root.clipboard_append(text)
    root.update()

def create_gui():
    global root
    root = tk.Tk()
    root.title("F1 Timer IP Configuration Helper")
    root.geometry("450x350")
    
    main_frame = ttk.Frame(root, padding="20")
    main_frame.pack(fill=tk.BOTH, expand=True)
    
    # Title
    title_label = ttk.Label(
        main_frame,
        text="F1 Timer IP Configuration Helper",
        font=('Arial', 14, 'bold')
    )
    title_label.pack(pady=(0, 15))
    
    # Get hostname and IPs
    hostname, ip_addresses = get_ip_addresses()
    
    # Hostname display
    hostname_frame = ttk.Frame(main_frame)
    hostname_frame.pack(fill=tk.X, pady=5)
    
    ttk.Label(hostname_frame, text="Computer Name:", font=('Arial', 10, 'bold')).pack(side=tk.LEFT)
    ttk.Label(hostname_frame, text=hostname).pack(side=tk.RIGHT)
    
    # IP addresses display
    ip_frame = ttk.LabelFrame(main_frame, text="Available IP Addresses")
    ip_frame.pack(fill=tk.BOTH, expand=True, pady=10)
    
    # Instructions
    instruction_text = (
        "Use one of these IP addresses in the timer_config.ini file.\n"
        "The Primary IP is usually the best choice."
    )
    ttk.Label(ip_frame, text=instruction_text, wraplength=400).pack(pady=10)
    
    # IP list
    for i, (ip_type, ip) in enumerate(ip_addresses):
        ip_row = ttk.Frame(ip_frame)
        ip_row.pack(fill=tk.X, pady=5, padx=10)
        
        ttk.Label(ip_row, text=f"{ip_type}:", width=20).pack(side=tk.LEFT)
        ttk.Label(ip_row, text=ip, width=15).pack(side=tk.LEFT, padx=5)
        
        copy_btn = ttk.Button(
            ip_row, 
            text="Copy",
            command=lambda addr=ip: copy_to_clipboard(addr)
        )
        copy_btn.pack(side=tk.RIGHT)
    
    # Configuration instructions
    config_frame = ttk.LabelFrame(main_frame, text="Configuration Instructions")
    config_frame.pack(fill=tk.X, pady=10)
    
    config_text = (
        "1. Run this utility on BOTH the rig PC and operator PC\n"
        "2. Note the Primary IP address of the rig PC\n"
        "3. On the operator PC, edit timer_config.ini and set this IP"
    )
    ttk.Label(config_frame, text=config_text, justify=tk.LEFT, wraplength=400).pack(pady=10, padx=10)
    
    # Close button
    ttk.Button(main_frame, text="Close", command=root.destroy).pack(pady=10)
    
    root.mainloop()

if __name__ == "__main__":
    create_gui() 