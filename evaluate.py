"""
Not Magnus
Classical chess engine by Devin Zhang

Evaluation functions which score a given position
"""
import chess.gaviota
from util import *
from piece_squares_tables import *


def eval_endgame(board):
    """
    Evaluates an endgame position with 5 or less pieces
    Returns depth-to-mate from Gaviota endgame tablebase
    """
    with chess.gaviota.open_tablebase("Endgame Book") as tablebase: # https://chess.cygnitec.com/tablebases/gaviota/
        if board.is_checkmate():
            return INF
        score = tablebase.get_dtm(board) * MATE_SCORE
        if score == 0:
            return -INF
        else:
            return score


def evaluate(board):
    """
    Game state evaluation function, score mimicking centipawns
    Values are relative so high values mean the board favors the current
    player, and not necessarily the white player

    Utilizes:
    - Material score
    - Piece-squares tables
    - Tapered evaluation
    - Mobility
    - 5-men Gaviota endgame tablebase (if toggled)

    Gives bonuses to:
    - Rooks on open and semi-open files
    - Passed pawns
    - Knights on outposts (squares on rank 4, 5, or 6 defended by a friendly pawn)

    Penalizes
    - Pinned queens
    - Friendly pawns that are on the same colored square as the bishop
    - Isolated pawns

    Material score values from Tomasz Michniewski's Simplified Evaluation Function
    Piece-squares table values and tapered evaluation from Ronald Friederich's PeSTO's Evaluation Function

    TODO
    - fine tune weights
    - king safety
    - Texel's tuning method
    - king pawn tropism
    - king safety
    """


    if ENDGAME_BOOK and get_num_pieces(board) <= 5:
        return eval_endgame(board)
    
    material_values = [100, 320, 330, 500, 900, MATE_SCORE]
    mg_psqts = {
        "P": w_mg_pawn_table,
        "N": w_mg_knight_table,
        "B": w_mg_bishop_table,
        "R": w_mg_rook_table,
        "Q": w_mg_queen_table,
        "K": w_mg_king_table,
        "p": b_mg_pawn_table,
        "n": b_mg_knight_table,
        "b": b_mg_bishop_table,
        "r": b_mg_rook_table,
        "q": b_mg_queen_table,
        "k": b_mg_king_table,
    }
    eg_psqts = {
        "P": w_eg_pawn_table,
        "N": w_eg_knight_table,
        "B": w_eg_bishop_table,
        "R": w_eg_rook_table,
        "Q": w_eg_queen_table,
        "K": w_eg_king_table,
        "p": b_eg_pawn_table,
        "n": b_eg_knight_table,
        "b": b_eg_bishop_table,
        "r": b_eg_rook_table,
        "q": b_eg_queen_table,
        "k": b_eg_king_table,
    }
    phase_scores = [0, 1, 1, 2, 4, 0]

    material_score = 0
    psqt_mg_score = 0
    psqt_eg_score = 0
    phase = 0
    total_phase = 16*phase_scores[chess.PAWN - 1] + 4*phase_scores[chess.KNIGHT - 1] + 4*phase_scores[chess.BISHOP - 1] \
                + 4*phase_scores[chess.ROOK - 1] + 2*phase_scores[chess.QUEEN - 1]
    piece_specific_score = 0

    b_bitboards = [0, 0, 0, 0, 0, 0, 0]
    w_bitboards = [0, 0, 0, 0, 0, 0, 0]
    bitboards = [b_bitboards, w_bitboards]

    # Generate bitboards
    for color in [chess.WHITE, chess.BLACK]:
        for piece in [chess.PAWN, chess.KNIGHT, chess.BISHOP, chess.ROOK, chess.QUEEN, chess.KING]:
            squares = []
            bb = board.pieces(piece, color)
            for i, c in enumerate(bin(bb)[:1:-1], 1):
                if c == "1":
                    squares.append(i - 1)
            bitboards[color][piece] = (squares, bb)

    # Evaluation
    for color in [chess.WHITE, chess.BLACK]:
        relative_weight = 1 if color == board.turn else -1
        for piece in [chess.PAWN, chess.KNIGHT, chess.BISHOP, chess.ROOK, chess.QUEEN, chess.KING]:
            piece_symbol = chess.piece_symbol(piece).upper() if color == chess.WHITE else chess.piece_symbol(piece).lower()
            squares, bb = bitboards[color][piece]
            for square in squares:
                # Material evaluation
                material_score += material_values[piece - 1] * relative_weight

                # PSQT evaluation part 1
                psqt_mg_score += mg_psqts[piece_symbol][square] * relative_weight
                psqt_eg_score += eg_psqts[piece_symbol][square] * relative_weight
                phase += phase_scores[piece - 1]


                # Piece-specific evaluation
                if piece == chess.PAWN:
                    # Penalty to bishop by number of pawns on bishop's square color
                    pawn_bishop_penalty = -2
                    bishop_squares = bitboards[color][chess.BISHOP][0]
                    if len(bishop_squares) != 2: # Technically incorrect, but situations with 2+ same colored bishops are unlikely
                        for bishop_square in bishop_squares:
                            if get_square_color(square) == get_square_color(bishop_square):
                                piece_specific_score += pawn_bishop_penalty * relative_weight

                    # Bonus to passed pawn
                    passed_pawn_bonus = [0, 5, 10, 20, 40, 80, 160, 0]
                    pawn_file = chess.BB_FILES[chess.square_file(square)]
                    bb_passing_files = chess.SquareSet(pawn_file)
                    if square % 8 != 0:
                        pawn_left_file = chess.BB_FILES[chess.square_file(square - 1)]
                        bb_passing_files |= chess.SquareSet(pawn_left_file)
                    if (square + 1) % 8 != 0:
                        pawn_right_file = chess.BB_FILES[chess.square_file(square + 1)]
                        bb_passing_files |= chess.SquareSet(pawn_right_file)
                    if len(bb_passing_files & bitboards[not color][chess.PAWN][1]) == 0:
                        if color == chess.WHITE:
                            piece_specific_score += passed_pawn_bonus[square // 8] * relative_weight
                        else:
                            piece_specific_score += passed_pawn_bonus[8 - ((square // 8) + 1)] * relative_weight

                    # Penalty to isolated pawn
                    pawn_isolated_penalty = -20
                    if len(bb_passing_files & bitboards[color][chess.PAWN][1]) != 3:
                        piece_specific_score += pawn_isolated_penalty * relative_weight

                if piece == chess.KNIGHT:
                    # Bonus to knight on outpost (a square on rank 4, 5, or 6 defended by a friendly pawn)
                    knight_outpost_bonus = 25
                    knight_squares = bitboards[color][chess.KNIGHT][0]
                    bb_pawns = bitboards[color][chess.PAWN][1]
                    for knight_square in knight_squares:
                        rank = (square // 8) + 1
                        if (color == chess.WHITE and (rank == 4 or rank == 5 or rank == 6)) or \
                            ((color == chess.BLACK) and (rank == 5 or rank == 4 or rank == 3)):
                                if len(board.attackers(color, knight_square) & bb_pawns) >= 1:
                                    piece_specific_score += knight_outpost_bonus * relative_weight
                                    break

                if piece == chess.ROOK:
                    # Bonus to rook on open file
                    rook_open_file_bonus = 50
                    rook_file = chess.BB_FILES[chess.square_file(square)]
                    bb_rook_file = chess.SquareSet(rook_file)
                    bb_friend_pawns = bitboards[color][chess.PAWN][1]
                    bb_foe_pawns = bitboards[not color][chess.PAWN][1]
                    if len(bb_rook_file & bb_friend_pawns) == 0:
                        if len(bb_rook_file & bb_foe_pawns) == 0:
                            piece_specific_score += rook_open_file_bonus * relative_weight
                        else:
                            piece_specific_score += rook_open_file_bonus / 2 * relative_weight

                if piece == chess.QUEEN:
                    # Penalty to pinned queen
                    queen_pinned_penalty = -50
                    squares_foe_sliders = bitboards[not color][chess.BISHOP][0] + bitboards[not color][chess.ROOK][0] + bitboards[not color][chess.QUEEN][0]
                    bb_foe_sliders = chess.SquareSet(chess.BB_EMPTY)
                    for foe_square in squares_foe_sliders:
                        bb_foe_sliders |= board.attacks(foe_square)
                    if board.attacks(square) & bb_foe_sliders != 0:
                        piece_specific_score += queen_pinned_penalty * relative_weight
                

    # PSQT evaluation part 2
    mg_phase = max(phase, total_phase)
    eg_phase = total_phase - mg_phase
    psqt_score = (psqt_mg_score * mg_phase + psqt_eg_score * eg_phase) / total_phase

    # Mobility evaluation
    mobility_score = len(list(board.legal_moves))
    
    # Totaling scores
    material_weight = 10
    psqt_weight = 1
    mobility_weight = 1
    piece_specific_weight = 1
    score = (material_weight * material_score) \
            + (psqt_weight * psqt_score) \
            + (mobility_weight * mobility_score) \
            + (piece_specific_weight * piece_specific_score)
    return score
        