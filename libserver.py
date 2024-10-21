
import sys
import selectors
import json
import io
import struct



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
        self.connections = {}

    def _set_selector_events_mask(self, mode):
        """Set selector to listen for events: mode is 'r', 'w', or 'rw'."""
        if mode == "r":
            events = selectors.EVENT_READ
        elif mode == "w":
            events = selectors.EVENT_WRITE
        elif mode == "rw":
            events = selectors.EVENT_READ | selectors.EVENT_WRITE
        else:
            raise ValueError(f"Invalid events mask mode {repr(mode)}.")
        self.selector.modify(self.sock, events, data=self)

    def _read(self):
        try:
            # Should be ready to read
            data = self.sock.recv(4096)
            self.game_connections()
        except BlockingIOError:
            # Resource temporarily unavailable (errno EWOULDBLOCK)
            pass
        else:
            if data:
                self._recv_buffer = b"" 
                self._recv_buffer += data
            else:
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

    def user_action(self, action):
        userAction = {
            "help": "Please enter the following format: app-client.py <host> <port> <action>, where <action> is either join or rules or help",
            "join": "\U0001F6A7 The networking quiz is under construction, please try again next Sprint \U0001F6A7",
            "rules": "\U0001F56D Choose the correct answer (A, B, C, or D) to the question on screen! The first to answer correctly gets 1 point. \U0001F56D"
        }
        response = userAction.get(action)
        # this is where the Sprint 4 gameplay will go
        # if response == "join":
             # enter gameplay options which will be answering A, B, C, D 
        return response
    
    def _create_response_json_content(self):
        action = self.request.get("action")
        #   Go into _user_action class with related actions 
        if action == "help" or action == "join" or action == "rules":
            #answer = request_search.get(action) or f'No match for "{action}".'
            answer = self.user_action(action)
            content = {"result": answer}
        else:
            content = {"result": f'Error: invalid action "{action}".'}
        content_encoding = "utf-8"
        response = {
            "content_bytes": self._json_encode(content, content_encoding),
            "content_type": "text/json",
            "content_encoding": content_encoding,
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

        self._write()

    def close(self):
        self.del_connection(self.addr)
        try:
            self.selector.unregister(self.sock)
        except Exception as e:
            print(
                f"error: selector.unregister() exception for",
                f"{self.addr}: {repr(e)}",
            )

        try:
            self.sock.close()
        except OSError as e:
            print(
                f"error: socket.close() exception for",
                f"{self.addr}: {repr(e)}",
            )
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
            request = self.request.get("action")
            print("received request", repr(request), "from", self.addr)
        self._recv_buffer = b""
        self._set_selector_events_mask("rw")

    def create_response(self):
        if self.jsonheader["content-type"] == "text/json":
            response = self._create_response_json_content()
        message = self._create_message(**response)
        response = self.request.get("action")
        print("sending response", repr(response), "to", self.addr)
        self.response_created = True
        self._send_buffer += message
        self._set_selector_events_mask("rw")
        self.request = None
        self.response_created = False
        self.jsonheader = None
        self._jsonheader_len = None

    def game_connections(self):
        n = 0
        name = "Client" + str(n)
        if name not in self.connections:
            n += 1
            self.connections[name] = self.addr
            print(f"{name} connected from {self.addr}")  
    
    def del_connection(self, addr):
        for key, value in list(self.connections.items()):
            if value == addr:
                print(f"", key, "disconnected.")
                del self.connections[key]
