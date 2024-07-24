import socket
import time

class TicTacToeGame:
    def __init__(self):
        self.board = [[" " for _ in range(3)] for _ in range(3)]
        self.current_player = "X"
        self.players = []

    def send_board(self, conn):
        board_str = "CURRENT BOARD\n"
        for row in self.board:
            formatted_row = " | ".join(cell if cell != " " else "_" for cell in row)
            board_str += f"| {formatted_row} |\n"
        board_str += "  0   1   2  \n"
        conn.sendall(board_str.encode())


    def check_win(self):
        for i in range(3):
            if all(self.board[i][j] == self.current_player for j in range(3)) or all(self.board[j][i] == self.current_player for j in range(3)):
                return True
        if all(self.board[i][i] == self.current_player for i in range(3)) or all(self.board[i][2 - i] == self.current_player for i in range(3)):
            return True
        return False

    def make_move(self, row, col):
        if 0 <= row < 3 and 0 <= col < 3 and self.board[row][col] == " ":
            self.board[row][col] = self.current_player
            return True
        return False

    def switch_player(self):
        self.current_player = "O" if self.current_player == "X" else "X"


class TicTacToeServer:
    def __init__(self, server_socket, players):
        self.host = "149.43.80.29"
        self.port = 5000
        self.server_socket = server_socket
        self.players = players

    def play_game(self, conn1, conn2):
        game = TicTacToeGame()
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
                    current_conn.sendall("Enter your move (row,col): ".encode())
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
                    row, col = map(int, move.split(','))
                    if game.make_move(row, col):
                        valid_move = True
                    else:
                        current_conn.sendall("Invalid move. Please try again.\n".encode())
                except ValueError:
                    current_conn.sendall("Invalid input. Please enter row and column numbers separated by a comma.\n".encode())

            if game.check_win():
                game.send_board(current_conn)
                game.send_board(waiting_conn)
                winning_message = "Congratulations! You won!\n"
                current_conn.sendall(winning_message.encode())
                waiting_conn.sendall("Sorry, you lost!\n".encode())
                break

            if all(cell != " " for row in game.board for cell in row):
                for conn in (conn1, conn2):
                    conn.sendall("Tie game!\n".encode())
                break

            game.switch_player()