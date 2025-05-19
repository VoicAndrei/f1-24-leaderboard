#!/usr/bin/env python3
"""
Simple port test client to verify connection
"""

import socket
import sys

def test_connection(host, port=5678, timeout=5):
    """Test connection to a server at the specified host and port."""
    
    print(f"Attempting to connect to {host}:{port}...")
    
    try:
        # Create a socket
        client_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        client_socket.settimeout(timeout)
        
        # Try to connect
        client_socket.connect((host, port))
        
        # If we get here, connection was successful
        print(f"Successfully connected to {host}:{port}")
        
        # Try to receive a response
        data = client_socket.recv(1024).decode('utf-8')
        print(f"Received: {data}")
        
        # Close the connection
        client_socket.close()
        
        return True
    
    except socket.timeout:
        print(f"Connection timed out after {timeout} seconds")
        return False
    
    except ConnectionRefusedError:
        print(f"Connection refused. Make sure the server is running on {host}:{port}")
        return False
    
    except Exception as e:
        print(f"Error: {e}")
        return False

if __name__ == "__main__":
    # Get host and port from command line
    if len(sys.argv) < 2:
        print("Usage: python port_test_client.py HOST [PORT]")
        sys.exit(1)
    
    host = sys.argv[1]
    port = 5678
    
    if len(sys.argv) > 2:
        try:
            port = int(sys.argv[2])
        except ValueError:
            print(f"Invalid port: {sys.argv[2]}")
            sys.exit(1)
    
    # Test the connection
    success = test_connection(host, port)
    
    if success:
        print("\nConnection test PASSED!")
        print("The port is accessible from this machine.")
    else:
        print("\nConnection test FAILED!")
        print("Possible issues:")
        print("1. The server is not running")
        print("2. A firewall is blocking the connection")
        print("3. The IP address or port number is incorrect")
        print("4. Network connectivity problems")
    
    # Wait for user input before closing
    input("\nPress Enter to exit...")
    sys.exit(0 if success else 1) 