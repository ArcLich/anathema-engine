"""
Not Magnus
Classical chess engine by Devin Zhang
"""
import chess
import chess.polyglot
from evaluate import *
from util import *

def negamax(depth, alpha, beta):
    """
    Searches the possible moves using negamax, alpha-beta pruning, and a transposition table

    TODO
    - legal move generation (bitboards)
    - aspiration search
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
        tt_score, tt_move, tt_type, tt_depth = ttable[key]
        if tt_depth >= depth:
            if tt_type == "EXACT":
                return (tt_move, tt_score)

            if tt_type == "LOWERBOUND" and tt_score > alpha: # Update lowerbound alpha
                alpha = tt_score
            elif tt_type == "UPPERBOUND" and tt_score < beta: # Update upperbound beta
                beta = tt_score

            if alpha >= beta:
                return (tt_move, tt_score)

    # Add position to the transposition table
    if depth == 0 or board.is_game_over():
        score = -evaluate() # TODO why is it negative of the value??
        
        if score <= alpha: # Score is lowerbound
            ttable[key] = (score, "", "LOWERBOUND", depth)
        elif score >= beta: # Score is upperbound
            ttable[key] = (score, "", "UPPERBOUND", depth)
        else: # Score is exact
            ttable[key] = (score, "", "EXACT", depth)

        return ("", score)
    else:
        # Alpha-beta negamax
        score = 0
        best_move = ""
        best_score = -INF
        moves = list(board.legal_moves)
        moves.sort(key = rate, reverse = True)
        for move in moves:
            board.push(move)
            score = -negamax(depth - 1, -beta, -alpha)[1]
            board.pop()

            if score > best_score:
                best_move = move
                best_score = score
            if best_score > alpha:
                alpha = best_score
            if best_score >= beta:
                break

        if board.piece_at(best_move.from_square).piece_type == chess.PAWN: # Clear ttable after pawn move
            ttable.clear()
        
        # Add position to the transposition table
        if best_score <= alpha: # Score is lowerbound
            ttable[key] = (best_score, best_move, "LOWERBOUND", depth)
        elif best_score >= beta: # Score is upperbound
            ttable[key] = (best_score, best_move, "UPPERBOUND", depth)
        else: # Sore is exact
            ttable[key] = (best_score, best_move, "EXACT", depth)

        return (best_move, best_score)

        
def MTDf(depth, guess):
    upperbound = INF
    lowerbound = -INF
    best_move = ""
    while (lowerbound < upperbound):
        if guess == lowerbound:
            beta = guess + 1
        else:
            beta = guess
        best_move, guess = negamax(depth, beta - 1, beta)
        if guess < beta:
            upperbound = guess
        else:
            lowerbound = guess
    return (best_move, guess)


def cpu_move():
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
    return MTDf(DEPTH, 0)[0]