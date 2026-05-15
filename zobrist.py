import random

#12 種棋子 * 64 格
PIECES = [[random.getrandbits(64) for _ in range(64)] for _ in range(12)]

#黑方
BLACK_TO_MOVE = random.getrandbits(64)

#入堡
CASTLING = [random.getrandbits(64) for _ in range(4)]

#過路兵
EN_PASSANT = [random.getrandbits(64) for _ in range(8)]

def piece_to_index(piece):
    if piece > 0:
        return piece - 1
    else:
        return abs(piece) + 5
        
def compute_initial_hash(board_obj):
    h = 0
    for r in range(8):
        for c in range(8):
            piece = board_obj.board[r][c]
            if piece != 0:
                h ^= PIECES[piece_to_index(piece)][r * 8 + c]
                
    if board_obj.turn == -1:
        h ^= BLACK_TO_MOVE
        
    if not board_obj.white_king_moved and not board_obj.white_Hrook_moved: h ^= CASTLING[0]
    if not board_obj.white_king_moved and not board_obj.white_Arook_moved: h ^= CASTLING[1]
    if not board_obj.black_king_moved and not board_obj.black_Hrook_moved: h ^= CASTLING[2]
    if not board_obj.black_king_moved and not board_obj.black_Arook_moved: h ^= CASTLING[3]
    
    if board_obj.en_passant:
        h ^= EN_PASSANT[board_obj.en_passant[1]]
        
    return h