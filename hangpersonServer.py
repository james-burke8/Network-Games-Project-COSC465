import socket
import time

# player class for each player 
class player:
    def __init__(self):
        self.guesses = set()
        self.word = ""
        self.opp_guess = ""
        self.person = 0

class hangpersonGame:
    def __init__(self, p1, p2):
        self.current_player = 0
        self.players = [p1, p2]

    # send game info to a given player
    def send_state(self, conn, player):
        current = self.players[player]
        state_str = "Opponent's Progress: \n" + ' '.join(current.opp_guess) + "\n"
        state_str += "\nYour Hangperson: " + hangpeople.people[current.person] + "\n"
        state_str += "\nWord: " + ' '.join(self.players[1 - player].opp_guess)
        state_str += "\nGuesses: " + str(list(current.guesses)) + "\n"
        conn.sendall(state_str.encode())

    # check to see if guess has been completed 
    def check_win(self, player):
        check = self.players[1 - player]
        if check.word == check.opp_guess:
            return True
        return False

    # check to see if hangperson is "hung"
    def check_loss(self, player):
        # check if hangperson is at max 
        if self.players[player].person == 6: 
            return True
        return False

    # check if an inputted guess is valid, if it is, update guess
    def make_move(self, move, player):
        # return true if a move is valid 
        current = self.players[player]
        opp = self.players[1 - player]
        move = move.lower()
        if move.isalpha() and len(move) == 1 and move not in current.guesses:
            # update guesses
            current.guesses.add(move)
            if move in opp.word:
                opp.opp_guess = self.update_guess(move, opp.opp_guess, opp.word)
                # if guess is in word, update guess progress in opponent 
            else:
                current.person += 1
            return True
        return False

    # update the guess variable by replacing underscores with guess when applicable
    def update_guess(self, move, opp_guess, word):
        word_arr = list(word)
        guess_arr = list(opp_guess)
        idx = 0
        for letter in word_arr:
            if letter == move:
                guess_arr[idx] = move
            idx += 1
        return ''.join(guess_arr)

    # check if an inputted word is valid, if it is, update player's word
    def check_word(self, word, player): 
        if word.isalpha() and len(word) > 1:
            self.players[player].word = word.lower()
            self.players[player].opp_guess = ''.join('_' for _ in word)
            return True
        return False

    # switch current player
    def switch_player(self):
        self.current_player = 0 if self.current_player == 1 else 1

class hangpersonServer:

    def __init__(self, server_socket, players):
        self.host = "149.43.80.29"
        self.port = 5000
        self.server_socket = server_socket
        self.players = players
        self.player1 = player()
        self.player2 = player()

    def play_game(self, conn1, conn2):
        game = hangpersonGame(self.player1, self.player2)

        # Check connections
        try:
            conn1.sendall("You are P1\n".encode())
        except socket.error:
            conn2.sendall("Player 1 disconnected, closing connection...")
            print("Connection error, closing game...")
            return
        try:
            conn2.sendall("You are P2\n".encode())
        except socket.error:
            conn1.sendall("Player 2 disconnected, closing connection...")
            print("Connection error, closing game...")
            return

        # game loop, exits when end condition is met
        words_in = 0
        while True:
            player = game.current_player
                
            current_conn = conn1 if game.current_player == 0 else conn2
            waiting_conn = conn2 if current_conn == conn1 else conn1

            game.send_state(current_conn, player)

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
            
            # if players have not entered words
            if words_in < 2:
                valid_word = False
                while not valid_word:
                    try:
                        current_conn.sendall("Enter your word: ".encode())
                    except socket.error:
                        s = "Opponent disconnected, closing connection..."
                        waiting_conn.sendall(s.encode())
                        print("Connection error, closing game...")
                        return
                    word = current_conn.recv(1024).decode().strip()
                    if not word:
                        s = "Opponent disconnected, closing connection..."
                        waiting_conn.sendall(s.encode())
                        print("Connection error, closing game...")
                        return
                    try:
                        if game.check_word(word, player):
                            valid_word = True
                            words_in += 1
                        else:
                            current_conn.sendall("Invalid move. Please try again.\n".encode())
                    except ValueError:
                        current_conn.sendall("Invalid input. Please enter a word consisting of alphabetic characters greater than length 1\n".encode())
            else:
                # players have entered words
                valid_move = False
                while not valid_move:
                    try:
                        current_conn.sendall("Enter your guess: ".encode())
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
                        if game.make_move(move, player):
                            valid_move = True
                        else:
                            current_conn.sendall("Invalid move. Please try again.\n".encode())
                    except ValueError:
                        current_conn.sendall("Invalid input. Please enter a single letter.\n".encode())

                # check if loss condition is met 
                if game.check_loss(player):
                    current_conn.sendall("\nSorry, you lost!\n".encode())
                    waiting_conn.sendall("\nOther player lost!\n".encode())
                    break

                # check if win condition is met
                if game.check_win(player):
                    game.send_state(current_conn, player)
                    game.send_state(waiting_conn, 1 - player)
                    winning_message = "Congratulations! You won!\n"
                    current_conn.sendall(winning_message.encode())
                    waiting_conn.sendall("Sorry, you lost!\n".encode())
                    break

            game.switch_player()

# class for storing the hangpeople images 
class hangpeople:
    people = ['''
  +---+
  |   |
      |
      |
      |
      |
=========''', '''
  +---+
  |   |
  O   |
      |
      |
      |
=========''', '''
  +---+
  |   |
  O   |
  |   |
      |
      |
=========''', '''
  +---+
  |   |
  O   |
 /|   |
      |
      |
=========''', '''
  +---+
  |   |
  O   |
 /|\  |
      |
      |
=========''', '''
  +---+
  |   |
  O   |
 /|\  |
 /    |
      |
=========''', '''
  +---+
  |   |
  O   |
 /|\  |
 / \  |
      |
=========''']
