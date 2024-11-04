# networking-quiz-game
This is a basic networking quiz game implemented using Python and sockets.
![jeopardy](https://github.com/user-attachments/assets/003effb0-ed99-4513-a5cd-e2f429822ffe)

## How to Play
1. **Start the server:** Run the 'server.py' script using syntax: server.py host port
2. **Connect the clients:** Run the 'client.py' script on two or three different machines or terminals using syntax: client.py host port username, with username being a username of your choosing.
3. **Play the game:** Players will be shown 10 questions about networking and whoever has the most points after 10 questions will win!

## Technologies Used
* Python
* Sockets

## Message Protocol
The quiz game uses a JSON-based Message Protocol consisting of the Message Header and the Message Content. 
The Message Header has:
1. A 2-byte header for the JSON header length.
2. A JSON header with byte-order, content-type, content-encoding, and content-length.
The Message Content has:
1. A JSON object for the message data, which can range depending on the message type from and to the client.

## State Synchronization 
The quiz game questions and options are broadcast to all users that have joined the quiz game using the asyncio module and two asynchronous functions:
1. send_to_clients, this function waits for the selector to indicate the socket can be written to without blocking, assigns the prepared message to the_send_buffer, and asynchronously writes the message to the specified
client_addr
2. send_questions_synchronized, this function send quiz questions and options to all connected clients simultaneously by creating asynchronous tasks for each client by calling the send_to_clients function and waiting for all tasks to complete using 
asyncio.gather. 

## Statement of Work
https://github.com/RylieDD/networking-quiz-game/blob/main/SOW.md

## Additional Resources
* [socket Python Documentation](https://docs.python.org/3/library/socket.html)
* [tkinter Python Documentation](https://docs.python.org/3/library/tkinter.html)
* [ssl Python Documentation](https://docs.python.org/3/library/ssl.html)
* [Sockets Tutorial](https://realpython.com/python-sockets/)
