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

    Material score values from Tomasz Michniewski's Simplified Evaluation Function
    Piece-squares table values and tapered evaluation from Ronald Friederich's PeSTO's Evaluation Function

    TODO
    - fine tune weights
    - pawn structure
    - king safety
    - Texel's tuning method
    - king pawn tropism
    - center control?

    gives bonus to:
    - batteries
    - rooks on 7th (and 8th?) rank
    - passed pawns (the further it is, the higher the bonus)
    - moves that control the center, espically with pawns
    - moves that prevent opponent from castling
    - outposts (either knight or bishop)
    - bishops on long diagonal that can see both center squares

    penalize:
    - undefended knights and bishops
    - doubled pawns (triple too, etc etc)
    - moves that trade while behind material
    - developing queen early
    - trading fianchettoed bishops
    - rooks on closed files
    - rooks trapped by the king. penalty worsens if king cannot castle
    - BISHOP: penalty depending on how many friendly pawns on the same color square as bishop,
      smaller penalty when bishop is outside pawn chain
    """
    if ENDGAME_BOOK and get_num_pieces(board) <= 5:
        return eval_endgame(board)

    material_values = {
        "P": 100,
        "N": 320,
        "B": 330,
        "R": 500,
        "Q": 900,
        "K": MATE_SCORE
    }
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
    phase_scores = {
        "P": 0,
        "N": 1,
        "B": 1,
        "R": 2,
        "Q": 4,
        "K": 0
    }

    material_score = 0
    psqt_mg_score = 0
    psqt_eg_score = 0
    phase = 0
    total_phase = 16*phase_scores["P"] + 4*phase_scores["N"] + 4*phase_scores["B"] + 4*phase_scores["R"] + 2*phase_scores["Q"]
    piece_specific_score = 0

    # Piece-specific score bonuses
    rook_open_file_bonus = 100

    piece_map = board.piece_map()

    for square in piece_map:
        piece = piece_map[square]
        piece_symbol = piece.symbol()
        piece_raw = piece_symbol.upper()

        relative_weight = 1 if piece.color == board.turn else -1
        
        # Material evaluation
        material_score += material_values[piece_raw] * relative_weight

        # PSQT evaluation part 1
        psqt_mg_score += mg_psqts[piece_symbol][7 - square // 8][square % 8] * relative_weight
        psqt_eg_score += eg_psqts[piece_symbol][7 - square // 8][square % 8] * relative_weight
        phase += phase_scores[piece_raw]

        # Piece-specific evaluation
        if piece_raw == "R":
            rook_file = chess.BB_FILES[chess.square_file(square)]
            bb_rook_file = chess.SquareSet(rook_file)

            # Rook on open file
            bb_friend_pawns = board.pieces(chess.PAWN, piece.color)
            bb_foe_pawns = board.pieces(chess.PAWN, not piece.color)
            if len(bb_rook_file & bb_friend_pawns) == 0:
                if len(bb_rook_file & bb_foe_pawns) == 0:
                    piece_specific_score += rook_open_file_bonus * relative_weight
                else:
                    piece_specific_score += rook_open_file_bonus / 2 * relative_weight

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
        