# Final Artifact README

## Contributors
- Garrett Kalter
- James Burke
- Lucca Figlioli
- Cade Smith

## Overview and Instructions

### Project Description
Our final artifact consists of four online games that can be played in the terminal of VSCode. The four online network games are designed for two players and include Battleship, Connect Four, Tic Tac Toe, and Hangman.

### Server and Client Setup
- **Server Address**: Hosted on the IPv4 address "149.43.0.29" and on port 5000.
- **Client and Server Code**: Each game has its client Python file and server Python file. For example, `BattleshipClient.py` handles the player's connection, and `BattleshipServer.py` sets up the server for each player to connect.

### Running a Game
1. **Server Terminal**: Open a terminal in the code editor, navigate to the Library folder, and run `python3 server.py`. This terminal will act as the server. The server can be started remotely on any device, and the players will be able to connect via an alternate device.
2. **Player Terminals**: Open two other terminals, navigate to the same folder, and enter `python3 client.py` in each. These will be the player terminals.
3. **Gameplay**: Follow the on-screen instructions in the client terminals to play the games. Each terminal represents one player.

## Challenges and Solutions

### Connection Handling
- **Disconnections**: Initially, handling player disconnections was problematic. For example, if Player 2 disconnected, we needed to close Player 1's connection with a proper message. We implemented custom disconnection handling in each game's server and client code to address this.

### Game-Specific Network Implementation
- **Differences Between Games**: Games like Connect4 and Tic Tac Toe maintain a single board updated with each move, whereas Battleship and Hangman have separate setups for each player. The initialization differs too, such as placing ships in Battleship and entering a word in Hangman.

### Error Handling
- **Connection Errors**: We used a try-except block within the `handle_two_player_session` function to manage potential socket errors during the initial game choice phase. On detecting a connection error, the system notifies the other player and resets the library using `restartLibrary` function for a clean setup for new sessions.

## Conclusion

This project allowed us to leverage our understanding of sockets and network-based connections to develop a suite of multiplayer games. Despite challenges with disconnections and game-specific logic, we successfully implemented a server that hosts four fun games, each offering complete multiplayer gameplay and comprehensive error-handling.
