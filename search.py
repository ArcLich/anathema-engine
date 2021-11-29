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
    - negaC*?
    - extensions
    - iterative deepening
    - aspiration search?
    - Quiescence Search (doesnt work)
    """
    key = chess.polyglot.zobrist_hash(board)

    # Search for position in the transposition table
    if key in ttable:
        tt_move, tt_score, tt_type, tt_depth = ttable[key]
        if tt_depth >= depth:
            if tt_type == "EXACT":
                return (tt_move, tt_score)

            if tt_type == "LOWERBOUND" and tt_score > alpha: # Update lowerbound alpha
                alpha = tt_score
            elif tt_type == "UPPERBOUND" and tt_score < beta: # Update upperbound beta
                beta = tt_score

            if alpha >= beta:
                return (tt_move, tt_score)

    if depth == 0 or board.is_game_over():
        score = evaluate(board)

        # Add position to the transposition table
        if score <= alpha: # Score is lowerbound
            ttable[key] = ("", score, "LOWERBOUND", depth)
        elif score >= beta: # Score is upperbound
            ttable[key] = ("", score, "UPPERBOUND", depth)
        else: # Score is exact
            ttable[key] = ("", score, "EXACT", depth)

        return ("", score)
    else:
        # Alpha-beta negamax
        score = 0
        best_move = ""
        best_score = -INF
        moves = list(board.legal_moves)
        moves.sort(key = lambda move : rate(board, depth, move), reverse = True)

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

        if board.piece_at(best_move.from_square).piece_type == chess.PAWN: # Clear ttable after pawn move
            ttable.clear()
        
        # Add position to the transposition table
        if best_score <= alpha: # Score is lowerbound
            ttable[key] = (best_move, best_score, "LOWERBOUND", depth)
        elif best_score >= beta: # Score is upperbound
            ttable[key] = (best_move, best_score, "UPPERBOUND", depth)
        else: # Score is exact
            ttable[key] = (best_move, best_score, "EXACT", depth)

        return (best_move, best_score)


def MTDf(board, depth, guess):
    """
    Searches the possible moves using negamax but zooming in on the window
    Psuedocode and algorithm from Aske Plaat, Jonathan Schaeffer, Wim Pijls, and Arie de Bruin
    """
    upperbound = INF
    lowerbound = -INF
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
    

def cpu_move(board):
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

    if ENDGAME_BOOK and get_num_pieces(board) <= 7:
        evals = []
        for move in list(board.legal_moves):
            board.push(move)
            score = eval_endgame(board)
            board.pop()
            evals.append((move, score))
        return max(evals, key = lambda eval : eval[1])[0]

    # return negamax(board, DEPTH, -INF, INF)[0]
    return MTDf(board, DEPTH, 0)[0]
