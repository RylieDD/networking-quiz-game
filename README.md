# networking-quiz-game
This is a basic networking quiz game implemented using Python and sockets.
![jeopardy](https://github.com/user-attachments/assets/003effb0-ed99-4513-a5cd-e2f429822ffe)

## How to Play
1. **Start the server:** Run the 'server.py' script using syntax:python3 server.py -p <port>
2. **Connect the clients:** Run the 'client.py' script on two or three different machines or terminals using syntax: python3 client.py -i <host> -p <port>
3. **Set Username:** The game will prompt you to enter username with the phrase "Enter a username:"
4. **Join or Rules:** The game will then prompt you to join the game or learn more from the rules with the phrase "Enter join for the quiz game or rules to see the quiz game rules:"
5. **Wait for Others:** The game will then prompt you to start with the phrase "To start the quiz, enter start. If multiple players are connected, the game won't begin until everyone's started." The server will wait for all players to send "start" before starting the game.
7. **Play the game:** If start is entered, the game begins! Players will be shown 10 questions about networking and whoever has the most points after 10 questions will win! If the players have the same score, it's a draw!
8. **Restart or Quit:** When the game is done and the players scores are shown, users can enter "start" to restart or "exit" to leave the game.

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
The asyncio library is used to achieve non-blocking, asynchronous message handling. The server broadcasts state updates like new quiz questions and the game progress to all clients via JSON-encoded messages and the use of asyncio.gather() to send the messages simultaneously. Each client uses asyncio coroutines to receive and process these messages. The asyncio coroutines allow the clients to ensure their local state reflects the server's current state while still allowing user input to be handled concurrently.

## Game Play
The game presents the players with 10 questions sent one at a time after the start prompt is entered by all players. After a user enters their answer, it is sent to the server to check if it is correct or not, and the server returns whether or not the client got the question right. When 10 questions have been sent and the final answers have been received, the server sends the winner results to all clients and asks if clients would like to exit or restart the game. 

Known issues with the game:
1. Repeated usernames are not checked when clients set them.
2. The quiz_question is repeated for all ten questions.
3. Incorrect input to the quiz question causes AttributeError and causes the game to hang.
4. There is no timer on the client answers so a user could not send an answer and cause the game to wait indefinitely.
These known issues will be worked on before final submission.

## Security/Risk Evaluation
1. There is no authentication to verify the identity of clients so unauthroized users could enter the game. This could be mitigated through a login page that would require the server to authenticate the crednetials provided by the connecting client.
2. The input to the server is not validated which allows malicious users to perform injection attacks through the message protocol. This could be mitigated through validating the user input and ensuring that a specific format is followed and any other input is rejected.
3. Requests are not limited so a malicious client could perform a DoS attack on the server by sending a large amount of requests. This could be mitigated through rate limiting for client request throttling.
4. The packets between the clients and server are not encrypted and are sent in plaintext which could be intercepted and manipulated through a MitM attack. This could be mitigated through applying an encryption library and logic to the client and server code that encrypts the traffic between them.

## Statement of Work
https://github.com/RylieDD/networking-quiz-game/blob/main/SOW.md

## Additional Resources
* [socket Python Documentation](https://docs.python.org/3/library/socket.html)
* [ssl Python Documentation](https://docs.python.org/3/library/ssl.html)
* [Sockets Tutorial](https://realpython.com/python-sockets/)
* [asyncio Python Documentation](https://docs.python.org/3/library/asyncio.html)
