# networking-quiz-game
This is a basic networking quiz game implemented using Python and sockets.
![jeopardy](https://github.com/user-attachments/assets/003effb0-ed99-4513-a5cd-e2f429822ffe)

## How to Play
NOTE: Ensure that the cert.pem and key.pem files are in the same directory as the server.py before running. This should be automatically done by pulling the repo but double-check if connection issues arise.
1. **Start the server:** Run the 'server.py' script using syntax: python3 server.py -p <port>
2. **Connect the clients:** Run the 'client.py' script on two or three different machines or terminals using syntax: python3 client.py -i <host> -p <port>
3. **Set Username:** The game will prompt you to enter username with the phrase "Enter a username:"
4. **Join or Rules:** The game will then prompt you to join the game or learn more from the rules with the phrase "Enter join for the quiz game or rules to see the quiz game rules:"
5. **Wait for Others:** The game will then prompt you to start with the phrase "To start the quiz, enter start. If multiple players are connected, the game won't begin until everyone's started." The server will wait for all players to send "start" before starting the game.
7. **Play the game:** If start is entered, the game begins! Players will be shown 10 questions about networking and whoever has the most points after 10 questions will win! If the players have the same score, it's a draw!
8. **Restart or Quit:** When the game is done and the players scores are shown, users can enter "start" to restart or "exit" to leave the game.

## Technologies Used
* Python
* Sockets
* ssl

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
2. There is no timer on the client answers so a user could not send an answer and cause the game to wait indefinitely.

## Encryption
TLS encryption is utilized by the client and server to encrypt the traffic between the two. The cert.pem and key.pem are included in the networking-quiz-game repo and are configured to work with the following cs machines:
1. baghdad.cs.colostate.edu
2. pepper.cs.colostat.edu
3. pumpkin.cs.colostate.edu
4. potato.cs.colostate.edu
The python ssl library was used to implement this encryption but it automatically utilizes the latest TLS version for the cryptographic protocol and older version of SSL have been set to not be used.

## Security/Risk Evaluation
1. There is no authentication to verify the identity of clients so unauthroized users could enter the game. This could be mitigated through a login page that would require the server to authenticate the crednetials provided by the connecting client.
2. The input to the server is not validated which allows malicious users to perform injection attacks through the message protocol. This could be mitigated through validating the user input and ensuring that a specific format is followed and any other input is rejected.
3. Requests are not limited so a malicious client could perform a DoS attack on the server by sending a large amount of requests. This could be mitigated through rate limiting for client request throttling.
4. The packets between the clients and server are encrypted but the cert.pem and key.pem files are stored in the repo for users to utilize, which could be used be a malicious actor to decrypt and manipulate the traffic of the client(s) and server with a MitM attack. This could be mitigated through applying a way for clients to create their own cert and key files before inital connection to the server that are then verified by the server.

## Project Retrospective
Areas where this project went right were:
1. The state synchronization between the clients is working properly.
2. Encryption has been applied to the communication between the client(s) and server.
3. Gameplay logic has been successfully created, refined, and implemented.
4. Knowledge and experience have been gained about the process to setup client and server communication that is robust, consistent, and secure.

Things that could have been improved were:
1. I could have taken more time to properly understand state synchronization and how to apply the asyncio library, so I could have prevented a significant time sink to fix the synchronization of the clients.
2. I could have first planned out any gameplay logic on paper before just starting to apply it to the quiz through code to have saved time with fixing logic mistakes.
3. I could have reached out to TAs or the instructor sooner when I was facing roadblocks.

Given more time, I would like to take this project to where there is a simple GUI to interact with to answer questions instead of using the terminal, more questions that would track the topics of the questions and suggest where a user could focus their studying on, and a more robust and secure encryption implementation for users.

## Statement of Work
https://github.com/RylieDD/networking-quiz-game/blob/main/SOW.md

## Additional Resources
* [socket Python Documentation](https://docs.python.org/3/library/socket.html)
* [ssl Python Documentation](https://docs.python.org/3/library/ssl.html)
* [Sockets Tutorial](https://realpython.com/python-sockets/)
* [asyncio Python Documentation](https://docs.python.org/3/library/asyncio.html)
