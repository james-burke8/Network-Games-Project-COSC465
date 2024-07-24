import socket
import sys
from termios import TCIFLUSH, tcflush

class BattleshipClient:
    def __init__(self, client_sock):
        self.host = "149.43.80.29"
        self.port = 5587
        self.client_socket = client_sock
        #self.connect()
        self.terminate = False

    def connect(self):
        try:
            self.client_socket.connect((self.host, self.port))
            print("Connected to server.")
        except:
            print("Connection to server failed, game full.")
            self.terminate = True

    def setup(self):
        if self.terminate:
           return
        message = self.client_socket.recv(1024).decode()
        if not message:
            s = "Connection Error. Game Over!"
            print(s)
            return
        print(message)
        count = 0
        while True:
            try:
                while True:
                    tcflush(sys.stdin, TCIFLUSH)
                    move = input("Enter your move (x,y): ")
                    if move != "":
                        break
                try:
                    self.client_socket.send(move.encode())
                except socket.error:
                    s = "Connection error. Game Over!"
                    print(s)
                    return
                response = self.client_socket.recv(1024).decode()
                print(response)
                if "Ship placed successfully." in response:
                    count += 1
                if count > 4:
                    self.play()
                    break
            except KeyboardInterrupt:
                print("Game ended.")
                break

    def play(self):
        print("Ready to Start, waiting for other player to place ships")
        
        while True:
            try:
                message = self.client_socket.recv(1024).decode()
                if not message:
                    s = "Connection error. Game Over!"
                    print(s)
                    return
                print(message)
                if message == "Player 1 Wins!" or message == "Player 2 Wins!" or "disconnected" in message:
                    return
                if message == "Wait for your turn":
                    message2 = self.client_socket.recv(1024).decode()
                    print(message2)
                    if message2 == "Player 1 Wins!" or message2 == "Player 2 Wins!" or "disconnected" in message2:
                        return
                    message3 = self.client_socket.recv(1024).decode()
                    print(message3)
                
                board = self.client_socket.recv(1024).decode()
                print(board)
                if board == "Player 1 Wins!" or board == "Player 2 Wins!" or "disconnected" in board:
                    return
                
                while True:
                    tcflush(sys.stdin, TCIFLUSH)
                    move = input("Enter your move (x,y): ")
                    print(move)
                    if move != "":
                        break
                self.client_socket.send(move.encode())
                response = self.client_socket.recv(1024).decode()
                print(response)
                if response == "Player 1 Wins!" or response == "Player 2 Wins!" or "disconnected" in response:
                    return
            except KeyboardInterrupt:
                print("Game ended.")
                break

if __name__ == "__main__":
    client = BattleshipClient()
    client.setup()