## Statement of Work
### Project Title:
networking-quiz-game
### Team:
Rylie Denehan
### Project Objective:
The goal of this project is to create a quiz show capability using knowledge gained from the CS457 course about servers, clients, sockets, etc. This quiz show will quiz contestants on questions consisting of the CS457 material and act as an additional study resource for the midterm and final.
### Scope:
#### Inclusions:
* TCP Server
* TCP Client
* Message Protocol
* Multi-Player Functionality
* Synchronized Client States
* Game Play
* Game State
* Game UI
* Error Handling
* Encryption  
#### Exclusions:
* Web Server/Client UI
### Deliverables:
* Working Python server and client scripts
* Working Python quiz-game script
* Gameplay Documentation
* SSL/TLS Encryption
### Timeline:
#### Key Milestones:
* Sprint 0: Setup Tool/GitHub and Submit SOW - estimated completion date: 9/22/2024
* Sprint 1: Implement TCP Server and Client - estimated completion date: 10/6/2024
* Sprint 2: Design and Implement Message Protocol - estimated completion date: 10/20/2024
* Sprint 3: Implement Multi-Player Functionality and Synchronize State Across Clients - estimated completion date: 11/3/2024
* Sprint 4: Design and Implment Game Play, Game State, and UI - estimated completion date: 11/17/2024
* Sprint 5: Implement Error Handling and Testing - estimated completion date: 12/6/2024
#### Task Breakdown:
* Sprint 0: Setup Tools

  a) Install necessary software and setup version control. (2 hours to complete)
* Sprint 0: Submit SOW

  a) Create and review Statement of Work for this project using the provided template. (2 hours to complete)
* Sprint 1: Basic Server Setup

   a) Create a server-side application that listens for incoming client connections on a specified port. (30 minutes to complete)
       
   b) Implement a mechanism to handle multiple client connections simultaneously.(30 minutes to complete)
       
   c) Log connection and disconnection events. (30 minutes to complete)
* Sprint 1: Client-Side Connection

   a) Develop a client-side application that can connect to the server. (30 minutes to complete)

   b) Implement error handling for failed connection attempts. (30 minutes to complete)

   c) Log connection and disconnection events. (30 minutes to complete)
* Sprint 1: Simple Message Exchange
   a) Establish a basic communication protocol between the server and clients. (30 minutes to complete)
       
   b) Implement functions to send and receive messages. (30 minutes to complete)
       
   c)Test the communication by sending simple messages back and forth. (15 minutes to complete)
* Sprint 1: Error Handling

   a) Implement basic error handling for network-related issues (e.g., connection timeouts, socket errors). (30 minutes to complete)

   b) Log error messages for debugging purposes. (30 minutes to complete)
* Sprint 1: Testing and Debugging

   a) Test the server's ability to handle multiple client connections. (15 minutes to complete)

   b) Verify that clients can connect to the server and exchange messages. (15 minutes to complete)

   c) Debug any issues related to network communication or socket operations. (15 minutes to complete)
* Sprint 1: Update README

   a) Update the GitHub README to reflect the capabilities added during Sprint 1. (30 minutes to complete)
* Sprint 2: Game Message Protocol Specification 

   a) Define the structure and format of messages exchanged between the server and clients. (2 hours to complete)
   
   b) Include message types (e.g., join, move, chat, quit), data fields, and expected responses. (2 hours to complete)
   
   c) Consider using a well-defined protocol like JSON or Protocol Buffers for serialization and deserialization. (2 hours to complete)
* Sprint 2: Server-Side Message Handling 

   a) Implement functions to receive, parse, and process incoming messages from clients. (4 hours to complete)
   
   b) Handle different message types appropriately (e.g., join requests, move commands, chat messages). (1 hour to complete)
   
   c) Maintain a list of connected clients and their associated game state. (1 hour to complete)
* Sprint 2: Client-Side Message Handling

  a) Implement functions to send messages to the server and handle incoming responses. (4 hours to complete)

  b) Parse server responses and update the client's game state accordingly. (1 hour to complete)

  c) Provide feedback to the user about the game's progress and any errors. (1 hour to complete)
* Sprint 2: Connection Management

   a) Implement mechanisms to handle client connections and disconnections. (2 hours to complete)
   
   b) Maintain a list of connected clients and their associated game data. (1 hour to complete)
   
   c) Notify other clients when a player joins or leaves the game. (1 hour to complete)
* Sprint 2: Update README

   a) Update the GitHub README to reflect the capabilities added during Sprint 2. (1 hour to complete)
* Sprint 3: Game State Synchronization

   a) Implement a mechanism to synchronize the game state across all connected clients. (3 hours to complete)
   
   b) Use a central server to broadcast game state updates to all clients. (3 hours to complete)
   
   c) Implement techniques to handle network latency and ensure consistent gameplay. (2 hours to complete)
* Sprint 3: Client-Side Game Rendering

   a) Develop the client-side logic to render the game state based on updates received from the server. (2 hours to complete)
   
   b) Ensure that all clients display the same game state/board and player updates/moves. (2 hour to complete)
* Sprint 3: Turn-Based Gameplay
   
   a) Synchronize turn information across all clients. (2 hours to complete)
* Sprint 3: Player Identification 
   
   a) Assign unique identifiers to each player to distinguish them and track their game state. (2 hours to complete)
   
   b) Allow players to choose or be assigned unique usernames or avatars. (1 hour to complete)
* Sprint 3: Update README

   a) Update the GitHub README to reflect the capabilities added during Sprint 3. (1 hour to complete)
* Sprint 4: Game State Management

   a) Update the game state based on player moves and winning conditions. (2 hours to complete)
   
   b) Store information about the current player, the game board, and any relevant game settings. (2 hours to complete)
* Sprint 4: Input Handling

   a) Implement functions to handle user input (e.g., mouse clicks, keyboard input) and translate it into game actions (e.g., placing a piece on the board). (2 hours to complete)
   
   b) Validate user input to ensure it is within the game's boundaries and rules. (1 hour to complete)
* Sprint 4: Winning Conditions

   a) Define the conditions for winning the game (e.g., three in a row, diagonal, etc.). (1 hour to complete)
   
   b) Implement logic to check for winning conditions after each move. (1 hour to complete)
   
   c) Notify players when a winner is determined or the game ends in a draw. (1 hour to complete)
* Sprint 4: Game Over Handling 

   a) Implement mechanisms to handle the end of a game. (1 hour to complete)
* Sprint 4: User Interface (UI)

   a) Develop a visually appealing and user-friendly UI for the game. (2 hours to complete)
   
   b) Display the game board, player information, and game status. (2 hours to complete)
   
   c) Provide clear and intuitive controls for players to interact with the game. (1 hour to complete)
* Sprint 4: Update README

   a) Update the GitHub README to reflect the capabilities added during Sprint 4. (1 hour to complete)
* Sprint 5: Error Handling

   a) Implement error handling mechanisms to catch and handle potential exceptions or unexpected situations. (2 hours to complete)
   
   b) Handle network errors, invalid input, and other potential issues gracefully. (2 hours to complete)
   
   c) Provide informative error messages to the user. (1 hour to complete)
* Sprint 5: Integration Testing 

   a) Test the entire game system to ensure that all components work together as expected. (4 hours to complete)
   
   b) Simulate different scenarios and test edge cases to identify potential bugs or issues. (4 hours to complete)
* Sprint 5: Security/Risk Evaluation

   a) Write a single paragraph or list describing what security issues your game may have and how they can be addressed. (1 hour to complete)
* Sprint 5: Update README

   a) Update the GitHub README to reflect the capabilities added during Sprint 5. (1 hour to complete)
### Technical Requirements:
#### Hardware:
* Server (CSU CS Lab computer)
* Router (for Internet Connection to Server)
#### Software:
* Python
* Git
* Visual Studio Code
* Windows 11
* Linux
* Python socket library
* Python threading library
* Python ssl library
* Python tkinter library
### Assumptions:
It is assumed that the CSU CS Lab computers will be available to run the Python scripts. It is also assumed that players have the resources to/understanding of how to run Python scripts.
### Roles and Responsibilities:
As a single person team, I will be all roles of project manager, developer, and tester:
* Project Manager Responsibilities: I will establish a clear plan with achievable milestones and defined tasking. I will maintain the README for the GitHub project page.
* Developer Responsibilities: I will complete defined project tasks in an effective manner and in the order outlined by the Project Manager. I will use best practices and document resources used as applicable. I will provide test cases for the tester and work with the tester to resolve issues.
* Tester Responsibilities: I will thoroughly test the project using test cases defined by the Developer and ones that I identify. I will provide feedback to the Developer and work with them as they resolve issues. 
### Communication Plan:
As a single person team, a communication channel is not needed.

The frequency of project updates will be at least 3 times weekly.
### Additional Notes:
* None right now.
