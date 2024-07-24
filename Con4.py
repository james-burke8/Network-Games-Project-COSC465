import socket
import time

class ConnectFourGame:
    def __init__(self):
        self.rows = 6
        self.cols = 7
        self.board = [[' ' for _ in range(self.cols)] for _ in range(self.rows)]
        self.current_player = 'X'

    def send_board(self, conn):
        full_board = "Current Board:\n"
        for row in self.board:
            formatted_row = " | ".join(row)
            full_board += f"| {formatted_row} |\n"
        full_board += "  0   1   2   3   4   5   6  \n"
        
        conn.sendall(full_board.encode())

    def check_win(self):
        directions = [(0, 1), (1, 0), (1, 1), (1, -1)]
        for x in range(self.rows):
            for y in range(self.cols):
                if self.board[x][y] == self.current_player:
                    for dx, dy in directions:
                        count = 1
                        for step in range(1, 4):
                            nx, ny = x + dx * step, y + dy * step
                            if 0 <= nx < self.rows and 0 <= ny < self.cols and self.board[nx][ny] == self.current_player:
                                count += 1
                            else:
                                break
                        if count == 4:
                            return True
        return False

    def make_move(self, col):
        if 0 <= col < self.cols and self.board[0][col] == ' ':
            for r in range(self.rows-1, -1, -1):
                if self.board[r][col] == ' ':
                    self.board[r][col] = self.current_player
                    return True
        return False

    def switch_player(self):
        self.current_player = 'O' if self.current_player == 'X' else 'X'

class ConnectFourServer:
    def __init__(self, server_sock, players):
        self.host = "149.43.80.29"
        self.port = 5000
        self.server_socket = server_sock
        self.players = players

    def play_game(self, conn1, conn2):
        game = ConnectFourGame()

        try:
            conn1.sendall("You are Xs\n".encode())
        except socket.error:
            conn2.sendall("Player 1 disconnected, closing connection...")
            print("Connection error, closing game...")
            return
        try:
            conn2.sendall("You are Os\n".encode())
        except socket.error:
            conn1.sendall("Player 2 disconnected, closing connection...")
            print("Connection error, closing game...")
            return

        while True:
            for conn in (conn1, conn2):
                game.send_board(conn)

            current_conn = conn1 if game.current_player == 'X' else conn2
            waiting_conn = conn2 if current_conn == conn1 else conn1

            try:
                current_conn.sendall("Your turn...\n".encode())
            except socket.error:
                s = "Opponent disconnected, closing connection..."
                waiting_conn.sendall(s.encode())
                print("Connection error, closing game...")
                return
            try:
                time.sleep(1)
                waiting_conn.sendall("Waiting for other player...\n".encode())
            except socket.error:
                s = "Opponent disconnected, closing connection..."
                current_conn.sendall(s.encode())
                print("Connection error, closing game...")
                return

            valid_move = False
            while not valid_move:
                try:
                    current_conn.sendall("Enter your move (col): ".encode())
                except socket.error:
                    s = "Opponent disconnected, closing connection..."
                    waiting_conn.sendall(s.encode())
                    print("Connection error, closing game...")
                    return
                move = current_conn.recv(1024).decode().strip()
                if not move:
                    s = "Opponent disconnected, closing connection..."
                    waiting_conn.sendall(s.encode())
                    print("Connection error, closing game...")
                    return
                try:
                    col = int(move)
                    if game.make_move(col):
                        valid_move = True
                    else:
                        current_conn.sendall("Invalid move. Please try again.\n".encode())
                except ValueError:
                    current_conn.sendall("Invalid input. Please enter a column number.\n".encode())

            if game.check_win():
                game.send_board(current_conn)
                game.send_board(waiting_conn)
                winning_message = "Congratulations! You won!\n"
                current_conn.sendall(winning_message.encode())
                waiting_conn.sendall("Sorry, you lost!\n".encode())
                break

            if all(cell != ' ' for row in game.board for cell in row):
                for conn in (conn1, conn2):
                    conn.sendall("Tie game!\n".encode())
                break

            game.switch_player()
