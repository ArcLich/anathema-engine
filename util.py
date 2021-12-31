"""
Not Magnus
Classical chess engine by Devin Zhang

Helper functions, constants, and globals used throughout the program
"""
import chess
import chess.svg
import IPython.display


# Options
START_AS = "WHITE" # Human player plays as: WHITE, BLACK, or RANDOM. Put COMPUTER for CPU to play itself
DEPTH = 4 # Search depth, minimum 1
OPENING_BOOK = False # Use opening book?
ENDGAME_BOOK = True # Use endgame book?

# Constants
INF = float("inf")
MATE_SCORE = 99999

# Other
ttable = {} # Transposition table
htable = [[[0 for x in range(64)] for y in range(64)] for z in range(2)] # History heuristic table [side to move][move from][move to]


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
    num = 0
    for color in chess.COLORS:
        for piece in chess.PIECE_TYPES:
            num += (len(board.pieces(piece, color)))
    return num


def get_phase(board):
    """
    Gets the game state of the board as a number
    Low numbers indicate early game
    High numbers indiciate endgame
    """
    pawn_phase = 0
    knight_phase = 1
    bishop_phase = 1
    rook_phase = 2
    queen_phase = 4
    total_phase = 16*pawn_phase + 4*knight_phase + 4*bishop_phase + 4*rook_phase + 2*queen_phase

    phase = total_phase
    phase -= (len(board.pieces(chess.PAWN, chess.WHITE)) + len(board.pieces(chess.PAWN, chess.BLACK))) * pawn_phase
    phase -= (len(board.pieces(chess.KNIGHT, chess.WHITE)) + len(board.pieces(chess.KNIGHT, chess.BLACK))) * knight_phase
    phase -= (len(board.pieces(chess.BISHOP, chess.WHITE)) + len(board.pieces(chess.BISHOP, chess.BLACK))) * bishop_phase
    phase -= (len(board.pieces(chess.ROOK, chess.WHITE)) + len(board.pieces(chess.ROOK, chess.BLACK))) * rook_phase
    phase -= (len(board.pieces(chess.QUEEN, chess.WHITE)) + len(board.pieces(chess.KNIGHT, chess.BLACK))) * queen_phase

    phase = (phase * 256 + (total_phase / 2)) / total_phase;

    return phase


def null_move_ok(board):
    """
    Returns true if conditions are met to perform null move pruning
    Returns false if side to move is in check or it's the endgame (because position is possibly zugzwang)
    """
    endgame_threshold = 100
    if board.is_check() or get_phase(board) >= endgame_threshold:
        return False
    return True
    