"""
Not Magnus
Classical chess engine by Devin Zhang
"""
import chess
import chess.polyglot
import chess.gaviota
from evaluate import *
from util import *


def qsearch(board, alpha, beta):
    """
    Quiescence search to extend search depth until there are no more captures
    """
    stand_pat = evaluate(board)
    if stand_pat >= beta:
        return beta
    alpha = max(alpha, stand_pat)

    moves = list(board.legal_moves)
    moves.sort(key = lambda move : rate(board, move, None), reverse = True)
    for move in moves:
        if board.is_capture(move):
            board.push(move)
            score = -qsearch(board, -beta, -alpha)
            key = chess.polyglot.zobrist_hash(board)
            ttable[key] = (0, None, score, score) # Add position to the transposition table
            board.pop()

            if score >= beta:
                return beta
            alpha = max(alpha, score)
    return alpha


def negamax(board, depth, alpha, beta):
    """
    Searches the possible moves using negamax, alpha-beta pruning, transposition table, and quiescence search
    Initial psuedocode adapated from Jeroen W.T. Carolus

    TODO
    - killer heuristic
    - history heuristic
    - legal move generation (bitboards?)
    - late move reduction
    - https://www.chessprogramming.org/Search#Alpha-Beta_Enhancements
    - parallel search
    - extensions
    - aspiration search?
    """
    key = chess.polyglot.zobrist_hash(board)
    tt_move = None

    # Search for position in the transposition table
    if key in ttable:
        tt_depth, tt_move, tt_lowerbound, tt_upperbound = ttable[key]
        if tt_depth >= depth:
            if tt_upperbound <= alpha or tt_lowerbound == tt_upperbound:
                return (tt_move, tt_upperbound)
            if tt_lowerbound >= beta:
                return (tt_move, tt_lowerbound)

    if depth <= 0 or board.is_game_over():
        score = qsearch(board, alpha, beta)
        ttable[key] = (depth, None, score, score) # Add position to the transposition table
        return (None, score)
    else:
        # Null move pruning
        if null_move_ok(board):
            board.push(chess.Move.null())
            null_move_depth_reduction = 2
            score = -negamax(board, depth - null_move_depth_reduction - 1, -beta, -beta + 1)[1]
            board.pop()
            if score >= beta:
                return (None, score)

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
            ttable[key] = (depth, best_move, -MATE_SCORE, best_score)
        if alpha < best_score < beta:
            ttable[key] = (depth, best_move, best_score, best_score)
        if best_score >= beta:
            ttable[key] = (depth, best_move, best_score, MATE_SCORE)

        return (best_move, best_score)


def MTDf(board, depth, guess):
    """
    Searches the possible moves using negamax by zooming in on the window
    Psuedocode from Aske Plaat, Jonathan Schaeffer, Wim Pijls, and Arie de Bruin
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
    Pseudocode from Jean-Christophe Weill
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
                move = opening.move
        except IndexError:
            OPENING_BOOK = False

    if ENDGAME_BOOK and get_num_pieces(board) <= 5:
        evals = []
        for move in list(board.legal_moves):
            board.push(move)
            score = eval_endgame(board)
            board.pop()
            evals.append((move, score))
        move = max(evals, key = lambda eval : eval[1])[0]

    # move = negamax(board, depth, -MATE_SCORE, MATE_SCORE)[0]
    # move = MTDf(board, depth, 0)[0]
    move = negacstar(board, depth, -MATE_SCORE, MATE_SCORE)[0]
    # move = iterative_deepening(board, depth)[0]

    set_ttable(board, move)
    return move
