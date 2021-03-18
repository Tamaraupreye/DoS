#!/usr/bin/env python3
from socket import *

# Create TCP/IP socket
serverSocket = socket(AF_INET, SOCK_STREAM)
serverAddr = ('192.168.1.192', 10000)
print(f"Starting up on {serverAddr[0]} port {serverAddr[1]}")

serverSocket.bind(serverAddr)  # Bind socket to port

serverSocket.listen()  # Listen for incoming connections

while True:
    # Wait for and accept connections
    conn, address = serverSocket.accept()
    print(f"Connected by {address}")
    while True:
        # Receive data from client
        data = conn.recv(1024)
        if not data:
            break
        # The server responds
        conn.sendall(data.upper())
