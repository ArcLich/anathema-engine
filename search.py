"""
Not Magnus
Classical chess engine by Devin Zhang
"""
import chess
import chess.polyglot
import chess.gaviota
from evaluate import *
from util import *


def negamax(board, depth, alpha, beta):
    """
    Searches the possible moves using negamax, alpha-beta pruning, null-move pruning, and a transposition table
    Initial psuedocode adapated from Jeroen W.T. Carolus

    TODO
    - killer heuristic
    - null move pruning
    - history heuristic
    - legal move generation (bitboards)
    - late move reduction
    - https://www.chessprogramming.org/Search#Alpha-Beta_Enhancements
    - parallel search
    - extensions
    - aspiration search?
    - Quiescence Search (doesnt work)
    """
    key = chess.polyglot.zobrist_hash(board)
    tt_move = None

    # Search for position in the transposition table
    if key in ttable:
        tt_move, tt_lowerbound, tt_upperbound, tt_depth = ttable[key]
        if tt_depth >= depth:
            if tt_upperbound <= alpha or tt_lowerbound == tt_upperbound:
                return (tt_move, tt_upperbound)
            if tt_lowerbound >= beta:
                return (tt_move, tt_lowerbound)

    if depth == 0 or board.is_game_over():
        score = evaluate(board)
        ttable[key] = (None, score, score, depth) # Add position to the transposition table
        return (None, score)
    else:
        # Alpha-beta negamax
        score = 0
        best_move = None
        best_score = -INF
        moves = list(board.legal_moves)
        moves.sort(key = lambda move : rate(board, move, tt_move), reverse = True)

        for move in moves:
            board.push(move)
            score = -negamax(board, depth - 1, -beta, -alpha)[1]
            board.pop()

            if score > best_score:
                best_move = move
                best_score = score

            alpha = max(alpha, best_score)

            if alpha >= beta: # Beta cut-off
                break
        
        # # Add position to the transposition table
        if best_score <= alpha:
            ttable[key] = (best_move, -MATE_SCORE, best_score, depth)
        if alpha < best_score < beta:
            ttable[key] = (best_move, best_score, best_score, depth)
        if best_score >= beta:
            ttable[key] = (best_move, best_score, MATE_SCORE, depth)

        return (best_move, best_score)


def MTDf(board, depth, guess):
    """
    Searches the possible moves using negamax by zooming in on the window
    Psuedocode and algorithm from Aske Plaat, Jonathan Schaeffer, Wim Pijls, and Arie de Bruin
    """
    upperbound = MATE_SCORE
    lowerbound = -MATE_SCORE
    while (lowerbound < upperbound):
        if guess == lowerbound:
            beta = guess + 1
        else:
            beta = guess

        move, guess = negamax(board, depth, beta - 1, beta)

        if guess < beta:
            upperbound = guess
        else:
            lowerbound = guess

    return (move, guess)


def negacstar(board, depth, mini, maxi):
    """
    Searches the possible moves using negamax by zooming in on the window
    Pseudocode and algorithm from Jean-Christophe Weill
    """
    while (mini < maxi):
        alpha = (mini + maxi) / 2
        move, score = negamax(board, depth, alpha, alpha + 1)
        if score > alpha:
            mini = score
        else:
            maxi = score
    return (move, score)


def iterative_deepening(board, depth):
    """
    Approaches the desired depth in steps using MTD(f)
    """
    guess = 0
    for d in range(1, depth + 1):
        move, guess = MTDf(board, d, guess)
    return (move, guess)
    

def cpu_move(board, depth):
    """
    Chooses a move for the CPU
    If inside opening book make book move
    If inside Gaviota tablebase make tablebase move
    Else search for a move
    """
    global OPENING_BOOK

    if OPENING_BOOK:
        try:
            with chess.polyglot.open_reader("Opening Book/Book.bin") as opening_book: # https://sourceforge.net/projects/codekiddy-chess/files/
                opening = opening_book.choice(board)
                opening_book.close()
                return opening.move
        except IndexError:
            OPENING_BOOK = False

    if ENDGAME_BOOK and get_num_pieces(board) <= 5:
        evals = []
        for move in list(board.legal_moves):
            board.push(move)
            score = eval_endgame(board)
            board.pop()
            evals.append((move, score))
        return max(evals, key = lambda eval : eval[1])[0]

    # return negamax(board, depth, -MATE_SCORE, MATE_SCORE)[0]
    # return MTDf(board, depth, 0)[0]
    return negacstar(board, depth, -MATE_SCORE, MATE_SCORE)[0]
    # return iterative_deepening(board, depth)[0]
