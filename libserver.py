
import asyncio
import random
import sys
import selectors
import json
import io
import struct
import time
import logging



class Message:
    def __init__(self, selector, sock, addr):
        self.selector = selector
        self.sock = sock
        self.addr = addr
        self._recv_buffer = b""
        self._send_buffer = b""
        self._jsonheader_len = None
        self.jsonheader = None
        self.request = None
        self.response_created = False
        self.username = None
        self.connections = {}
        self.first_request = True
        self._join_req = False
        self.num_ques = 0
        self.question = None
        
        #Setup logging
        self.logger = logging.getLogger(self.__class__.__name__)
        self.logger.setLevel(logging.ERROR)
        formatter = logging.Formatter('%(asctime)s - %(levelname)s - %(message)s')
        handler = logging.FileHandler('Server_Error.log')
        handler.setFormatter(formatter)
        self.logger.addHandler(handler)

    def _set_selector_events_mask(self, mode):
        """Set selector to listen for events: mode is 'r', 'w', or 'rw'."""
        if mode == "r":
            events = selectors.EVENT_READ
        elif mode == "w":
            events = selectors.EVENT_WRITE
        elif mode == "rw":
            events = selectors.EVENT_READ | selectors.EVENT_WRITE
        else:
            self.logger.error(f"Invalid events mask mode {repr(mode)} for {self.addr}.")
            raise ValueError(f"Invalid events mask mode {repr(mode)}.")
        self.selector.modify(self.sock, events, data=self)

    def _read(self):
        try:
            # Should be ready to read
            data = self.sock.recv(4096)
        except BlockingIOError:
            # Resource temporarily unavailable (errno EWOULDBLOCK)
            pass
        else:
            if data:
                self._recv_buffer = b"" 
                self._recv_buffer += data
            else:
                self.logger.error(f"Error: Peer closed connection for {self.addr}.")
                raise RuntimeError("Peer closed.")

    def _write(self):
        if self._send_buffer:
            try:
                # Should be ready to write
                sent = self.sock.send(self._send_buffer)
            except BlockingIOError:
                # Resource temporarily unavailable (errno EWOULDBLOCK)
                pass
            else:
                self._send_buffer = self._send_buffer[sent:]

                # Close when the buffer is drained. The response has been sent.
                # if sent and not self._send_buffer:
                    # self.close()
        self._send_buffer = b""

    def _json_encode(self, obj, encoding):
        return json.dumps(obj, ensure_ascii=False).encode(encoding)

    def _json_decode(self, json_bytes, encoding):
        tiow = io.TextIOWrapper(
            io.BytesIO(json_bytes), encoding=encoding, newline=""
        )
        obj = json.load(tiow)
        tiow.close()
        return obj

    def _create_message(
        self, *, content_bytes, content_type, content_encoding
    ):
        jsonheader = {
            "byteorder": sys.byteorder,
            "content-type": content_type,
            "content-encoding": content_encoding,
            "content-length": len(content_bytes),
        }
        jsonheader_bytes = self._json_encode(jsonheader, "utf-8")
        message_hdr = struct.pack(">H", len(jsonheader_bytes))
        message = message_hdr + jsonheader_bytes + content_bytes
        return message

    #Add additional arguments from project note
    def user_action(self, action):
        userAction = {
            "help": "Please enter the following format: app-client.py <action>, where action is join or rules",
            "rules": "\U0001F56D Choose the correct answer (A, B, C, or D) to the question on screen! The first to answer correctly gets 1 point. \U0001F56D",
            "-h" : "Please enter the following format: app-client.py <host> <port> <username> to connect",
            "-i" : "Needs to provide the server IP",
            "-p" : "Needs to provide the server port",
            "-n" : "Needs to provide the name of the DNS server (will have to run nslookup?)"
        }
        response = userAction.get(action)
        return response
     
    def quiz_questions(self):
        questions = [
            {
                "question" : "\nHow many IP model layers are there?",
                "options": "\nA. 3  \nB. 1000  \nC. 5  \nD. -1",
                "answer" : "C"
            },
            {
                "question" : "\nWhat is an HTTP cookie used for?",
                "options": "\nA. A cookie is used to spoof client identity to an HTTP server  \nB. A cookie is a code used by a client to authenticate an identity to an HTTP server  \nC. Like dessert, cookies are used at the end of a transaction, to indicate the end of the transaction  \nD. A cookie is a code used by a server, carried on a client HTTP request, to access information the server had earlier stored about an earlier interaction with this Web browser",               
                "answer" : "D"
            },
            {
                "question" : "\nWhere in a router is the destination IP address looked up in a forwarding table to determine the appropriate output port to which the datagram should be directed?",
                "options" : "\nA. At the output port leading to the next hop towards the destination  \nB. At the input port where a packet arrives  \nC. Within the switching fabric \nD. Within the routing processor",
                "answer" : "D"
            }
        ]
        question = random.choice(questions)
        self.question = question
        return question
    
    def gameplay(self, question, answer):        
        client_answers = {}
        # This will wait for 10 seconds while the clients respond and save a dictionary of their answers 
        for user, _ in self.connections.items():
            time.sleep(10)
            if answer:
                client_answers[user] = answer
        # initial code for gameplay but will be better defined in Sprint 4
        for user, answer in client_answers.items():
            is_correct = answer == question["answer"]
            if is_correct:
                self.request = {
                    "action": "answer",
                    "answer": question["answer"],
                    "result": "You answered correctly"
                }
            else:
                self.request = {
                    "action": "answer",
                    "answer": question["answer"],
                    "result": "You answered incorrectly"
                }
            self.create_response()
        self.num_ques += 1


    def _create_response_json_content(self):
        action = self.request.get("action")
        #   Go into _user_action class with related actions 
        if action.lower() == "help" or action.lower() == "rules" or action == "-h" or action == "-i" or action == "-p" or action == "-n":
            #answer = request_search.get(action) or f'No match for "{action}".'
            answer = self.user_action(action)
            content = {"result": answer}
        elif self.first_request == True:
            content = {"result": f'Setting username to "{action}".'}
            self.first_request = False
        #this will take in the join request to start the game and process any answers
        elif action.lower() == "join":
            self._join_req = True
            question = self.quiz_questions()
            content = {
                "action": "question",
                "question": question["question"],
                "options" : question["options"] 
             }
        #this will create the quiz question response content
        elif action.lower() == "a" or action.lower() == "b" or action.lower() == "c" or action.lower() == "d":
            self.gameplay(self.question, action)
            question = self.quiz_questions()
        else:
            self.logger.error(f'Error: invalid action "{action}" for {self.addr}.')
            content = {"result": f'Error: invalid action "{action}".'}
        content_encoding = "utf-8"
        response = {
            "content_bytes": self._json_encode(content, content_encoding),
            "content_type": "text/json",
            "content_encoding": content_encoding
        }
        return response

    def process_events(self, mask):
        if mask & selectors.EVENT_READ:
            self.read()
        if mask & selectors.EVENT_WRITE:
            self.write()

    def read(self):
        self._read()

        if self._jsonheader_len is None:
            self.process_protoheader()

        if self._jsonheader_len is not None:
            if self.jsonheader is None:
                self.process_jsonheader()

        if self.jsonheader:
            if self.request is None:
                self.process_request()

    def write(self):
        if self.request:
            if not self.response_created:
                self.create_response()
                self.response_created = False
        self._write()
        self.request = None

    def close(self):
        self.del_connection(self.addr)
        try:
            self.selector.unregister(self.sock)
        except Exception as e:
            self.logger.error(f"error: selector.unregister() exception for {self.addr}: {repr(e)}.")

        try:
            self.sock.close()
        except OSError as e:
            self.logger.error(f"error: socket.close() exception for {self.addr}: {repr(e)}.")
        finally:
            # Delete reference to socket object for garbage collection
            self.sock = None

    def process_protoheader(self):
        hdrlen = 2
        if len(self._recv_buffer) >= hdrlen:
            self._jsonheader_len = struct.unpack(
                ">H", self._recv_buffer[:hdrlen]
            )[0]
            self._recv_buffer = self._recv_buffer[hdrlen:]

    def process_jsonheader(self):
        hdrlen = self._jsonheader_len
        if len(self._recv_buffer) >= hdrlen:
            self.jsonheader = self._json_decode(
                self._recv_buffer[:hdrlen], "utf-8"
            )
            self._recv_buffer = self._recv_buffer[hdrlen:]
            for reqhdr in (
                "byteorder",
                "content-length",
                "content-type",
                "content-encoding",
            ):
                if reqhdr not in self.jsonheader:
                    self.logger.error(f'Missing required header "{reqhdr}" for {self.addr}.')
                    raise ValueError(f'Missing required header "{reqhdr}".')

    def process_request(self):
        content_len = self.jsonheader["content-length"]
        if len(self._recv_buffer) < content_len:
            return
        # self._recv_buffer = self._recv_buffer[:content_len]
        data = self._recv_buffer[:content_len]
        if self.jsonheader["content-type"] == "text/json":
            encoding = self.jsonheader["content-encoding"]
            self.request = self._json_decode(data, encoding)
            if self.first_request == True:
                    request = self.request.get("action")
                    self.game_connections(request)
            else:
                request = self.request.get("action")
            print("received request", repr(request), "from", self.addr)
        self._recv_buffer = b""
        self._set_selector_events_mask("rw")

    def create_response(self):
        response = self.request.get("action")
        prepared_response = self._create_response_json_content()
        message = self._create_message(**prepared_response)
        print("sending response", repr(response), "to", self.username)
        self.response_created = True
        self._send_buffer += message
        # For quiz question responses, use asyncio and a task list to send synchronized questions to the clients in self.connections
        if response == "question":
            async def send_to_clients(self, client_addr):
                await self._set_selector_events_mask('w')  # Ensure write readiness before sending
                self._send_buffer = message
                await self._write(client_addr)

            async def send_questions_synchronized():
                questions = []
                for client_addr in self.connections.values():
                    questions.append(asyncio.create_task(send_to_clients(self, client_addr)))
                await asyncio.gather(*questions)

            asyncio.run(send_questions_synchronized())
        
        self._set_selector_events_mask("rw")
        self.jsonheader = None
        self._jsonheader_len = None

    def game_connections(self, username):
        if username not in self.connections:
            self.username = username
            self.connections[username] = self.addr
            print(f"{username} connected from {self.addr}")  
    
    def del_connection(self, addr):
        for key, value in list(self.connections.items()):
            if value == addr:
                print(f"", key, "disconnected.")
                del self.connections[key]
