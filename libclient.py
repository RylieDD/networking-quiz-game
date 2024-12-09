import asyncio
import json
import struct
from collections import deque
import sys
import logging

#This Message class contains all the Client Messaging Protocol logic to read, write, encode, decode, process, and send the client input and the server responses.
#The game state of the clients to output the quiz questions and options is also handled here.
class Message:
    def __init__(self, reader, writer, loop):
        self.reader = reader
        self.writer = writer
        self.loop = loop
        self.username = None
        self.quizStart = False
        self.quizEnd = False
        self.first_ques = False
        self.waiting_for_question = False
        self.message_queue = deque()
        self.message_event = asyncio.Event()
        self.message_event.set()
        self.wait = False

        #Setup logging
        self.logger = logging.getLogger(self.__class__.__name__)
        self.logger.setLevel(logging.ERROR)
        formatter = logging.Formatter('%(asctime)s - %(levelname)s - %(message)s')
        handler = logging.FileHandler('Client_Error.log')
        handler.setFormatter(formatter)
        self.logger.addHandler(handler)


    async def send_message(self, content):
        try:
            encoded_content = self._json_encode(content, "utf-8")
            jsonheader = {
                "byteorder": "little",
                "content-type": "text/json",
                "content-encoding": "utf-8",
                "content-length": len(encoded_content),
            }
            header = self._json_encode(jsonheader, "utf-8")
            header_len = struct.pack(">H", len(header))
            message = header_len + header + encoded_content
            self.writer.write(message)
            await self.writer.drain()
        except (asyncio.CancelledError, ConnectionResetError, BrokenPipeError) as e:
            self.logger.error(f"Connection error while sending message: {e} for {self.reader}.")
            print(f"Connection error while sending message: {e}")
            return
        except Exception as e:
            self.logger.error(f"Error sending message: {e} for {self.reader}.")
            print(f"Error sending message: {e}")

    async def receive_messages(self):
        try: 
            while True:
                try:
                    # Read header length
                    header_len = await self.reader.readexactly(2)
                    header_len = struct.unpack(">H", header_len)[0]

                    # Read header
                    header = await self.reader.readexactly(header_len)
                    jsonheader = self._json_decode(header, "utf-8")

                    # Read content
                    content_len = jsonheader["content-length"]
                    content = await self.reader.readexactly(content_len)
                    decoded_message = self._json_decode(content, "utf-8")
                    self.message_queue.append(decoded_message)
                except asyncio.IncompleteReadError:
                    self.logger.error(f"Connection closed by server. for {self.reader}.")
                    print("Connection closed by server.")
                    break
                except ConnectionResetError:
                    self.logger.error(f"Server connection reset. Exiting message receiving. for {self.reader}.")
                    print("Server connection reset. Exiting message receiving.")
                    break
                except Exception as e:
                    self.logger.error(f"Error receiving message: {e} for {self.reader}.")
                    print(f"Error receiving message: {e}")
                    await asyncio.sleep(0.1)
        except KeyboardInterrupt:
            self.logger.error(f"KeyboardInterrupt detected during message reception. Exiting. for {self.reader}.")
            print("KeyboardInterrupt detected during message reception. Exiting.")
            

    async def process_messages(self):
        try: 
            while True:
                if self.message_queue:
                    try:
                        message = self.message_queue.popleft()
                        await self.process_response(message)
                    except Exception as e:
                        self.logger.error(f"Error processing message: {e} for {self.reader}.")
                        print(f"Error processing message: {e}")
                await asyncio.sleep(0.1)
        except KeyboardInterrupt:
            self.logger.error(f"KeyboardInterrupt detected during message processing. Exiting. for {self.reader}.")
            print("KeyboardInterrupt detected during message processing. Exiting.")

    async def process_response(self, response):
        try:
            action = response.get("action")
            input = response.get("input")
            if not action:
                print(response.get("result", "Unknown response"))
                return
            elif action.lower() == "exit":
                sys.exit(1)
            elif action.lower() == "username":
                print(response["result"])
            elif action.lower() in ["rules", "help", "-h", "-n"]:
                print(response["result"])
            elif action.lower() == "info":
                print(response["result"])
                print(input)
            elif action.lower() == "start":
                print(response["result"])
                self.waiting_for_question = True
            elif action.lower() == "question":
                self.waiting_for_question = False
                self.game_state(response)
                print(input)
            elif action.lower() == "answer":
                self.game_state(response)
            elif action.lower() == "end":
                self.quizStart = False
                self.quizEnd = True
                print(response["result"])
                print(input)
            else:
                print(f"Unknown action: {action}")
            
        except Exception as e:
            self.logger.error(f"Error processing response: {e} for {self.reader}.")
            print(f"Error processing response: {e}")

    async def handle_user_inputs(self):
        while True:
                try:
                    await self.message_event.wait()
                    if not self.username:
                        user_input = await self.loop.run_in_executor(None, input, "Enter your username: ")
                        await self.send_message({"action": user_input})
                        self.username = user_input
                    elif not self.quizStart and not self.first_ques:
                        user_input = await self.loop.run_in_executor(None, input, "")
                        if user_input == "join":
                            self.first_ques = True
                        elif user_input == "rules":
                            print("Enter join for the quiz game or rules to see the quiz game rules:")
                        await self.send_message({"action": user_input})
                    elif not self.quizStart and self.first_ques:
                        user_input = await self.loop.run_in_executor(None, input, "")
                        if user_input == "start":
                            self.quizStart = True
                        await self.send_message({"action": user_input})
                    elif self.waiting_for_question:
                        print("Waiting for the quiz question...")
                        await asyncio.sleep(1)
                    elif self.quizStart:
                        user_input = await self.loop.run_in_executor(None, input, "")
                        if user_input == "start":
                                self.quizStart = True
                                self.quizEnd = False
                                await self.send_message({"action": user_input})
                        elif user_input == "exit":
                            await self.send_message({"action": user_input})
                            break
                        else:
                            await self.send_message({"action": "answer", "choice": user_input})  
                except KeyboardInterrupt:
                    self.logger.error(f"Exiting input loop. for {self.reader}.")
                    print("Exiting input loop.")
                except Exception as e:
                    self.logger.error(f"Error handling user input: {e} {self.reader}.")
                    print(f"Error handling user input: {e}")
                    break
    
    def game_state(self, content):
        if content.get("action") == "question":
            question = content.get("question")
            print(f"Question:{question}")
            options = content.get("options")
            print(f"Options: {options}")
        elif content.get("action") == "answer":
            result = content.get("result")
            print(result)

    def _json_encode(self, obj, encoding):
        return json.dumps(obj, ensure_ascii=False).encode(encoding)

    def _json_decode(self, json_bytes, encoding):
        return json.loads(json_bytes.decode(encoding))
