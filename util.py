"""
Not Magnus
Classical chess engine by Devin Zhang
"""
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


def display(board):
    """
    Clears cell and displays visual board
    """
    IPython.display.clear_output(wait = True)
    IPython.display.display(board)