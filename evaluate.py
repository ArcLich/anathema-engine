"""
Not Magnus
Classical chess engine by Devin Zhang
Evaluation functions which score a given position
"""
import os
import chess.gaviota
from evaluation_values import *
from util import *


def is_square_A_file(square):
    """
    Returns true if the square is on the A file
    """
    return square % 8 == 0


def is_square_H_file(square):
    """
    Returns true if the square is on the H file
    """
    return (square + 1) % 8 == 0


def get_bb_king_zone(square, color):
    """
    Gets the king zone (the ring around the king plus 3 more squares facing the enemy)
    bitboard for the given side
    """
    king_rank = chess.BB_RANKS[chess.square_rank(square)]
    bb_king_ranks = chess.SquareSet(king_rank)
    if color == chess.WHITE:
        if square + 8 <= 63:
            king_forward_rank = chess.BB_RANKS[chess.square_rank(square) + 1]
            bb_king_ranks |= chess.SquareSet(king_forward_rank)
            if square + 16 <= 63:
                king_forward_rank = chess.BB_RANKS[chess.square_rank(square) + 2]
                bb_king_ranks |= chess.SquareSet(king_forward_rank)
        if square - 8 >= 0:
            king_back_rank = chess.BB_RANKS[chess.square_rank(square) - 1]
            bb_king_ranks |= chess.SquareSet(king_back_rank)
    else:
        if square - 8 >= 0:
            king_forward_rank = chess.BB_RANKS[chess.square_rank(square) - 1]
            bb_king_ranks |= chess.SquareSet(king_forward_rank)
            if square - 16 >= 0:
                king_forward_rank = chess.BB_RANKS[chess.square_rank(square) - 2]
                bb_king_ranks |= chess.SquareSet(king_forward_rank)
        if square + 8 <= 63:
            king_back_rank = chess.BB_RANKS[chess.square_rank(square) + 1]
            bb_king_ranks |= chess.SquareSet(king_back_rank)

    king_file = chess.BB_FILES[chess.square_file(square)]
    bb_king_files = chess.SquareSet(king_file)
    if not is_square_A_file(square):
        king_left_file = chess.BB_FILES[chess.square_file(square - 1)]
        bb_king_files |= chess.SquareSet(king_left_file)
    if not is_square_H_file(square):
        king_right_file = chess.BB_FILES[chess.square_file(square + 1)]
        bb_king_files |= chess.SquareSet(king_right_file)

    bb_king_zone = bb_king_ranks & bb_king_files
    return bb_king_zone


def get_square_color(square):
    """
    Given a square on the board return whether
    its a dark square or a light square
    """
    if (square % 8) % 2 == (square // 8) % 2:
        return chess.BLACK
    return chess.WHITE


def eval_endgame(board):
    """
    Evaluates an endgame position with 5 or less pieces
    Returns depth-to-mate from Gaviota endgame tablebase
    """
    with chess.gaviota.open_tablebase(os.path.dirname(os.path.realpath(__file__)) + ENDGAME_BOOK_LOCATION) as tablebase: # https://chess.cygnitec.com/tablebases/gaviota/
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
    - Pawn hash table

    Gives bonuses to:
    - Rooks on open and semi-open files
    - Passed pawns
    - Knights/bishops on outposts (squares on rank 4, 5, or 6 defended by a friendly pawn)
    - Attacks on the enemy king zone (ring around the king plus 3 forward squares towards the enemy)
    - Pawn moves that gain space

    Penalizes
    - Pinned queens
    - Friendly pawns that are on the same colored square as the bishop
    - Isolated pawns
    - Rooks trapped by king, more so if king cannot castle
    
    Material score values from Tomasz Michniewski's Simplified Evaluation Function
    Tapered evaluation and piece-square table values from Ronald Friederich's PeSTO's Evaluation Function
    Other select values from Stockfish

    TODO
    - fine tune weights and values (Texel's tuning method)
    """
    game_state = get_game_state(board)
    if game_state == 1: # Game is checkmate
        return -MATE_SCORE
    elif 2 <= game_state <= 5: # Game is drawn
        return 0

    if ENDGAME_BOOK and get_num_pieces(board) <= 5:
        return eval_endgame(board)

    # Init tapered evaluation
    phase_scores = (0, 0, 1, 1, 2, 4, 0)
    phase = 0
    total_phase = 16*phase_scores[chess.PAWN] + 4*phase_scores[chess.KNIGHT] + 4*phase_scores[chess.BISHOP] \
                + 4*phase_scores[chess.ROOK] + 2*phase_scores[chess.QUEEN]

    # Init scores
    material_score = 0

    psqt_mg_score = 0
    psqt_eg_score = 0
    psqt_score = 0

    mobility_score = 0

    piece_specific_mg_score = 0
    piece_specific_eg_score = 0
    piece_specific_score = 0

    # Part of piece specific score, saved to pawn hash table by itself
    pawn_mg_score = 0
    pawn_eg_score = 0

    # Init bitboards
    occupied = board.occupied
    b_bitboards = [0, 0, 0, 0, 0, 0, 0]
    w_bitboards = [0, 0, 0, 0, 0, 0, 0]
    bitboards = [b_bitboards, w_bitboards]

    for color in [chess.WHITE, chess.BLACK]:
        for piece in [chess.PAWN, chess.KNIGHT, chess.BISHOP, chess.ROOK, chess.QUEEN, chess.KING]:
            squares = []
            bb = board.pieces(piece, color)
            for i, c in enumerate(bin(bb)[:1:-1], 1):
                if c == "1":
                    squares.append(i - 1)
            bitboards[color][piece] = (squares, bb)

    # Evaluation
    pawn_hash_in_table = False
    pawn_hash_key = (bin(bitboards[chess.WHITE][chess.PAWN][1]), bin(bitboards[chess.BLACK][chess.PAWN][1]))
    if pawn_hash_key in pawn_hash_table:
        pawn_mg_score, pawn_eg_score = pawn_hash_table[pawn_hash_key]
        pawn_hash_in_table = True

    for color in [chess.WHITE, chess.BLACK]:
        relative_weight = 1 if color == board.turn else -1

        friend_king_square = bitboards[color][chess.KING][0][0]
        enemy_king_square = bitboards[not color][chess.KING][0][0]

        bb_king_zone = get_bb_king_zone(enemy_king_square, not color) # Initialize enemy king zone, bonus applied to attacks on the enemy king zone
        king_attack_units = 0

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

                # Piece-specific evaluation part 1
                if piece == chess.PAWN:
                    if not pawn_hash_in_table:
                        # Penalty to bishop by number of pawns on bishop's square color
                        bishop_squares = bitboards[color][chess.BISHOP][0]
                        if len(bishop_squares) != 2: # Technically incorrect, but situations with 2+ same colored bishops are unlikely
                            for bishop_square in bishop_squares:
                                if get_square_color(square) == get_square_color(bishop_square):
                                    pawn_mg_score += pawn_bishop_mg_penalty * relative_weight
                                    pawn_eg_score += pawn_bishop_eg_penalty * relative_weight

                        # Bonus to passed pawn
                        pawn_file = chess.BB_FILES[chess.square_file(square)]
                        bb_passing_files = chess.SquareSet(pawn_file)
                        if not is_square_A_file(square):
                            pawn_left_file = chess.BB_FILES[chess.square_file(square - 1)]
                            bb_passing_files |= chess.SquareSet(pawn_left_file)
                        if not is_square_H_file(square):
                            pawn_right_file = chess.BB_FILES[chess.square_file(square + 1)]
                            bb_passing_files |= chess.SquareSet(pawn_right_file)
                        if len(bb_passing_files & bitboards[not color][chess.PAWN][1]) == 0:
                            if color == chess.WHITE:
                                pawn_mg_score += passed_pawn_mg_bonus[square // 8] * relative_weight
                                pawn_eg_score += passed_pawn_eg_bonus[square // 8] * relative_weight
                            else:
                                pawn_mg_score += passed_pawn_mg_bonus[8 - ((square // 8) + 1)] * relative_weight
                                pawn_eg_score += passed_pawn_eg_bonus[8 - ((square // 8) + 1)] * relative_weight

                        # Penalty to isolated pawn
                        if len(bb_passing_files & bitboards[color][chess.PAWN][1]) != 3:
                            pawn_mg_score += pawn_isolated_mg_penalty * relative_weight
                            pawn_eg_score += pawn_isolated_eg_penalty * relative_weight
                        
                        # Bonus to space, defined by number of squares behind pawn (including the pawn's square itself)
                        rank = chess.square_rank(square) + 1
                        if color == chess.WHITE:
                            pawn_mg_score += rank * pawn_space_mg_bonus * relative_weight
                            pawn_eg_score += rank * pawn_space_eg_bonus * relative_weight
                        else:
                            pawn_mg_score += (9 - rank) * pawn_space_mg_bonus * relative_weight
                            pawn_eg_score += rank * pawn_space_eg_bonus * relative_weight

                elif piece == chess.KNIGHT:
                    # Bonus to knight on outpost (a square on rank 4, 5, or 6 defended by a friendly pawn)
                    bb_pawns = bitboards[color][chess.PAWN][1]
                    rank = chess.square_rank(square) + 1
                    if (color == chess.WHITE and (rank == 4 or rank == 5 or rank == 6)) or \
                        ((color == chess.BLACK) and (rank == 5 or rank == 4 or rank == 3)):
                            if len(board.attackers(color, square) & bb_pawns) >= 1:
                                piece_specific_mg_score += outpost_mg_bonus * relative_weight
                                piece_specific_eg_score += outpost_eg_bonus * relative_weight

                    # Bonus to attacks on the enemy king zone
                    king_attack_units += len(board.attacks(square) & bb_king_zone) * 2

                    # Bonus to mobility by how many squares can be moved to
                    mobility_score += count_bin(chess.BB_KNIGHT_ATTACKS[square] & ~occupied)

                elif piece == chess.BISHOP:
                    # Bonus to bishop on outpost (a square on rank 4, 5, or 6 defended by a friendly pawn)
                    bb_pawns = bitboards[color][chess.PAWN][1]
                    rank = chess.square_rank(square) + 1
                    if (color == chess.WHITE and (rank == 4 or rank == 5 or rank == 6)) or \
                        ((color == chess.BLACK) and (rank == 5 or rank == 4 or rank == 3)):
                            if len(board.attackers(color, square) & bb_pawns) >= 1:
                                piece_specific_mg_score += outpost_mg_bonus * relative_weight
                                piece_specific_eg_score += outpost_eg_bonus * relative_weight

                    # Bonus to attacks on the enemy king zone
                    king_attack_units += len(board.attacks(square) & bb_king_zone) * 2

                    # Bonus to mobility by how many squares can be moved to
                    mobility_score += count_bin(chess.BB_DIAG_ATTACKS[square][chess.BB_DIAG_MASKS[square] & occupied] & ~occupied)

                elif piece == chess.ROOK:
                    # Bonus to rook on open file
                    rook_file = chess.BB_FILES[chess.square_file(square)]
                    bb_rook_file = chess.SquareSet(rook_file)
                    bb_friend_pawns = bitboards[color][chess.PAWN][1]
                    bb_foe_pawns = bitboards[not color][chess.PAWN][1]
                    if len(bb_rook_file & bb_friend_pawns) == 0:
                        if len(bb_rook_file & bb_foe_pawns) == 0:
                            piece_specific_mg_score += rook_open_file_mg_bonus * relative_weight
                            piece_specific_eg_score += rook_open_file_eg_bonus * relative_weight
                        else:
                            piece_specific_mg_score += rook_semiopen_file_mg_bonus * relative_weight
                            piece_specific_eg_score += rook_semiopen_file_eg_bonus * relative_weight

                    # Bonus to attacks on the enemy king zone
                    king_attack_units += len(board.attacks(square) & bb_king_zone) * 3

                    # Bonus to mobility by how many squares can be moved to
                    mobility_score += count_bin((chess.BB_RANK_ATTACKS[square][chess.BB_RANK_MASKS[square] & occupied] \
                                               | chess.BB_FILE_ATTACKS[square][chess.BB_FILE_MASKS[square] & occupied]) & ~occupied)

                    # Penalty if trapped by king, more so if king cannot castle
                    rook_file = chess.square_file(square) + 1
                    king_file = chess.square_file(friend_king_square) + 1
                    if king_file <= 4 and rook_file < king_file:
                        if board.has_queenside_castling_rights(color):
                            piece_specific_mg_score += rook_trapped_mg_penalty * relative_weight
                            piece_specific_eg_score += rook_open_file_eg_bonus * relative_weight
                        else:
                            piece_specific_mg_score += rook_trapped_nocastle_mg_penalty * relative_weight
                            piece_specific_eg_score += rook_trapped_nocastle_eg_penalty * relative_weight
                    elif king_file >= 5 and rook_file > king_file:
                        if board.has_kingside_castling_rights(color):
                            piece_specific_mg_score += rook_trapped_mg_penalty * relative_weight
                            piece_specific_eg_score += rook_open_file_eg_bonus * relative_weight
                        else:
                            piece_specific_mg_score += rook_trapped_nocastle_mg_penalty * relative_weight
                            piece_specific_eg_score += rook_trapped_nocastle_eg_penalty * relative_weight

                elif piece == chess.QUEEN:
                    # Penalty to pinned queen
                    squares_foe_sliders = bitboards[not color][chess.BISHOP][0] + bitboards[not color][chess.ROOK][0] + bitboards[not color][chess.QUEEN][0]
                    bb_foe_sliders = chess.SquareSet(chess.BB_EMPTY)
                    for foe_square in squares_foe_sliders:
                        bb_foe_sliders |= board.attacks(foe_square)
                    if board.attacks(square) & bb_foe_sliders != 0:
                        piece_specific_mg_score += queen_pinned_mg_penalty * relative_weight
                        piece_specific_eg_score += queen_pinned_eg_penalty * relative_weight

                    # Bonus to attacks on the enemy king zone
                    king_attack_units += len(board.attacks(square) & bb_king_zone) * 5

                    # Bonus to mobility by how many squares can be moved to
                    mobility_score += count_bin((chess.BB_RANK_ATTACKS[square][chess.BB_RANK_MASKS[square] & occupied] \
                                               | chess.BB_FILE_ATTACKS[square][chess.BB_FILE_MASKS[square] & occupied] \
                                               | chess.BB_DIAG_ATTACKS[square][chess.BB_DIAG_MASKS[square] & occupied]) & ~occupied)

        # Bonus to attacks on the enemy king zone
        king_attack_units = min(king_attack_units, 61)
        piece_specific_score += king_threat_table[king_attack_units] * relative_weight

    # Score pawn evaluation in pawn hash table
    pawn_hash_table[pawn_hash_key] = (pawn_mg_score, pawn_eg_score)

    # Tapered evaluation
    mg_phase = max(phase, total_phase)
    eg_phase = total_phase - mg_phase
    
    # PSQT evaluation part 2
    psqt_score = (psqt_mg_score * mg_phase + psqt_eg_score * eg_phase) / total_phase

    # Piece-specific evaluation part 1
    piece_specific_mg_score += pawn_mg_score
    piece_specific_eg_score += pawn_eg_score
    piece_specific_score += (piece_specific_mg_score * mg_phase + piece_specific_eg_score * eg_phase) / total_phase
    
    # Totaling scores
    material_weight = 10
    psqt_weight = 1
    mobility_weight = 1
    piece_specific_weight = 1
    score = (material_weight * material_score) \
            + (psqt_weight * psqt_score) \
            + (mobility_weight * mobility_score) \
            + (piece_specific_weight * piece_specific_score) \
            + 1 # Add one so evaluations of 0 are not confused with draw scores
    return score
