
#!/usr/bin/env python3

import asyncio
import sys
import socket
import selectors
import traceback

import libserver

sel = selectors.DefaultSelector()
connections = []

def accept_wrapper(sock):
    conn, addr = sock.accept()  # Should be ready to read
    conn.setblocking(False)
    message = libserver.Message(sel, conn, addr)
    connections.append(addr)
    sel.register(conn, selectors.EVENT_READ, data=message)

if len(sys.argv) != 3:
    print (len(sys.argv))
    print("usage:", sys.argv[0], "-p <port>")
    sys.exit(1)

host, port = "0.0.0.0", int(sys.argv[2])
lsock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
# Avoid bind() exception: OSError: [Errno 48] Address already in use
lsock.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
lsock.bind((host, port))
lsock.listen()
# print("listening on", (host, port))
lsock.setblocking(False)
sel.register(lsock, selectors.EVENT_READ, data=None)

try:
    while True:
        events = sel.select(timeout=None)
        for key, mask in events:
            if key.data is None:
                accept_wrapper(key.fileobj)
            else:
                message = key.data
                try:
                    message.process_events(mask)
                except Exception:
                    print(
                        "main: error: exception for",
                        f"{message.addr}:\n{traceback.format_exc()}",
                    )
                    message.close()
except KeyboardInterrupt:
    print("caught keyboard interrupt, exiting")
finally:
    sel.close()



'''
async def process_events(message, mask):
    if message.process_events(mask) is not None:
        await message.process_events(mask)
        data = message.request
        print("Server data: ", data)
        if data == "start":
            await question_send(message, connections)

async def question_send(message, clients):
    tasks = [asyncio.create_task(message.create_response("question")) for addr in clients]
    await asyncio.gather(*tasks)

#async def event_loop():
while True:
    events = sel.select(timeout=None)
    tasks = []
    for key, mask in events:
        if key.data is None:
            accept_wrapper(key.fileobj)
        else:
            message = key.data
            #tasks.append(asyncio.create_task(process_events(message, mask)))
    # Wait for all tasks to complete concurrently
    #await asyncio.gather(*tasks)
    # Handle errors after gathering
    #for task in tasks:
    #    try:
     #       await task
        except Exception:
            print(
                "main: error: exception for",
                f"{message.addr}:\n{traceback.format_exc()}",
            )
            message.close()

try:
    asyncio.run(event_loop())
except KeyboardInterrupt:
    print("caught keyboard interrupt, exiting")
finally:
    sel.close()
    '''
