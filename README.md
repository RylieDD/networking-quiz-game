# networking-quiz-game
This is a basic networking quiz game implemented using Python and sockets.
![jeopardy](https://github.com/user-attachments/assets/003effb0-ed99-4513-a5cd-e2f429822ffe)

## How to Play
1. **Start the server:** Run the 'server.py' script using syntax:python3 server.py -p <port>
2. **Connect the clients:** Run the 'client.py' script on two or three different machines or terminals using syntax: python3 client.py -i <host> -p <port>
3. **Set Username:** The game will prompt you to enter username with the phrase "Enter a username:"
4. **Join or Rules:** The game will then prompt you to join the game or learn more from the rules with the phrase "Enter join for the quiz game or rules to see the quiz game rules:"
5. **Wait for Others:** The game will then prompt you to wait for other players or start on your own with the phrase "To wait to start the quiz with other players, enter wait. To start the quiz, enter start."
7. **Play the game:** If start is entered, the game begins! Players will be shown 10 questions about networking and whoever has the most points after 10 questions will win!

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
This logic is currently not functioning due to edits during this sprint. The game will operate with one user but the state synchronization needed to be moved from the libserver.py to the server.py and was not completed in time for Sprint 4. The state synchronization will incorporate the asyncio module when it is operating.
The quiz game questions and options are broadcast to all users that have joined the quiz game using the asyncio module and two asynchronous functions:
1. send_to_clients, this function waits for the selector to indicate the socket can be written to without blocking, assigns the prepared message to the_send_buffer, and asynchronously writes the message to the specified
client_addr
2. send_questions_synchronized, this function send quiz questions and options to all connected clients simultaneously by creating asynchronous tasks for each client by calling the send_to_clients function and waiting for all tasks to complete using 
asyncio.gather. 

## Game Play
The game presents the players with 10 questions after the start prompt is entered. A user enters their answer, it is sent to the server to check if it is correct or not, and the server returns the answer to the client so the results can be shown in the terminal and the user's score can be updated. 

## Statement of Work
https://github.com/RylieDD/networking-quiz-game/blob/main/SOW.md

## Additional Resources
* [socket Python Documentation](https://docs.python.org/3/library/socket.html)
* [tkinter Python Documentation](https://docs.python.org/3/library/tkinter.html)
* [ssl Python Documentation](https://docs.python.org/3/library/ssl.html)
* [Sockets Tutorial](https://realpython.com/python-sockets/)
