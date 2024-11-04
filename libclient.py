
import sys
import selectors
import json
import io
import struct
import time
import logging


class Message:
    def __init__(self, selector, sock, addr, request):
        self.selector = selector
        self.sock = sock
        self.addr = addr
        self.request = request
        self._recv_buffer = b""
        self._send_buffer = b""
        self._request_queued = False
        self._jsonheader_len = None
        self.jsonheader = None
        self.response = None
        self.username = None
        self.score = 0
        self.quizStart = False

        #Setup logging
        self.logger = logging.getLogger(self.__class__.__name__)
        self.logger.setLevel(logging.ERROR)
        formatter = logging.Formatter('%(asctime)s - %(levelname)s - %(message)s')
        handler = logging.FileHandler('Client_Error.log')
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


    # GameState updates printed here, call game_state class to update the current GameState
    def _process_response_json_content(self):
        content = self.response
        action = content.get("action")
        #
        if action == "question" or action == "answer":
                self.game_state(content)
        else:
            result = content.get("result")
            print(f"{result}")

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
            if self.response is None:
                self.process_response()

    def write(self):
        if not self._request_queued:
            self.queue_request(None)

        self._write()

        if self._request_queued:
            if not self._send_buffer:
                # Set selector to listen for read events, we're done writing.
                self._set_selector_events_mask("r")

    def close(self):
        print("You are now disconnected, goodbye!")
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

    #Change game state to update after quiz is running.
    def game_state(self, content):
        userGameState = {}
        question = content.get("question")
        options = content.get("options")
        if content.get("question"):
            print(f'Question:', question)
            print(f'Options:', options)
            self.user_inputs()
        #Next two elifs calculates the user's score based on the returned answer from the server 
        elif content.get("result") == "You answered correctly":
            self.score += 1
            print(content.get("result"))
        elif content.get("result") == "You answered incorrectly":
            print(content.get("result"))
        #The user state is updated and printed to the client
        userGameState.update(user=self.username, address=self.addr, score=self.score)
        print(userGameState.get("user"),"current score is:", userGameState.get("score"))
    
    def queue_request(self, user_input):
        content = self.request["content"]
        content_type = self.request["type"]
        content_encoding = self.request["encoding"]

        if user_input is not None:
            self._send_buffer = b""
            content = {"action": user_input}
        else:
            self.username = content.get("action")
            content_type == "text/json"
        req = {
                "content_bytes": self._json_encode(content, content_encoding),
                "content_type": content_type,
                "content_encoding": content_encoding,
            } 
        message = self._create_message(**req)
        self.gamestate = content
        self._send_buffer += message
        self._request_queued = True

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

    def process_response(self):
        content_len = self.jsonheader["content-length"]
        if not len(self._recv_buffer) >= content_len:
            return
        data = self._recv_buffer[:content_len]
        self._recv_buffer = self._recv_buffer[content_len:]
        if self.jsonheader["content-type"] == "text/json":
            encoding = self.jsonheader["content-encoding"]
            self.response = self._json_decode(data, encoding)
            self._process_response_json_content()
        self._recv_buffer = b""
        self._send_buffer = b""
        self._request_queued = False
        self._jsonheader_len = None
        self.jsonheader = None
        self.response = None
        self._set_selector_events_mask("rw")
        self.user_inputs()

    def user_inputs(self):
        user_input = input("Enter input (or 'exit' to quit): ")
        # Close if exit action exists
        if user_input.lower() == "exit":
            self.close()
        elif user_input.lower() == "join":
            print(f"The Quiz is beginning! When the question appears, you will have 10 seconds enter the correct response of A, B, C, or D.")
            #Adding pause for users to read the quiz rules
            time.sleep(5)
            self.quizStart = True
            self.queue_request(user_input)
        elif user_input.lower() == "a" or user_input.lower() == "b" or user_input.lower() == "c" or user_input.lower() == "d":
            print(f'You are answering ', user_input)
            self.queue_request(user_input)
        else:
            self.queue_request(user_input)
