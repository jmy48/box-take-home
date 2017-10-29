import constants
#contains all piece movement logic, check/checkmating logic.

class Board:
	def __init__(self, input_board=[["k","p","__","__","R"],
									["g","__","__","__","B"],
									["s","__","__","__","S"],
									["b","__","__","__","G"],
									["r","__","__","P","K"]]):
		"""
		The board is a:
		List[List[String]]
		"""
		self.board_matrix = input_board

	def get_legal_moves_king(self, i, j, lower):
		res = []
		for x in xrange(i - 1, i + 2):
			for y in xrange(j - 1, j + 2):
				if (-1 < x < constants.BOARD_WIDTH and #in range
					-1 < y < constants.BOARD_HEIGHT and
					(self.board_matrix[x][y] == '__' or #empty space
					(str.islower(self.board_matrix[x][y]) #encounters an enemy piece
					!= lower))):
					res.append((x,y))
		return res

	def get_legal_moves_rook(self, i, j, lower):
		res = []
		for x in xrange(1, constants.BOARD_WIDTH - i): #traverse right until encounters piece
			if self.board_matrix[i + x][j] != '__':
				if lower != str.islower(self.board_matrix[i + x][j]): # if enemy, still a valid move
					res.append((i + x, j))
				break
			res.append((i + x, j))

		for x in xrange(1, i + 1): #traverse left
			if self.board_matrix[i - x][j] != '__':
				if lower != str.islower(self.board_matrix[i - x][j]):
					res.append((i - x, j))
				break
			res.append((i - x, j))

		for y in xrange(1, constants.BOARD_HEIGHT - j): #traverse up
			if self.board_matrix[i][j + y] != '__':
				if lower != str.islower(self.board_matrix[i][j + y]):
					res.append((i, j + y))
				break
			res.append((i ,j + y))

		for y in xrange(1, j + 1): #traverse down
			if self.board_matrix[i][j - y] != '__':
				if lower != str.islower(self.board_matrix[i][j - y]):
					res.append((i, j - y))
				break
			res.append((i, j - y))

		return res

	def get_legal_moves_bishop(self, i, j, lower):
		res = []
		for x in xrange(1, min(constants.BOARD_WIDTH - i, constants.BOARD_HEIGHT - j)): #traverse top-right until encounters piece
			if self.board_matrix[i + x][j + x] != '__':
				if lower != str.islower(self.board_matrix[i + x][j + x]): # if enemy, still a valid move
					res.append((i + x, j + x))
				break
			res.append((i + x, j + x))

		for x in xrange(1, min(i + 1, constants.BOARD_HEIGHT - j)): #traverse top-left
			if self.board_matrix[i - x][j + x] != '__':
				if lower != str.islower(self.board_matrix[i - x][j + x]):
					res.append((i - x, j + x))
				break
			res.append((i - x, j + x))

		for y in xrange(1, min(constants.BOARD_WIDTH - i, j + 1)): #traverse bottom-right
			if self.board_matrix[i + y][j - y] != '__':
				if lower != str.islower(self.board_matrix[i + y][j - y]):
					res.append((i + y, j - y))
				break
			res.append((i + y, j - y))

		for y in xrange(1, min(i + 1, j + 1)): #traverse bottom-left
			if self.board_matrix[i - y][j - y] != '__':
				if lower != str.islower(self.board_matrix[i - y][j - y]):
					res.append((i - y, j - y))
				break
			res.append((i - y, j - y))

		return res

	#similar to king movement, except for bottom-left/right
	def get_legal_moves_gold(self, i, j, lower):
		up_or_down = -1 if lower else 1

		return [(x, y) for x, y in self.get_legal_moves_king(i, j, lower) if not 
				(((x, y) == (i - 1, j + up_or_down)) or ((x, y) == (i + 1, j + up_or_down)))]

	def get_legal_moves_silver(self, i, j, lower):
		up_or_down = -1 if lower else 1

		return [(x, y) for x, y in self.get_legal_moves_king(i, j, lower) if not 
				(((x, y) == (i + 1, j)) or ((x, y) == (i - 1, j)) or ((x, y) == (i, j + up_or_down)))]

	def get_legal_moves_pawn(self, i, j, lower):

		up_or_down = 1 if lower else -1

		if (0 < j + up_or_down >= constants.BOARD_HEIGHT or
			(self.board_matrix[i][j + up_or_down] != "__" and
			str.islower(self.board_matrix[i][j + up_or_down]) == lower)):
			return []
		else:
			return [(i, j + up_or_down)]

	def get_legal_moves(self, square):
		i, j = square
		ch = self.board_matrix[i][j]
		lower = str.islower(ch)
		ch = ch.lower()

		return {
			"k": self.get_legal_moves_king(i, j, lower),
			"r": self.get_legal_moves_rook(i, j, lower),
			"b": self.get_legal_moves_bishop(i, j, lower),
			"g": self.get_legal_moves_gold(i, j, lower),
			"s": self.get_legal_moves_silver(i, j, lower),
			"p": self.get_legal_moves_pawn(i, j, lower),
			"+s": self.get_legal_moves_gold(i, j, lower),
			"+b": self.get_legal_moves_bishop(i, j, lower) + self.get_legal_moves_king(i, j, lower),
			"+r": self.get_legal_moves_rook(i, j, lower) + self.get_legal_moves_king(i, j, lower),
			"+p": self.get_legal_moves_gold(i, j, lower)
		}[ch]

	def promote(self, player, piece):
		i, j = player.pieces_on_board[piece]
		self.board_matrix[i][j] = "+" + piece
		player.pieces_on_board["+" + piece] = player.pieces_on_board.pop(piece)

	def unpromote(self, player, piece):
		if piece[0] == '+':
			i, j = player.pieces_on_board[piece]
			self.board_matrix[i][j] = piece[1:]
			player.pieces_on_board[piece[1:]] = player.pieces_on_board.pop(piece)

	def can_promote(self, player, begin, end):
		x, y = end
		i, j = begin

		return (player.id == 0 and (y == constants.BOARD_HEIGHT-1 or j == constants.BOARD_HEIGHT-1) or
				player.id == 1 and (j == 0 or y == 0)) and self.board_matrix[i][j][0] != "+"

	# deep: if copy is false, it changes the board state, else, it returns a new deep copy
	def make_move(self, player, begin_square, end_square, promote, copy = False):
		i, j = begin_square
		x, y = end_square

		begin = self.board_matrix[i][j]
		end = self.board_matrix[x][y]

		if copy:
			m = [row[:] for row in self.board_matrix]
			captured_piece = None
			if m[x][y] != "__":
				captured_piece = m[x][y]
			m[x][y] = m[i][j]
			m[i][j] = "__"
			return m, captured_piece
		else:
			if end != "__":

				self.unpromote(player.opponent, str.lower(self.board_matrix[x][y]))

				player.opponent.pieces_on_board.pop(str.lower(self.board_matrix[x][y]))

				player.droppable.append(str.lower(self.board_matrix[x][y]))

			player.pieces_on_board[str.lower(begin)] = (x,y)

			self.board_matrix[x][y] = begin
			self.board_matrix[i][j] = "__"

			#Check for forced pawn promotion
			forced = str.lower(begin) == "p" and (str.islower(begin) and y == constants.BOARD_HEIGHT-1 or
				str.isupper(begin) and y == 0)

			if promote and self.can_promote(player, begin_square, end_square) or forced:
				self.promote(player, str.lower(self.board_matrix[x][y]))

			if player.id == 0:
				self.board_matrix[x][y] = str.lower(self.board_matrix[x][y])
			elif player.id == 1:
				self.board_matrix[x][y] = str.upper(self.board_matrix[x][y])


	#returns a list of all legal moves of a player. 
	def find_all_legal_moves(self, player):
		res = []
		for k,v in player.pieces_on_board.iteritems():
			for end in self.get_legal_moves(v):
				res.append((v, end))
		return res

	def make_drop(self, player, drop_position, piece, copy = False):
		i, j = drop_position

		if copy:
			y = [row[:] for row in self.board_matrix]
			y[i][j] = piece
			return y
		else:
			self.board_matrix[i][j] = piece if player.id == 0 else str.upper(piece)
			player.droppable.remove(piece)

			player.pieces_on_board[piece] = (i, j)

	def find_all_legal_drops(self, player):
		res = []

		for i in xrange(constants.BOARD_WIDTH):
			for j in xrange(constants.BOARD_HEIGHT):

				if self.board_matrix[i][j] != "__":
					continue

				for piece in player.droppable:
					if piece == "p":
						if (j == constants.BOARD_HEIGHT-1 and player.id == 0 or
							j == 0 and player.id == 1):
							continue

						m = self.make_drop(player, (i, j), piece, copy = True)

						pop = player.pieces_on_board.get(piece, None)
						player.pieces_on_board[piece] = (i, j)


						temp = self.board_matrix
						self.board_matrix = m

						moves = self.find_all_moves_no_check(player.opponent)

						self.board_matrix = temp

						player.pieces_on_board.pop(piece)

						if pop is not None:
							player.pieces_on_board[piece] = pop


						if not moves and self.check_check_drop(player.opponent, (i, j), piece, player):
							continue

						has_pawn_in_column = False
						for column_entry in xrange(constants.BOARD_HEIGHT):
							ch = self.board_matrix[i][column_entry]
							if (ch == "p" and player.id == 0 or
								ch == "P" and player.id == 1):
								has_pawn_in_column = True
						if has_pawn_in_column:
							continue
					res.append(((i, j), piece))
		return res

	#check if making the move would result in check for player
	#player: the player object
	def check_check_move(self, player, begin_square, end_square, promote):
		i, j = begin_square
		x, y = end_square

		if str.islower(self.board_matrix[i][j]):
			player_who_moved = player if player.id == 0 else player.opponent
		else:
			player_who_moved = player if player.id == 1 else player.opponent

		m, captured_piece = self.make_move(player_who_moved, begin_square, end_square, promote, copy = True)

		if captured_piece is not None:
			pop = player_who_moved.opponent.pieces_on_board.pop(str.lower(captured_piece), None)
			player_who_moved.droppable.append(str.lower(self.board_matrix[x][y]))

		player_who_moved.pieces_on_board[str.lower(self.board_matrix[i][j])] = (x,y)	

		temp = self.board_matrix
		self.board_matrix = m

		if promote and self.can_promote(player_who_moved, begin_square, end_square):
			self.promote(player_who_moved, str.lower(self.board_matrix[x][y]))

		king_position = player.pieces_on_board['k']

		check = king_position in [z[1] for z in self.find_all_legal_moves(player.opponent)]

		#restore captured piece (this function is for a hypothetical move, not a real move)
		if captured_piece is not None:
			player_who_moved.opponent.pieces_on_board[str.lower(captured_piece)] = pop
			player_who_moved.droppable.pop()

		self.board_matrix = temp

		player_who_moved.pieces_on_board[str.lower(self.board_matrix[i][j])] = (i, j)

		if promote and self.can_promote(player_who_moved, begin_square, end_square):
			self.unpromote(player_who_moved, str.lower(self.board_matrix[i][j]))

		return check

	def check_check_drop(self, player, square, piece, moving_player):
		i, j = square

		player_who_moved = moving_player

		m = self.make_drop(player_who_moved, square, piece, copy = True)

		pop = player_who_moved.pieces_on_board.get(piece, None)
		player_who_moved.pieces_on_board[piece] = (i, j)

		temp = self.board_matrix
		self.board_matrix = m

		king_position = player.pieces_on_board['k']

		check = king_position in [x[1] for x in self.find_all_legal_moves(player.opponent)]

		#restore original state (this function is for a hypothetical move, not a real move)
		player_who_moved.pieces_on_board.pop(piece)
		if pop is not None:
			player_who_moved.pieces_on_board[piece] = pop
		self.board_matrix = temp

		return check		

	#for checking for checkmate, and for printing out legal moves during a check
	def find_all_moves_and_drops_no_check(self, player):
		#find all legal moves/drops for player, and check_check.
		#slow runtime but requires less overhead

		moves = []
		drops = []

		for move in self.find_all_legal_moves(player):

			begin_square, end_square = move
			if not self.check_check_move(player, begin_square, end_square, False):
				moves.append(move)

		for drop in self.find_all_legal_drops(player):
			drop_position, piece = drop
			if not self.check_check_drop(player, drop_position, piece, player):
				drops.append(drop)

		return moves, drops


	def find_all_moves_no_check(self, player):

		moves = []

		for move in self.find_all_legal_moves(player):
			begin_square, end_square = move
			if not self.check_check_move(player, begin_square, end_square, False):
				moves.append(move)

		return moves