"""
Not Magnus
Classical chess engine by Devin Zhang
"""
import chess
import chess.polyglot
from evaluate import *
from util import *

def search(board, depth, alpha, beta):
    """
    Searches the possible moves using negamax, alpha-beta pruning, and a transposition table

    TODO
    - move ordering + legal move  (bitboards)
    - aspiration search
    - pv search (or negascout)
    - iterative deepening
    - null move pruning
    - late move reduction
    - https://www.chessprogramming.org/Search#Alpha-Beta_Enhancements
    - parallel search
    - Quiescence Search
    """
    # Psuedocode from Jeroen W.T. Carolus
    key = chess.polyglot.zobrist_hash(board)

    # Search for position in the transposition table
    if key in ttable:
        tt_value, tt_type, tt_depth = ttable[key]
        if tt_depth >= depth:
            if (tt_type == "EXACT"):
                return ("", tt_value)

            if (tt_type == "LOWERBOUND" and tt_value > alpha):
                alpha = tt_value # Update lowerbound alpha
            elif (tt_type == "UPPERBOUND" and tt_value < beta):
                beta = tt_value # Update upperbound beta

            if alpha >= beta:
                return ("", tt_value)

    # Add position to the transposition table
    if depth == 0 or board.is_game_over():
        score = -evaluate(board) # TODO why is it negative of the value??
        
        if (score <= alpha):
            ttable[key] = (score, "LOWERBOUND", depth) # Score is lowerbound
        elif (score >= beta):
            ttable[key] = (score, "UPPERBOUND", depth) # Score is upperbound
        else:
            ttable[key] = (score, "EXACT", depth) # Score is exact

        return ("", score)
    else:
        # Alpha-beta negamax
        score = 0
        best_move = ""
        best_score = -INF
        for move in list(board.legal_moves):
            board.push(move)
            score = -search(board, depth - 1, -beta, -alpha)[1]
            board.pop()

            if score > best_score:
                best_move = move
                best_score = score
            if best_score > alpha:
                alpha = best_score
            if best_score >= beta:
                break

        # Add position to the transposition table
        if (best_score <= alpha):
            ttable[key] = (best_score, "LOWERBOUND", depth) # score is lowerbound
        elif (best_score >= beta):
            ttable[key] = (best_score, "UPPERBOUND", depth) # score is upperbound
        else:
            ttable[key] = (best_score, "EXACT", depth) # score is exact

        return (best_move, best_score)


def cpu_move(board):
    """
    Chooses a move for the CPU
    If inside opening book make book move
    Else compute move

    TODO add endgame book
    """
    global OPENING

    if OPENING:
        with chess.polyglot.open_reader("Book.bin") as opening_book: # https://sourceforge.net/projects/codekiddy-chess/files/
            try:
                opening = opening_book.choice(board)
                opening_book.close()
                return opening.move
            except IndexError:
                opening_book.close()
                OPENING = False
    return search(board, DEPTH, -INF, INF)[0]