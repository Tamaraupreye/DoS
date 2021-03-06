#!/usr/bin/env python3

import selectors
import types
import socket
import argparse
import time

HOST = '192.168.1.192'  # The server's hostname or IP address
PORT = 10000  # The port used by the server
SEND_STRING = 'aaaaaaaaaa'.encode("utf-8")


def start_connections(host, port, num_conns, sel):
    server_addr = (host, port)
    for i in range(0, num_conns):
        connid = i + 1
        print('starting connection', connid, 'to', server_addr)
        sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        sock.setblocking(False)
        sock.connect_ex(server_addr)
        events = selectors.EVENT_READ | selectors.EVENT_WRITE
        data = types.SimpleNamespace(connid=connid,
                                     msg_total=len(SEND_STRING),
                                     recv_total=0,
                                     messages=[SEND_STRING],
                                     outb=b'')
        sel.register(sock, events, data=data)


def service_connection(key, mask, sel):
    sock = key.fileobj
    data = key.data
    if mask & selectors.EVENT_READ:
        recv_data = sock.recv(1024)  # Should be ready to read
        if recv_data:
            print('received', repr(recv_data), 'from connection', data.connid)
            data.recv_total += len(recv_data)
        if not recv_data or data.recv_total == data.msg_total:
            print('closing connection', data.connid)
            sel.unregister(sock)
            sock.close()
    if mask & selectors.EVENT_WRITE:
        if not data.outb and data.messages:
            data.outb = data.messages.pop(0)
        if data.outb:
            print('sending', repr(data.outb), 'to connection', data.connid)
            sent = sock.send(data.outb)  # Should be ready to write
            data.outb = data.outb[sent:]


def service_connection_ex():
    sel = selectors.DefaultSelector()
    start_connections(HOST, PORT, 1, sel)
    while True:
        events = sel.select(timeout=1)
        if events:
            for key, mask in events:
                service_connection(key, mask, sel)
        # Check for a socket being monitored to continue.
        if not sel.get_map():
            break
    sel.close()


if __name__ == "__main__":
    for tr in range(5000):
        print(f"\n{tr}\n")
        service_connection_ex()
