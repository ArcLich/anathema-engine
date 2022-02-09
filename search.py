"""
Not Magnus
Learner classical chess engine by Devin Zhang

Search functions which navigate the game tree
"""
import chess.polyglot
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
            
            # Add position to the transposition table
            key = chess.polyglot.zobrist_hash(board)
            checksum = key ^ hash((0, None, score, score))
            ttable[key] = (checksum, 0, None, score, score)
            
            board.pop()

            if score >= beta:
                return beta
            alpha = max(alpha, score)
    return alpha


def negamax(board, depth, alpha, beta):
    """
    Searches the possible moves using negamax, alpha-beta pruning, transposition table,
    quiescence search, null move pruning, and late move reduction
    Initial psuedocode adapated from Jeroen W.T. Carolus
    Lockless transpositional table procedure (using what I call a "checksum") by Robert Hyatt and Timothy Mann

    TODO
    - parallel search
    """
    key = chess.polyglot.zobrist_hash(board)
    tt_move = None

    # Search for position in the transposition table
    if key in ttable:
        tt_checksum, tt_depth, tt_move, tt_lowerbound, tt_upperbound = ttable[key]
        if tt_checksum ^ hash((tt_depth, tt_move, tt_lowerbound, tt_upperbound)) == key and tt_depth >= depth:
            if tt_upperbound <= alpha or tt_lowerbound == tt_upperbound:
                return (tt_move, tt_upperbound)
            if tt_lowerbound >= beta:
                return (tt_move, tt_lowerbound)

    if depth <= 0 or board.is_game_over():
        score = qsearch(board, alpha, beta)
        
        # Add position to the transposition table
        checksum = key ^ hash((depth, None, score, score))
        ttable[key] = (checksum, depth, None, score, score)
        
        return (None, score)
    else:
        # Null move pruning
        if null_move_ok(board):
            null_move_depth_reduction = 2
            board.push(chess.Move.null())
            score = -negamax(board, depth - 1 - null_move_depth_reduction, -beta, -beta + 1)[1]
            board.pop()
            if score >= beta:
                return (None, score)

        # Alpha-beta negamax
        score = 0
        best_move = None
        best_score = -INF
        moves = list(board.legal_moves)
        moves.sort(key = lambda move : rate(board, move, tt_move), reverse = True)

        moves_searched = 0
        failed_high = False

        for move in moves:
            board.push(move)
            
            # Late move reduction
            late_move_depth_reduction = 0
            full_depth_moves_threshold = 4
            reduction_threshold = 4
            if moves_searched >= full_depth_moves_threshold and failed_high == False and depth >= reduction_threshold and reduction_ok(board, move):
                late_move_depth_reduction = 1

            score = -negamax(board, depth - 1 - late_move_depth_reduction, -beta, -alpha)[1]
            board.pop()

            moves_searched += 1

            if score > best_score:
                best_move = move
                best_score = score

            alpha = max(alpha, best_score)

            if best_score >= beta: # Beta cut-off (fails high)
                failed_high = True
                if not board.is_capture(move):
                    htable[board.piece_at(move.from_square).color][move.from_square][move.to_square] += depth**2 # Update history heuristic table
                break
        
        # Add position to the transposition table
        if best_score <= alpha:
            checksum = key ^ hash((depth, best_move, -MATE_SCORE, best_score))
            ttable[key] = (checksum, depth, best_move, -MATE_SCORE, best_score)
        if alpha < best_score < beta:
            checksum = key ^ hash((depth, best_move, best_score, best_score))
            ttable[key] = (checksum, depth, best_move, best_score, best_score)
        if best_score >= beta:
            checksum = key ^ hash((depth, best_move, best_score, MATE_SCORE))
            ttable[key] = (checksum, depth, best_move, best_score, MATE_SCORE)

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


def iterative_deepening(board, depth):
    """
    Approaches the desired depth in steps using MTD(f)
    """
    global multithreading_result

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
    global ttable
    global htable

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
        move = max(evals, key = lambda eval : eval[1])[0]
        return move

    move = negamax(board, depth, -MATE_SCORE, MATE_SCORE)[0]
    # move = MTDf(board, depth, 0)[0]
    # move = iterative_deepening(board, depth)[0]

    if board.is_irreversible(move): # Reset transposition table
        ttable.clear()
    htable = [[[0 for x in range(64)] for y in range(64)] for z in range(2)] # Reset history heuristic table
    
    return move
