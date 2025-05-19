#!/usr/bin/env python3
"""
Simple port test server to verify connection
"""

import socket
import sys

def start_test_server(port=5678):
    """Start a simple test server on the specified port."""
    
    # Create a socket
    server = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    server.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
    
    try:
        # Bind to all interfaces on the specified port
        server.bind(('0.0.0.0', port))
        server.listen(1)
        
        print(f"Test server started on port {port}")
        print("Waiting for a connection...")
        
        # Accept one connection and then exit
        client_sock, address = server.accept()
        print(f"Connection received from {address[0]}:{address[1]}")
        
        # Send a test message
        client_sock.send("Connection successful!".encode('utf-8'))
        
        # Close the connection
        client_sock.close()
        print("Test successful! Port is accessible.")
    
    except Exception as e:
        print(f"Error: {e}")
    
    finally:
        server.close()
        print("Server closed")

if __name__ == "__main__":
    # Get port from command line if provided
    port = 5678
    if len(sys.argv) > 1:
        try:
            port = int(sys.argv[1])
        except ValueError:
            print(f"Invalid port: {sys.argv[1]}")
            sys.exit(1)
    
    # Start the test server
    start_test_server(port) 