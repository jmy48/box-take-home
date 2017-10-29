import game

class Player:
	def __init__(self, lower_or_upper, droppable_pieces=[], in_check_initialized=False):
		self.droppable = droppable_pieces
		self.in_check = in_check_initialized
		self.pieces_on_board = {}
		self.id = lower_or_upper
		self.opponent = None