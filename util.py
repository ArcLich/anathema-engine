"""
Not Magnus
Classical chess engine by Devin Zhang

Helper functions, tables, constants, and globals used throughout the program
"""
import time
import chess
import IPython.display
from chess.svg import board


# Options
START_AS = "WHITE" # Human player plays as: WHITE, BLACK, or RANDOM. Put COMPUTER for CPU to play itself
DEPTH = 4 # Search depth, minimum 1
OPENING_BOOK = False # Use opening book?
ENDGAME_BOOK = False # Use endgame book?
OPENING_BOOK_LOCATION = "/Opening Book/Book.bin"
ENDGAME_BOOK_LOCATION = "/Endgame Book"

# Constants
INF = float("inf")
MATE_SCORE = 99999

# Tables
ttable = {} # Transposition table
htable = [[[0 for x in range(64)] for y in range(64)] for z in range(2)] # History heuristic table [side to move][move from][move to]
rtable = {} # Draw by repetition table

# UCI
nodes = 0 # Number of positions considered
start_time = 0 # Time search is started


def display(board):
    """
    Clears cell and displays visual board
    """
    IPython.display.clear_output(wait = True)
    if START_AS == "WHITE" or START_AS == "COMPUTER":
        orientation = chess.WHITE
    else:
        orientation = chess.BLACK
    if board.move_stack:
        lastmove = board.peek()
    else:
        lastmove = None
    IPython.display.display(chess.svg.board(board, orientation = orientation, lastmove = lastmove, size = 350))


def rate(board, move, tt_move):
    """
    Rates a move in relation to the following order for move ordering:
    - Refutation move (moves from transpositions) | score = 600
    - Winning captures (low value piece captures high value piece) | 100 <= score <= 500
    - Promotions / Equal captures (piece captured and capturing have the same value) | score = 0
    - Killer moves (from history heuristic table) | -100 < score < 0
    - Losing captures (high value piece captures low value piece) | -500 <= score <= -100
    - All others | score = -1000

    Pieces have the following values:
    - Pawn: 1
    - Knight: 2
    - Bishop: 3
    - Rook: 4
    - Queen: 5
    - King: 6

    Values are arbitrary, and only useful when comparing
    whether one is higher or lower than the other
    """
    if tt_move:
        return 600

    if htable[board.piece_at(move.from_square).color][move.from_square][move.to_square] != 0:
        return htable[board.piece_at(move.from_square).color][move.from_square][move.to_square] / -100

    if board.is_capture(move):
        if board.is_en_passant(move):
            return 0 # pawn value (1) - pawn value (1) = 0
        else:
            return (board.piece_at(move.to_square).piece_type - board.piece_at(move.from_square).piece_type) * 100

    if move.promotion:
        return 0

    return -1000


def get_num_pieces(board):
    """
    Get the number of pieces of all types and color on the board.
    """
    return len(chess.SquareSet(board.occupied))


def null_move_ok(board):
    """
    Returns true if conditions are met to perform null move pruning
    Returns false if side to move is in check or too few pieces (indicator of endgame, more chance for zugzwang)
    """
    endgame_threshold = 14 # TODO adjust threshold
    if (board.move_stack and board.peek() == chess.Move.null()) or board.is_check() or get_num_pieces(board) <= endgame_threshold:
        return False
    return True


def reduction_ok(board, depth, move, moves_searched, has_failed_high):
    """
    Returns true if conditions are met to perform late move reduction
    Returns false if move:
    - is a capture
    - is a promotion
    - gives check
    - is made while in check
    """
    full_depth_moves_threshold = 4 # Minimum number of moves to search at full depth
    reduction_threshold = 3 # Maximum depth to reduce at

    result = True
    board.pop()
    if moves_searched < full_depth_moves_threshold or has_failed_high == True or depth < reduction_threshold \
        or board.is_capture(move) or move.promotion or board.gives_check(move) or board.is_check():
        result = False
    board.push(move)
    return result


def uci_output(move, score, depth, nodes, time_search):
    """
    Print output about the search in UCI engine communication
    """
    time_now = time.time_ns()
    time_diff = time_now - time_search

    try:
        return "info depth {} score cp {} nodes {} nps {} time {} pv {} \n"\
            .format(depth, int(score), nodes, int(nodes / (time_diff * 10**-9)), int(time_diff * 10**-6), move)
    except ZeroDivisionError:
        time_diff = 0.1
        return "info depth {} score cp {} nodes {} nps {} time {} pv {} \n"\
            .format(depth, int(score), nodes, int(nodes / (time_diff * 10**-9)), int(time_diff * 10**-6), move)


def can_exit_search(movetime, stop, start_time):
    """
    Returns true if stop command given or too much time elapsed on search
    """
    if stop() or (movetime - (time.time_ns() - start_time) * 10**-6) <= 0:
        return True
    return False


def is_threefold_repetition(board):
    """
    Checks if the game is over by threefold repetition
    """
    key = board._transposition_key()
    if key in rtable:
        if rtable[key] >= 3:
            return True
    return False


def get_game_state(board):
    """
    Returns a number based on how the game has ended:
    - Game not ended: 0
    - Checkmate: 1
    - Stalemate: 2
    - Draw (by threefold repetition): 3
    - Draw (by fifty-move rule): 4
    - Draw (by insufficient material): 5
    """
    if board.is_checkmate():
        return 1
    if board.is_stalemate():
        return 2
    if is_threefold_repetition(board):
        return 3
    if board.halfmove_clock >= 100:
        return 4
    if board.is_insufficient_material():
        return 5
    return 0


def count_bin(num):
    """
    Given an integer, return how many 1s in that integer
    in binary form
    """
    return bin(num).count("1")


def is_game_over(board):
    """
    Checks if the game is over by checkmate, stalemate,
    threefold repetition, fifty-move rule, or insufficient material
    """
    if get_game_state(board) == 0:
        return False
    return True
