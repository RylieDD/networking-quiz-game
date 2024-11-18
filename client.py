#!/usr/bin/env python3

import struct
import sys
import socket
import selectors
import traceback

import libclient

sel = selectors.DefaultSelector()


def create_request(action):
    if action != "exit":
        return dict(
            type="text/json",
            encoding="utf-8",
            content=dict(action=action),
        )
    else:
        sys.exit(1)


def start_connection(host, port, request):
    addr = (host, port)
    sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    sock.setblocking(False)
    sock.connect_ex(addr)
    events = selectors.EVENT_READ | selectors.EVENT_WRITE
    message = libclient.Message(sel, sock, addr, request)
    sel.register(sock, events, data=message)

# Remove the username addition from the first connection 
if len(sys.argv) != 5:
    print("usage:", sys.argv[0], "-i <host> -p <port>")
    sys.exit(1)

host, port = sys.argv[2], int(sys.argv[4])
action = "connect"
request = create_request(action)
start_connection(host, port, request)

try:
    while True:
        events = sel.select(timeout=1)
        for key, mask in events:
            message = key.data
            try:
                message.process_events(mask)
            except Exception:
                print(
                    "main: error: exception for",
                    f"{message.addr}:\n{traceback.format_exc()}",
                )
                message.close()
        # Check for a socket being monitored to continue.
        if not sel.get_map():
            break
except KeyboardInterrupt:
    print("caught keyboard interrupt, exiting")
finally:
    sel.close()
