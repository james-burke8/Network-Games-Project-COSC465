import socket
import threading
import time

class BattleshipGame:
    def __init__(self):
        self.board_size = 10
        self.p1board = [['~' for _ in range(self.board_size)] for _ in range(self.board_size)]
        self.p1OppBoard = [['~' for _ in range(self.board_size)] for _ in range(self.board_size)]
        self.p2board = [['~' for _ in range(self.board_size)] for _ in range(self.board_size)]
        self.p2OppBoard = [['~' for _ in range(self.board_size)] for _ in range(self.board_size)]
        self.p1ships = []
        self.p2ships = []
        self.guessedp1 = set()
        self.guessedp2 = set()

    #places ship at provided coordinate
    def place_ship(self, player, x, y):
        if player == 1:
            if (x, y) in self.p1ships:
                return False
            if x > self.board_size or y > self.board_size:
                return False
            self.p1ships.append((x, y))
            return True
        else:
            if (x, y) in self.p2ships:
                return False
            if x > self.board_size or y > self.board_size:
                return False
            self.p2ships.append((x, y))
            return True

    #checks if hit or miss
    def check_hit(self, x, y, player):
        player = 1 - player
        if player == 1:
            if (x, y) in self.p2ships:
                self.p1OppBoard[x][y] = "X"
                self.guessedp1.add((x,y))
                return True
            else:
                self.p1OppBoard[x][y] = "O"
                return False
        if player == 0:
            if (x, y) in self.p1ships:
                self.p2OppBoard[x][y] = "X"
                self.guessedp2.add((x,y))
                return True
            else:
                self.p2OppBoard[x][y] = "O"
                return False

class BattleshipServer:
    def __init__(self, client_sock, players):
        self.host = "149.43.80.29"
        self.port = 5587
        self.server_socket = client_sock
        self.players = players
        self.socket_error = False

    def start(self):
        self.server_socket.bind((self.host, self.port))
        self.server_socket.listen()

        print("Server is listening...")

        while len(self.players) < 2:
            client_socket, _ = self.server_socket.accept()
            print("Connection established with player", len(self.players) + 1)
            self.players.append(client_socket)

        self.server_socket.close()
        self.setup_game()

    #sets up boards for players
    def setup_game(self):
        game = BattleshipGame()
        print("Starting Game...")
        self.setup_board(self.players[0], game, 1)
        self.setup_board(self.players[1], game, 2)
        if self.socket_error:
            return
        print("Boards Created")
        while True:
            for i, client_socket in enumerate(self.players):
                opponent_socket = self.players[1 - i]
                num1 = 5 - len(game.guessedp1) 
                num2 = 5 - len(game.guessedp2)
                time.sleep(1)
                if i == 0:
                    string = "Sink the other players ships (" + str(num1) + "):"
                else:
                    string = "Sink the other players ships (" + str(num2) + "):"
                try:
                    client_socket.send(string.encode())
                except socket.error:
                    s = "Player " + str(i + 1) + " disconnected unexpectedly. Game Over!"
                    print(s)
                    opponent_socket.send(s.encode())
                    self.cleanup()
                    return
                string2 = "Wait for your turn"
                opponent_socket.send(string2.encode())
                time.sleep(1)
                board = self.format_board(i + 1, game)
                client_socket.send(board.encode())
                try:
                    data = client_socket.recv(1024).decode()
                    if not data:
                        s = "Player " + str(i + 1) + " disconnected unexpectedly. Game Over!"
                        print(s)
                        opponent_socket.send(s.encode())
                        self.cleanup()
                        return
                    x, y = map(int, data.split(","))
                    if game.check_hit(x, y, i):
                        response = "Hit!"
                    else:
                        response = "Miss!"
                    if len(game.guessedp1) > 4:
                        response = "Player 1 Wins!"
                        client_socket.send(response.encode())
                        opponent_socket.send(response.encode())
                        print("Game Over, Player 1 Wins!")
                        self.cleanup()
                        return
                    if len(game.guessedp2) > 4:
                        response = "Player 2 Wins!"
                        client_socket.send(response.encode())
                        opponent_socket.send(response.encode())
                        print("Game Over, Player 2 Wins!")
                        self.cleanup()
                        return
                    time.sleep(1)
                    client_socket.send(response.encode())
                    response = "Opponent " + response
                    opponent_socket.send(response.encode())
                    time.sleep(1)
                except ValueError:
                    client_socket.send("Invalid input. Use format 'x,y'. You lost your turn!".encode())
                    opponent_socket.send("Opponent entered an invalid move and lost their turn!".encode())
                    continue

    def setup_board(self, client_socket, game, player):
        if self.socket_error:
            return
        print("Getting ships from player " + str(player))
        try:
            client_socket.send("Place your ships. (5  remaining) Enter ship coordinates as 'x,y' (e.g., '0,0').".encode())
        except socket.error:
                    s = "Player " + str(player) + " disconnected unexpectedly. Game Over!"
                    print(s)
                    try:
                        self.players[player-1].send(s.encode())
                    except socket.error:
                        print("")
                    self.cleanup()
                    self.socket_error = True
                    return
        num = 4
        while num >= 0:
            try:
                data = client_socket.recv(1024).decode()
                if not data:
                    s = "Player " + str(player) + " disconnected unexpectedly. Game Over!"
                    print(s)
                    try:
                        self.players[player-1].send(s.encode())
                    except socket.error:
                        print("")
                    self.cleanup()
                    self.socket_error = True
                    return
                x, y = map(int, data.split(","))
                if not game.place_ship(player, x, y):
                    client_socket.send("Invalid placement. Try again.".encode())
                    continue
            except ValueError:
                client_socket.send("Invalid input. Use format 'x,y'.".encode())
                continue
            string = "Ship placed successfully. " + str(num) + " remaining"
            client_socket.send(string.encode())
            num -= 1

    def format_board(self, player, game):
        if player == 1:
            board = '\n'.join([' '.join(row) for row in game.p1OppBoard])
        else:
            board = '\n'.join([' '.join(row) for row in game.p2OppBoard])
        return board
    
    def cleanup(self):
        for client_socket in self.players:
            client_socket.close()

if __name__ == "__main__":
    server = BattleshipServer()
    server.start()