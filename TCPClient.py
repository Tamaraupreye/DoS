#!/usr/bin/env python3

from socket import *
import time

HOST = '192.168.1.192'  # The server's hostname or IP address
PORT = 10000  # The port used by the server
SEND_STRING = 'aaaaaaaaaa'.encode("utf-8")
NUM_PACKETS_TO_SEND = 500000


def send_packet():
    with socket(AF_INET, SOCK_STREAM) as s:
        s.settimeout(3)
        start = time.time()
        s.connect((HOST, PORT))
        s.sendall(SEND_STRING)
        data = s.recv(1024)
    return time.time() - start


def send_multiple_packets(num):
    rtt_arr = []
    t_arr = []
    with socket(AF_INET, SOCK_STREAM) as s:
        s.settimeout(120)
        s.connect((HOST, PORT))
        for i in range(num):
            start = time.time()
            t_arr.append(start)
            s.sendall(SEND_STRING)
            data = s.recv(1024)
            rtt_arr.append(time.time() - start)
    return t_arr, rtt_arr


if __name__ == "__main__":
    for _ in range(NUM_PACKETS_TO_SEND):
        send_packet()

# if __name__ == "__main__":
#     send_multiple_packets(NUM_PACKETS_TO_SEND)
