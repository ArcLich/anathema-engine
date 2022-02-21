"""
Not Magnus
Classical chess engine by Devin Zhang

Helper functions, tables, constants, and globals used throughout the program
"""
import chess
import chess.svg
import IPython.display
import time


# Options
START_AS = "BLACK" # Human player plays as: WHITE, BLACK, or RANDOM. Put COMPUTER for CPU to play itself
DEPTH = 4 # Search depth, minimum 1
OPENING_BOOK = False # Use opening book?
ENDGAME_BOOK = False # Use endgame book?
OPENING_BOOK_LOCATION = "Opening Book/Book.bin"
ENDGAME_BOOK_LOCATION = "Endgame Book"

# Constants
INF = float("inf")
MATE_SCORE = 99999

# Tables
ttable = {} # Transposition table
htable = [[[0 for x in range(64)] for y in range(64)] for z in range(2)] # History heuristic table [side to move][move from][move to]

# UCI
stop = False # Stop searching
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
    return len(board.piece_map())


def null_move_ok(board):
    """
    Returns true if conditions are met to perform null move pruning
    Returns false if side to move is in check or too few pieces (indicator of endgame, more chance for zugzwang)
    """
    endgame_threshold = 14
    if (board.ply() >= 1 and board.move_stack and board.peek() != chess.Move.null()) or board.is_check() or get_num_pieces(board) <= endgame_threshold:
        return False
    return True


def reduction_ok(board, move): # TODO error when initating new position, another error might cause loss of elo
    """
    Returns true if conditions are met to perform late move reduction
    Returns false if move:
    - Is a capture
    - Is a promotion
    - Gives check
    - Is made while in check
    """
    result = True
    board.pop()
    if board.is_capture(move) or move.promotion or board.gives_check(move) or board.is_check():
        result = False
    board.push(move)
    return result


def get_square_color(square):
    """
    Given a square on the board return whether
    its a dark square or a light square
    """
    if (square % 8) % 2 == (square // 8) % 2:
        return chess.BLACK
    else:
        return chess.WHITE


def is_square_a_file(square):
    """
    Returns true if the square is on the A file
    """
    return square % 8 == 0


def is_square_h_file(square):
    """
    Returns true if the square is on the H file
    """
    return (square + 1) % 8 == 0


def get_square_rank(square):
    """
    Returns the rank of the square (1-8)
    """
    return (square // 8) + 1


def uci_output(move, score, depth, nodes, time_search):
    """
    Print output about the search in UCI engine communication
    """
    time_now = time.time_ns()
    time_diff = time_now - time_search
    try:
        return "Info: depth {}, score {}, nodes {}, nps {}, time {}, pv {} \n".format(depth, int(score), nodes, int(nodes/(time_diff*10**-9)), int(time_diff*10**-6), move)
    except ZeroDivisionError:
        time_diff = 0.1
        return "Info: depth {}, score {}, nodes {}, nps {}, time {}, pv {} \n".format(depth, int(score), nodes, int(nodes/(time_diff*10**-9)), int(time_diff*10**-6), move)


def can_exit_search(movetime, stop):
    """
    Returns true if stop command given or too much time elapsed on search
    """
    return stop() or (movetime - (time.time_ns() - start_time) * 10**-6) <= 0