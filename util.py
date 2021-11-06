import chess
import IPython.display


# Options
START_AS = "WHITE" # Human player plays as: WHITE, BLACK, or RANDOM
DEPTH = 4 # Search depth, minimum 1
OPENING = False # Use opening book?

# Constants
INF = float("inf")

# Other
ttable = {} # Transposition table


def get_num_pieces(board, piece, color = "BOTH"):
    """
    Returns the number of a certain piece on the board, given color
    Or returns number of a certain piece of both colors combined
    """
    if color == "BOTH":
        return get_num_pieces(board, piece, chess.WHITE) + get_num_pieces(board, piece, chess.BLACK)
    else:
        return str(board.pieces(piece, color)).count("1")


def display(board):
    """
    Clears cell and displays visual board
    """
    IPython.display.clear_output(wait = True)
    IPython.display.display(board)