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
        self.num_ques = 0
        self.question = None
        self.quizStart = False
        self.first_con = True
        self.score = 0
        
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
            "connect" : "Welcome to the Networking Quiz Game",
            "help" : "Please enter the following format: <action>, where action is join or rules",
            "rules" : "\U0001F56D Enter join to start the quiz game. When the quiz starts, choose the correct answer (A, B, C, or D) to the question on screen! Answer correctly for 1 point. \U0001F56D",
            "-h" : "Please enter the following format: app-client.py -i <host> -p <port> to connect",
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
            },
            {
                "question" : "\nWhat is the purpose of a manifest file in a streaming multimedia setting?",
                "options" : "\nA. To let a client know where it can retrieve different video segments, encoded at different rates  \nB. To let a OTT (Over-the-top) video server know the video that the client wants to view  \nC. Allows a video service to log the video and the server from which a client streams a video  \nD. To allow a client to reserve bandwidth along a path from a server to that client, so the client can view a stream video without impairment.",
                "answer" : "A"
            },
            {
                "question" : "\nWhat approach is taken by a CDN to stream content to hundreds of thousands of simultaneous users?",
                "options" : "\nA. Proactively push videos to a client device before they are requested, using machine learning to predict requested videos  \nB. Allow client devices to send requested content to each other, in order to offload the CDN infrastructure  \nC. Store/serve multiple copies of videos at multiple geographically distributed sites  \nD. Serve video from a single central “mega-server” with ultra-high-speed network connectivity, and high-speed storage",
                "answer" : "C"
            },
            {
                "question" : "\nSuppose a Web server has five ongoing connections that use TCP receiver port 80, and assume there are no other TCP connections (open or being opened or closed) at that server.  How many TCP sockets are in use at this server?",
                "options" : "\nA. 6  \nB. 1  \nC. 5  \nD. 4",
                "answer" : "A"
            },
            {
                "question" : "\nWhat happens when a socket connect() procedure is called/invoked?",
                "options": "\nA. This causes the client to reach out to a TCP server to establish a connection between that client and the server. If there is already one or more servers on this connection, this new server will also be added to this connection  \nB. This procedure creates a new socket at the client, and connects that socket to the specified server  \nC. This causes the server to reach out to a TCP client to establish a connection between that client and the server  \nD. Nothing at all",
                "answer" : "B"
            },
            {
                "question" : "\nWhere is transport-layer functionality primarily implemented?",
                "options" : "\nA. Transport layer functions are implemented primarily at the routers and switches in the network  \nB. Transport layer functions are implemented primarily at the hosts at the “edge” of the network  \nC.Transport layer functions are implemented primarily in the cloud  \nD. Transport layer functions are implemented primarily at each end of a physical link connecting one host/router/switch to another one host/router/switch",
                "answer" : "B"
            },
            {
                "question" : "\nWhat is meant by transport-layer demultiplexing?",
                "options" : "\nA. Taking data from one socket (one of possibly many sockets), encapsulating a data chuck with header information (thereby creating a transport layer segment) and eventually passing this segment to the network layer  \nB. Taking data from multiple sockets, all associated with the same destination IP address, adding destination port numbers to each piece of data, and then concatenating these to form a transport-layer segment, and eventually passing this segment to the network layer  \nC. Receiving a transport-layer segment from the network layer, extracting the payload (data) and delivering the data to the correct socket  \nD. Receiving a transport-layer segment from the network layer, extracting the payload, determining the destination IP address for the data, and then passing the segment and the IP address back down to the network layer",
                "answer" : "C"
            },
            {
                "question" : "\nWhat is meant by transport-layer multiplexing?",
                "options" : "\nA. Taking data from one socket (one of possibly many sockets), encapsulating a data chuck with header information (thereby creating a transport layer segment) and eventually passing this segment to the network layer  \nB. Receiving a transport-layer segment from the network layer, extracting the payload (data) and delivering the data to the correct socket  \nC. Taking data from multiple sockets, all associated with the same destination IP address, adding destination port numbers to each piece of data, and then concatenating these to form a transport-layer segment, and eventually passing this segment to the network layer  \nD. Receiving a transport-layer segment from the network layer, extracting the payload, determining the destination IP address for the data, and then passing the segment and the IP address back down to the network layer",
                "answer" : "A"
            },
            {
                "question" : "\nWhat is the name of the security defense that provides confidentiality by encoding contents?",
                "options" : "\nA. Access control  \nB. Digital signatures  \nC. Encryption  \nD. Firewall",
                "answer" : "C"
            },
            {
                "question" : "\nWhat is the name of the security defense that is used to detect tampering/changing of message contents, and to identify the originator of a message?",
                "options" : "\nA. Firewall  \nB. Digital signatures  \nC. Authentication  \nD. Access control",
                "answer" : "B"
            },
            {
                "question" : "\nWhat is the name of the security defense that proves you are who you say you are?",
                "options" : "\nA. Firewall  \nB. Encryption  \nC. Access control  \nD. Authentication",
                "answer" : "D"
            },
            {
                "question" : "\nLimiting use of resources or capabilities to given users?",
                "options" : "\nA. Digital signatures  \nB. Authentication  \nC. Access control  \nD. Encryption",
                "answer" : "C"
            },
            {
                "question" : "\nWhat is the definition of a “good” path for a routing protocol?",
                "options" : "\nA. A path that has a minimum number of hops  \nB. A low delay path  \nC. A path that has little or no congestion  \nD. Routing algorithms typically work with abstract link weights that could represent any of, or combinations of, all of the other answers",
                "answer" : "D"
            }
        ]
        question = random.choice(questions)
        self.question = question
        return question
    
    def gameplay(self, question, answer):
        # This take input from the clients responses for 10 questions and save a dictionary of their answers to compare if they are right or wrong
        if self.num_ques < 10:       
            is_correct = answer.upper() == question["answer"]

            if is_correct:
                content = {
                    "answer": question["answer"],
                    "result": "You answered correctly"
                }
                self.score += 1
            else:
                content = {
                    "answer": question["answer"],
                    "result": "You answered incorrectly"
                }
            self.num_ques += 1
            return content
        else:
            
            content = {
                "result" : f'User "{self.username}" is the winner with a score of "{self.score}"!'
            }
            return content


    def _create_response_json_content(self):
        action = self.request.get("action")
        #   Go into _user_action class with related actions 
        if action.lower() == "help" or action.lower() == "rules" or action == "-h" or action == "-i" or action == "-p" or action == "-n" or action == "connect":
            #answer = request_search.get(action) or f'No match for "{action}".'
            answer = self.user_action(action)
            content = {"result": answer}
        elif self.username == None and self.first_con == False:
            self.game_connections(action)
            content = {"result": f'Setting username to "{action}".'}
        #this will take in the join request to start the game and process any answers
        elif action.lower() == "join":
            # Check if player wants multiple players or just them
            self.request["action"] = "initial"
            content = {
                "result" : "To wait to start the quiz with other players, enter wait. To start the quiz, enter start."
            }
        elif action.lower() == "wait":
            content = {"result" : "Waiting to start the quiz."}
        elif action.lower() == "start" or action.lower() == "question":
            self.quizStart = True
            self.request["action"] = "question"
            question = self.quiz_questions()
            content = {
                "question": question["question"],
                "options" : question["options"] 
             }
        #this will create the quiz question response content
        elif action.lower() == "a" or action.lower() == "b" or action.lower() == "c" or action.lower() == "d" or action.lower() == "none":
            self.request["action"] = "answer"
            quiz_answer = self.gameplay(self.question, action)
            content = quiz_answer
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

    #logic to wait for addtional players or to play by yourself
    def player_wait(self, username):
        #send a response to the user asking if waiting or not 
        
        return "You are waiting "
    
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
            if self.first_con == True:
                    request = self.request.get("action")
                    self.first_con = False
            else:
                request = self.request.get("action")
            print("received request", repr(request), "from", self.addr)
        self._recv_buffer = b""
        self._set_selector_events_mask("rw")

    def create_response(self):
        prepared_response = self._create_response_json_content()
        message = self._create_message(**prepared_response)
        response = self.request.get("action")
        print("sending response", repr(response), "to", self.username)
        self.response_created = True
        self._send_buffer += message
        self._set_selector_events_mask("rw")
        self.jsonheader = None
        self._jsonheader_len = None

    def game_connections(self, username):
        self.username = username
        self.connections[self.username] = self.addr
        self.logger.error(f"Peer started connection for {self.addr} with username {self.username}.")

    def del_connection(self, addr):
        for key, value in list(self.connections.items()):
            if value == addr:
                print(f"", key, "disconnected.")
                del self.connections[key]
