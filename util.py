"""
Not Magnus
Classical chess engine by Devin Zhang
"""
import chess
import chess.svg
import IPython.display


# Options
START_AS = "WHITE" # Human player plays as: WHITE, BLACK, or RANDOM
DEPTH = 5 # Search depth, minimum 1
OPENING_BOOK = False # Use opening book?
ENDGAME_BOOK = True # Use endgame book?

# Constants
INF = float("inf")

# Other
ttable = {} # Transposition table
rtable = {} # Refutation table


def display(board):
    """
    Clears cell and displays visual board
    """
    IPython.display.clear_output(wait = True)
    if START_AS == "WHITE":
        orientation = chess.WHITE
    else:
        orientation = chess.BLACK
    if board.move_stack:
        lastmove = board.peek()
    else:
        lastmove = None
    IPython.display.display(chess.svg.board(board, orientation = orientation, lastmove = lastmove, size = 350))


def rate(board, depth, move):
    """
    Rates a move in relation to the following order for move ordering:
    - Winning captures (low value piece captures high value piece) | 10 <= score <= 50
    - Promotions / Equal captures (piece captured and capturing have the same value) | score = 0
    - Killer moves | score = -5
    - Losing captures (high value piece captures low value piece) | -50 <= score <= -10
    - All others | score = -INF

    Values are arbitrary, and only useful when comparing whether
    one is higher or lower than the other

    TODO
    History heuristic
    """
    if depth in rtable:
        if move in rtable[depth]:
            return -5

    if board.is_capture(move):
        if board.is_en_passant(move):
            return 0
        else:
            return 10 * (board.piece_at(move.to_square).piece_type - board.piece_at(move.from_square).piece_type)

    if move.promotion:
        return 0

    return -INF


def get_num_pieces(board):
    """
    Get the number of pieces of all types and color on the board.
    """
    num = 0
    for color in chess.COLORS:
        for piece in chess.PIECE_TYPES:
            num += (len(board.pieces(piece, color)))
    return num
    