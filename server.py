import socket
import threading
import time
from games.Con4 import *
from games.Connect4Client import * 
from games.BattleshipServer import BattleshipGame
from games.BattleshipServer import BattleshipServer
from games.tServer import *
from games.tClient import *
from games.hangpersonClient import *
from games.hangpersonServer import *

#OpenAI's ChatGPT was consulted during the debugging process of some parts of this code, licensing agreement provided at the bottom of this file

game_options = {
    '1': BattleshipServer,
    '2': ConnectFourServer,
    '3': TicTacToeServer,
    '4': hangpersonServer,
    '5': BattleshipServer
}

def handle_two_player_session(conn1, conn2, sock):
    try:
        while True:
            time.sleep(1)
            conn1.sendall("Choose a game:\n1. Battleship\n2. Connect4\n3. Tic Tac Toe\n4. Hangman\nOr press '5' to shut down the library ".encode())
            conn2.sendall("Waiting for player 1 to choose a game...\n".encode())
            
            choice1 = conn1.recv(1024).decode().strip()
            if not choice1:
                conn2.sendall("Player 1 disconnected".encode())
                print("Player 1 disconnected, restarting library...")
                restartLibrary(sock)
                return
            print(f"Debug: Player 1 choice received: {choice1}")  

            conn2.sendall(f"Player 1 chose {choice1}. Please confirm by typing '{choice1}' or choose another game.".encode())
            choice2 = conn2.recv(1024).decode().strip()
            if not choice2:
                conn1.sendall("Player 2 disconnected".encode())
                print("Player 2 disconnected, restarting library...")
                restartLibrary(sock)
                return
            print(f"Debug: Player 2 choice received: {choice2}") 
        
            if choice1 == choice2 and choice1 in game_options:
                if choice1 == '5':
                    return
                conn1.sendall("Game starting. Wait for your turn...\n".encode())
                conn2.sendall("Game starting. Wait for your turn...\n".encode())
                print("Starting game...")
                players = [conn1, conn2]
                if choice1 == '1':
                    startBattleshipServer(sock, players)  
                    return
                if choice1 == '2':
                    startConnect4Server(sock, players)
                    return
                if choice1 == '3':
                    startTicServer(sock, players)
                    return
                if choice1 == '4':
                    startHangServer(sock, players)
                    return
            else:
                conn1.sendall("Failed to agree on a game. Please try again.\n".encode())
                conn2.sendall("Failed to agree on a game. Please try again.\n".encode())
    except socket.error:
        print("Game Over/Connection Error")
        restartLibrary(sock)
        return
    
def startBattleshipServer(sock, playerArray):
    print("Starting Battleship Game")
    server = BattleshipServer(client_sock = sock, players = playerArray)
    server.setup_game()
    restartLibrary(sock)
    return

def startConnect4Server(sock, playerArray):
    print("Starting Connect4 Game")
    server = ConnectFourServer(server_sock = sock, players = playerArray)
    server.play_game(playerArray[0], playerArray[1])
    restartLibrary(sock)
    return

def startTicServer(sock, playerArray):
    print("Starting Tic Tac Toe Game")
    server = TicTacToeServer(server_socket = sock, players=playerArray)
    server.play_game(playerArray[0], playerArray[1])
    restartLibrary(sock)
    return

def startHangServer(sock, playerArray):
    print("Starting Hangperson Game")
    server = hangpersonServer(server_socket = sock, players=playerArray)
    server.play_game(playerArray[0], playerArray[1])
    restartLibrary(sock)
    return

def main():
    host = '149.43.80.29'  
    port = 5000
    server_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    server_socket.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
    server_socket.bind((host, port))
    server_socket.listen(5)
    print("Server started. Waiting for connections...")

    try:
        while True:
            conn1, addr1 = server_socket.accept()
            print(f"Player 1 connected from {addr1}")
            conn1.sendall("Connected to server. Waiting for another player...\n".encode())

            conn2, addr2 = server_socket.accept()
            print(f"Player 2 connected from {addr2}")
            conn2.sendall("Connected to server. Player 1 is ready.\n".encode())

            server_socket.close()

            handle_two_player_session(conn1, conn2, server_socket)
            return

    except KeyboardInterrupt:
        print("Server is shutting down.")
        return
    finally:
        print("Library shutting down, thank you for playing!")
        server_socket.close()

def restartLibrary(server_socket):
    print("Waiting for new connections...")
    host = '149.43.80.29'  
    port = 5000
    server_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    server_socket.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
    server_socket.bind((host, port))
    server_socket.listen(5)

    try:
        while True:
            try:
                conn1, addr1 = server_socket.accept()
                print(f"Player 1 connected from {addr1}")
                conn1.sendall("Connected to server. Waiting for another player...\n".encode())

                conn2, addr2 = server_socket.accept()
                print(f"Player 2 connected from {addr2}")
                conn2.sendall("Connected to server. Player 1 is ready.\n".encode())

                server_socket.close()

                handle_two_player_session(conn1, conn2, server_socket)
            except socket.error:
                print("Game Over/Connection Error")
                return

    except KeyboardInterrupt:
        print("Server is shutting down.")
        return
    finally:
        #print("Finally")
        server_socket.close()

if __name__ == "__main__":
    main()

"""
The code provided by me (or any other OpenAI model) is generated on-the-fly and is not copyrighted or 
sourced from any specific external location. You're free to use, modify, and distribute the code as you see fit.
Licensing Requirements:
There are no specific licensing requirements for the code. 
You can consider it as being under a permissive license, like the MIT License or similar, 
which means you can use it for any purpose without any restrictions, and you're not 
required to include the original copyright notice or disclaimers.
"""