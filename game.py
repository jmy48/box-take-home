import player
import board
import constants
import utils

class Game:
	#if current_player = 0 then it's player one's turn, otherwise it's player two's turn
	def __init__(self, input_board=board.Board(),
				player1_start=player.Player(0, droppable_pieces = []),
				player2_start=player.Player(1, droppable_pieces = []),
				current_player=0, current_command=None, promotion=False):

		self.board = input_board

		#convention that player1 refers to undercase pieces
		self.player1 = player1_start

		self.player2 = player2_start

		self.turns = 0

		self.current_player = current_player

		self.command = current_command

		self.promote = promotion

		self.initialize_players()

	def initialize_players(self):
		for i in xrange(constants.BOARD_WIDTH):
			for j in xrange(constants.BOARD_HEIGHT):
				ch = self.board.board_matrix[i][j]
				if ch != "__":
					if str.isupper(ch):
						self.player2.pieces_on_board[str.lower(ch)] = (i, j)
					else:
						self.player1.pieces_on_board[ch] = (i, j)
		self.player1.opponent = self.player2
		self.player2.opponent = self.player1

	#reason: "disqualified", or "checkmated" or "tie"
	def win(self, player_id, reason):
		current_lower_or_upper = "lower" if self.current_player == 0 else "UPPER"
		lower_or_upper = "lower" if player_id == 0 else "UPPER"

		print current_lower_or_upper + " player action: " + self.command

		print utils.stringifyBoard(self.board.board_matrix)
		print "Captures UPPER: " + " ".join([str.upper(x) for x in self.player2.droppable])
		print "Captures lower: " + " ".join(self.player1.droppable) + "\n"

		if reason == "disqualified":
			print lower_or_upper + " player wins.  Illegal move."

		elif reason == "checkmated":
			print lower_or_upper + " player wins.  Checkmate."
		elif reason == "tie":
			print "Tie game.  Too many moves."

		exit(0)

	def id_to_player(self, player_id):
		if player_id == 0:
			return self.player1
		elif player_id == 1:
			return self.player2

	def move(self, begin_square, end_square):
		i, j = begin_square
		x, y = end_square
		player = self.id_to_player(self.current_player)

		#check if not moving right player's piece, or if trying to move "__"
		if (str.islower(self.board.board_matrix[i][j]) != bool(1 - self.current_player)
			or self.board.board_matrix[i][j] == "__"):
			self.win(1 - self.current_player, "disqualified")

		legal_moves = self.board.get_legal_moves(begin_square)

		#check if making an illegal move based on piece movement
		if end_square not in legal_moves:
			self.win(1 - self.current_player, "disqualified")

		#check for promotion legality
		temp = self.board.board_matrix[x][y]
		self.board.board_matrix[x][y] = self.board.board_matrix[i][j]
		if self.promote and not self.board.can_promote(player, begin_square, end_square):
			self.board.board_matrix[x][y] = temp
			self.win(1 - self.current_player, "disqualified")
		self.board.board_matrix[x][y] = temp

		if (str.lower(self.board.board_matrix[i][j]) == "g" 
			or str.lower(self.board.board_matrix[i][j]) == "k") and self.promote:
			self.win(1 - self.current_player, "disqualified")			

		#check if making the move would result in a board state that is in check for self
		if self.board.check_check_move(player, begin_square, end_square, self.promote):
			self.win(1 - self.current_player, "disqualified")

		#If code gets to this point, the move is legal.

		player.in_check = False

		#check if making the move would result in a board state that is in_check for opponent
		if self.board.check_check_move(player.opponent, begin_square, end_square, self.promote):
			player.opponent.in_check = True

		#now actually make the move
		self.board.make_move(player, begin_square, end_square, self.promote)

		#check for checkmate
		moves, drops = self.board.find_all_moves_and_drops_no_check(player.opponent)

		if not moves and not drops and player.opponent.in_check:
			self.win(self.current_player, "checkmated")

		self.turns += 1

		if self.turns == 400:
			self.win(self.current_player, "tie")

		self.current_player = 1 - self.current_player

	def drop(self, square, piece):
		i, j = square
		player = self.id_to_player(self.current_player)

		#if this drop is in the list of all legal drops
		if not ((square, piece) in self.board.find_all_legal_drops(player)):
			self.win(1 - self.current_player, "disqualified")

		if self.board.check_check_drop(player, square, piece, player):
			self.win(1 - self.current_player, "disqualified")

		#If code gets to this point, the move is legal.

		player.in_check = False

		#check if making the move would result in a board state that is in_check for opponent
		if self.board.check_check_drop(player.opponent, square, piece, player):
			player.opponent.in_check = True

		#now actually make the drop
		self.board.make_drop(player, square, piece)

		#check for checkmate
		moves, drops = self.board.find_all_moves_and_drops_no_check(player.opponent)
		if not moves and not drops:
			self.win(self.current_player, "checkmated")

		self.turns += 1

		if self.turns == 400:
			self.win(self.current_player, "tie")

		self.current_player = 1 - self.current_player