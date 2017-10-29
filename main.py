import sys
import board
import game
import utils
import player
import constants

#starts the game
def main():

	if sys.argv[1] == "-i":
		repl(game.Game())

	elif sys.argv[1] == "-f":
		filemode()
	else:
		print "Invalid arguments. Please use arguments -i or -f <filename>"

def filemode():
	filename = sys.argv[2]
	d = utils.parseTestCase(filename)

	initial_board = [["__" for _ in xrange(constants.BOARD_WIDTH)] for _ in xrange(constants.BOARD_HEIGHT)]
	for piece in d["initialPieces"]:
		x, y = notation_to_coordinates(piece["position"])
		initial_board[x][y] = piece["piece"]

	p1 = player.Player(0, droppable_pieces = d["lowerCaptures"])
	p2 = player.Player(1, droppable_pieces = [str.lower(x) for x in d["upperCaptures"]])

	g = game.Game(input_board=board.Board(initial_board), player1_start=p1, player2_start=p2)

	for move in d["moves"]:

		g.command = move
		tokens = move.split(' ')

		if tokens[0] == "move":
			if len(tokens) > 3 and tokens[3] == "promote":
				g.promote = True
			g.move(notation_to_coordinates(tokens[1]), notation_to_coordinates(tokens[2]))

			g.promote = False

		elif tokens[0] == "drop":
			square, piece = notation_to_drop(tokens[1], tokens[2])
			g.drop(square, piece)

	lower_or_upper = "lower" if g.current_player == 1 else "UPPER"
	if g.command is not None:
		print lower_or_upper + " player action: " + g.command
	print_game(g)

def repl(game):
	print_game(game)
	user_in = raw_input()
	tokens = user_in.split(' ')

	game.command = user_in

	if tokens[0] == "move":
		if len(tokens) > 3 and tokens[3] == "promote":
			game.promote = True

		game.move(notation_to_coordinates(tokens[1]), notation_to_coordinates(tokens[2]))

		game.promote = False

	elif tokens[0] == "drop":
		square, piece = notation_to_drop(tokens[1], tokens[2])
		game.drop(square, piece)


	lower_or_upper = "lower" if game.current_player == 1 else "UPPER"
	
	if game.command is not None:
		print lower_or_upper + " player action: " + game.command

	repl(game)

def notation_to_coordinates(notation):
	"""
	type notation: String
	rtype: (Int, Int)
	"""
	return ord(notation[0]) - 97, int(notation[1]) - 1

def notation_to_drop(piece, square):
	return notation_to_coordinates(square), piece

def move_to_notation(move):
	a, b = move[0]
	c, d = move[1]
	return "move " + chr(a + 97) + str(b + 1) + " " + chr(c + 97) + str(d + 1)

def drop_to_notation(drop):
	a, b = drop[0]
	return "drop " + drop[1] + " " + chr(a + 97) + str(b + 1)

def print_game(game):
	lower_or_upper = "lower" if game.current_player == 0 else "UPPER"

	print utils.stringifyBoard(game.board.board_matrix)
	print "Captures UPPER: " + " ".join([str.upper(x) for x in game.player2.droppable])
	print "Captures lower: " + " ".join(game.player1.droppable) + "\n"

	player = game.id_to_player(game.current_player)
	if player.in_check:
		moves, drops = game.board.find_all_moves_and_drops_no_check(player)
		moves = sorted([move_to_notation(x) for x in moves])
		drops = sorted([drop_to_notation(x) for x in drops])
		print lower_or_upper + " player is in check!\nAvailable moves:"
		for drop in drops:
			print drop
		for move in moves:
			print move
	print ("lower> " if game.current_player == 0 else "UPPER> "),

if __name__ == "__main__":
	main()