"""
Not Magnus
Classical chess engine by Devin Zhang
"""
import chess
import IPython.display


# Options
START_AS = "WHITE" # Human player plays as: WHITE, BLACK, or RANDOM
DEPTH = 5 # Search depth, minimum 1
OPENING = False # Use opening book?

# Constants
INF = float("inf")

# Other
board = chess.Board()
ttable = {} # Transposition table


def display():
    """
    Clears cell and displays visual board
    """
    IPython.display.clear_output(wait = True)
    IPython.display.display(board)


def rate(move):
    """
    Rates a move in relation to the following order:
    - Winning captures (low value piece captures high value piece)
    - Promotions / Equal captures (piece captured and capturing have the same value)
    - Losing captures (high value piece captures low value piece)
    - All others
    High scores are winning captures, low scores are losing captures, etc

    Values are arbitrary, and only useful when comparing whether
    one is higher or lower than the other
    """
    if board.is_capture(move):
        if board.is_en_passant(move):
            return 0
        return board.piece_at(move.to_square).piece_type - board.piece_at(move.from_square).piece_type
    if move.promotion:
        return 0
    return -99999