
import sys
from termios import TCIFLUSH, tcflush

class hangpersonClient:
    def __init__(self, client_sock):
        self.host = "149.43.80.29"
        self.port = 5000
        self.client_socket = client_sock

    def connect(self):
        try:
            self.client_socket.connect((self.host, self.port))
            print("Connected to the Tic Tac Toe server.")
            return True
        except Exception as e:
            print(f"Unable to connect to the server: {e}")
            return False

    def play(self):
        try:
            while True:
                message = self.client_socket.recv(1024).decode()
                print(message)
                if "disconnected" in message:
                    return
                if "Enter your guess" in message or "Enter your word" in message:
                    while True:
                        tcflush(sys.stdin, TCIFLUSH)
                        move = input("")
                        if move != "":
                            break
                    self.client_socket.send(move.encode())
                elif "Congratulations" in message or "Sorry" in message or "Other" in message:
                    print("Game Over.")
                    break
        except KeyboardInterrupt:
            print("Disconnected from the server.")
        finally:
            self.client_socket.close()
            print("Connection closed.")

if __name__ == "__main__":
    client = hangpersonClient()
    if client.connect():
        client.play()