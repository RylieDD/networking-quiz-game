#!/usr/bin/env python3

import asyncio
import sys
import socket
import selectors
import time
import traceback
import libserver
import ssl

sel = selectors.DefaultSelector()
connections = {}
messages = {}
global quiz_state
ready_event = asyncio.Event()

#Application of TLS using the provided cert.pem and key.pem
def create_tls_context(certfile="cert.pem", keyfile="key.pem"):
    context = ssl.create_default_context(ssl.Purpose.CLIENT_AUTH)
    context.load_cert_chain(certfile=certfile, keyfile=keyfile)
    context.options |= ssl.OP_NO_SSLv2 | ssl.OP_NO_SSLv3 
    context.options |= ssl.OP_NO_TLSv1 | ssl.OP_NO_TLSv1_1 
    return context

#Starts the client connection to the server
def accept_wrapper(sock):
    conn, addr = sock.accept() 
    conn.setblocking(False)
    message = libserver.Message(sel, conn, addr, handler=handle_action)
    length = len(connections)
    if len(connections) <= 2:
        connections[addr] = {'username': None, 'started': False, 'connected': False, 'responded': False}
        messages[addr] = {'message': message, 'mask': None}
        sel.register(conn, selectors.EVENT_READ, data=message)
    else:
        print(f"Too many players for the quiz game, rejecting connection from {addr}.")
        conn.close()
#Starts the socket and applies the TLS context
if len(sys.argv) != 3:
    print (len(sys.argv))
    print("usage:", sys.argv[0], "-p <port>")
    sys.exit(1)
tls_context = create_tls_context()
host, port = "0.0.0.0", int(sys.argv[2])
lsock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
lsock.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
lsock.bind((host, port))
lsock.listen()
lsock.setblocking(False)
tls_sock = tls_context.wrap_socket(lsock, server_side=True)
sel.register(tls_sock, selectors.EVENT_READ, data=None)

#Handles actions from the clients that need to be synchronized
async def handle_action(addr, action, answer=None):
    global quiz_state
    print(f"Received action '{action}' from {addr}")
    if action == "connect":
        if connections[addr]["connected"]:
            print(f"Client {addr} already connected. Ignoring duplicate 'connect'.")
            return

        connections[addr]["connected"] = True
        message = messages[addr]["message"]
        await message.send_response(
            {"result": "Connected to the quiz game."}
        )
        return
    if action == "start":
        print(f"Handling 'start' from {addr}")
        connections[addr]["started"] = True
        quiz_state = {
            "current_question": None,
            "num_questions_asked": 0,
            "max_questions": 10,
            "scores": {}
        }

        if len(connections) == 1 or all(conn["started"] for conn in connections.values()):
            ready_event.set()
            print("All clients are ready, starting the quiz.")
            tasks = [
                messages[client_addr]["message"].send_response(
                    {
                        "action": "start",
                        "result": "Quiz is starting... waiting for questions.",
                    }
                )
                for client_addr in connections
            ]
            await asyncio.gather(*tasks)
            print("Initial quiz message sent to all clients.")
            time.sleep(0.5)
            await broadcast_question()
        else:
            print(f"Client {addr} waiting for others.")
            message = messages[addr]["message"]
            await message.send_response(
                {
                "action": "info",
                "result": "Received start request. Waiting for other players...",
                }
            )
    elif action.lower() == "answer":
        print(f"Received answer '{answer}' from {addr}.")
        await handle_answer(addr, answer)
    elif action == "exit":
        print(f"Client {addr} requested to exit.")
        handle_disconnection(addr)
        message = messages[addr]["message"]
        await message.send_response(
            {"result": "Goodbye! Closing connection..."}
        )
        message.close()
        del messages[addr]
    else:
        message = messages[addr]["message"]
        await message.send_response({"result": f'Error: invalid action "{action}".'})

#Where the quiz questions are created and sent
async def broadcast_question():
    global quiz_state

    if quiz_state["num_questions_asked"] > quiz_state["max_questions"]:
        print("Max questions reached. Ending quiz.")
        end_quiz()
        return

    else:
        print("Generating quiz question.")
        example_message = next(iter(messages.values()))["message"]
        question = example_message.quiz_questions()
        quiz_state["current_question"] = question
        quiz_state["num_questions_asked"] += 1

    tasks = []
    for addr in connections:
        message = messages[addr]["message"]
        content = {
            "action": "question",
            "result": "Here is your question:",
            "question": question["question"],
            "options": question["options"],
            "input": "Answer the question by entering a, b, c, or d: "
        }
        print(f"Sending question to {addr}")
        tasks.append(message.send_response(content))
        message.jsonheader = None
        message._jsonheader_len = None
    if tasks:
        time.sleep(0.1)
        await asyncio.gather(*tasks)
        print("Question sent to all clients.")

#Where the clients answers are checked and the response message is created and sent
async def handle_answer(addr, answer):
    global quiz_state
    if not quiz_state["current_question"]:
        return 
    correct = (
        answer.upper() == quiz_state["current_question"]["answer"]
    )
    if correct:
        quiz_state["scores"][addr] = quiz_state["scores"].get(addr, 0) + 1
        response = {"result": "Correct answer!"}
    else:
        response = {
            "result": f"Wrong answer!"
        }
    connections[addr]["responded"] = True
    message = messages[addr]["message"]
    await message.send_response(response)

    if all(conn["responded"] for conn in connections.values()):
        reset_responses()
        if quiz_state["num_questions_asked"] < quiz_state["max_questions"]:
            await broadcast_question()
        else:
            await end_quiz()
    
#Resets the responded flag to allow client answers to be handled
def reset_responses():
    for conn in connections.values():
        conn["responded"] = False

#Where the end of quiz logic is handled
async def end_quiz():
    global quiz_state
    scores = quiz_state["scores"]
    if scores:
        highest_score = max(scores.values())
        winners = [addr for addr, score in scores.items() if score == highest_score]
        winner_message = f"Winner(s): {', '.join([connections[w]['username'] for w in winners])} with {highest_score} points."
    else:
        winner_message = "No winners. Better luck next time!"

    tasks = []
    for addr in connections:
        message = messages[addr]["message"]
        tasks.append(
            message.send_response({"action": "end", "result": winner_message, "input": "Enter start to restart the game or exit to exit the quiz game:"})
        )
    quiz_state = {
    "current_question": None,
    "num_questions_asked": 0,
    "max_questions": 10,
    "scores": {}
    } 
    for addr in connections:
        messages[addr]["message"].used_questions = []
    message.jsonheader = None
    message._jsonheader_len = None
    await asyncio.gather(*tasks)

#Where disconnection by clients is handled
def handle_disconnection(addr):
    if addr in connections:
        username = connections[addr].get("username", "Unknown")
        print(f"Client {username} at {addr} disconnected.")
        del connections[addr]
    if addr in messages:
        del messages[addr]
#Main logic loop of the server
async def main():
    try:
        while True:
            events = sel.select(timeout=None)
            for key, mask in events:
                if key.data is None:
                    accept_wrapper(key.fileobj)
                else:
                    message = key.data
                    addr = message.addr
                    try:
                        if addr in connections:
                            if connections[addr]['username'] is None:
                                connections[addr]['username'] = message.username
                            if len(connections) > 1:
                                if all(conn['started'] for conn in connections.values()):
                                    messages[addr]['message'] = message
                                    messages[addr]['mask'] = mask
                                    if all(conn_data["started"] for conn_data in connections.values()):
                                        await message.process_events(mask)
                                elif all(conn['responded'] for conn in connections.values()):
                                    messages[addr]['message'] = message
                                    messages[addr]['mask'] = mask
                                    if all(conn_data["responded"] for conn_data in connections.values()):
                                        await message.process_events(mask)
                                else:
                                    await message.process_events(mask)
                            else:
                                await message.process_events(mask)
                        else:
                            print(f"Client {addr} not found in connections.")
                    except RuntimeError as e:
                        print(f"Runtime error for {addr}: {e}")
                        handle_disconnection(addr)
                        message.close()
                    except Exception as e:
                        print(f"Unhandled error for {addr}: {traceback.format_exc()}")
                        handle_disconnection(addr)
                        message.close()
    except KeyboardInterrupt:
        print("caught keyboard interrupt, exiting")
    finally:
        sel.close()
        tls_sock.close()
if __name__ == "__main__":
    loop = asyncio.get_event_loop()
    loop.run_until_complete(main())
