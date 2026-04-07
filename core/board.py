import numpy as np
import sys
import os
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))
import chess
import chess.polyglot
import config
from . import piece_moves
import zobrist

class Board():
    def __init__(self):

        # 8*8的空白棋盤
        self.board = np.zeros((8, 8), dtype=int)

        # 白子先走
        self.turn = config.WHITE

        #王,堡有沒有動過
        self.white_king_moved = False
        self.black_king_moved = False

        self.white_Hrook_moved = False
        self.white_Arook_moved = False
        self.black_Hrook_moved = False
        self.black_Arook_moved = False

        #過路兵
        self.en_passant = None

        self.setup_board()
        self.history = []

        self.zobrist_key = 0

        self.white_king_pos = (7, 4)
        self.black_king_pos = (0, 4)

    def setup_board(self):

        # 初始化棋盤-Pawn
        self.board[1] = config.PAWN * config.BLACK
        self.board[6] = config.PAWN * config.WHITE

        # 底線棋子(順序)
        pieces = [
            config.ROOK,
            config.KNIGHT,
            config.BISHOP,
            config.QUEEN,
            config.KING,
            config.BISHOP,
            config.KNIGHT,
            config.ROOK
        ]

        self.board[0] = np.array(pieces) * config.BLACK
        self.board[7] = np.array(pieces) * config.WHITE

        self.zobrist_key = zobrist.compute_initial_hash(self)

    def display(self):

        pieces_map = {
            0: " . ",
            1: " wP", -1: " bP",
            2: " wN", -2: " bN",
            3: " wB", -3: " bB",
            4: " wR", -4: " bR",
            5: " wQ", -5: " bQ",
            6: " wK", -6: " bK"
        }

        print("\n")
        for r in range(8):
            print(f"{8-r}", end=" ")
            for c in range(8):
                piece_code = self.board[r][c]
                print(pieces_map[piece_code], end="")
            print(" ")

        print("   a  b  c  d  e  f  g  h\n")

    def to_algebraic(self, coord):
        r, c = coord
        
        #字母表
        files = "abcdefgh"
        
        #查表找出字母
        file_str = files[c]
        
        #計算數字
        rank_str = str(8 - r)
        
        #組合回傳
        return file_str + rank_str

    def from_algebraic(self, move_str):
        files = "abcdefgh"

        c1 = files.index(move_str[0])
        r1 = 8 - int(move_str[1])

        c2 = files.index(move_str[2])
        r2 = 8 - int(move_str[3])

        promote = config.QUEEN
        if len(move_str) == 5:
            promo_char = move_str[4]
            if promo_char == 'n': promote = config.KNIGHT
            elif promo_char == 'b': promote = config.BISHOP
            elif promo_char == 'r': promote = config.ROOK

        return (r1, c1), (r2, c2), promote

    def move(self, begin, end, promote=config.QUEEN):
        r1, c1 = begin
        r2, c2 = end

        #過路兵
        if abs(self.board[r1][c1]) == config.PAWN:
            if (r2, c2) == self.en_passant:
                self.board[r1][c2] = 0

        #castle判定
        #王,堡
        if self.board[r1][c1] == config.KING * config.WHITE:
            self.white_king_moved = True
        if self.board[r1][c1] == config.KING * config.BLACK:
            self.black_king_moved = True
        if self.board[r1][c1] == config.ROOK * config.WHITE:
            if c1 == 7:
                self.white_Hrook_moved = True
            elif c1 == 0:
                self.white_Arook_moved = True
        if self.board[r1][c1] == config.ROOK * config.BLACK:
            if c1 == 7:
                self.black_Hrook_moved = True
            elif c1 == 0:
                self.black_Arook_moved = True

        #若王入堡
        #白王
        if (r1, c1) == (7, 4) and (r2, c2) == (7, 6):
            self.board[7][5] = self.board[7][7]
            self.board[7][7] = 0
        if (r1, c1) == (7, 4) and (r2, c2) == (7, 2):
            self.board[7][3] = self.board[7][0]
            self.board[7][0] = 0
        #黑王
        if (r1, c1) == (0, 4) and (r2, c2) == (0, 6):
            self.board[0][5] = self.board[0][7]
            self.board[0][7] = 0
        if (r1, c1) == (0, 4) and (r2, c2) == (0, 2):
            self.board[0][3] = self.board[0][0]
            self.board[0][0] = 0

        #移過去
        self.board[r2][c2] = self.board[r1][c1]

        #原位empty
        self.board[r1][c1] = 0

        #Promote
        if abs(self.board[r2][c2]) == config.PAWN:
            if r2 == 0 or r2 == 7:
                color = 1 if self.board[r2][c2] > 0 else -1
                self.board[r2][c2] = promote * color

        #有沒有兩步的兵
        self.en_passant = None
        if abs(self.board[r2][c2]) == config.PAWN and abs(r2 - r1) == 2:
            mid_r = (r1 + r2) // 2
            self.en_passant = (mid_r, c1)

        #王位置
        if abs(self.board[r1][c1]) == config.KING:
            if self.board[r1][c1] > 0:
                self.white_king_pos = (r2, c2)
            else:
                self.black_king_pos = (r2, c2)

        #換下個人
        self.turn *= -1

    #確定行動合法
    def is_in_check(self, color):
        
        kr, kc = self.white_king_pos if color == 1 else self.black_king_pos
        opp = -color#對方顏色


        # 馬的攻擊
        for dr, dc in piece_moves.KNIGHT_MOVES:
            r, c = kr + dr, kc + dc
            if self.is_on_board((r, c)):
                if self.board[r][c] == config.KNIGHT * opp:
                    return True

        # 車/后（直線方向）
        for dr, dc in piece_moves.ORTHOGONAL_MOVES:
            r, c = kr, kc
            while True:
                r += dr
                c += dc
                if not self.is_on_board((r, c)):
                    break
                target = self.board[r][c]
                if target == 0:
                    continue
                if target == config.ROOK * opp or target == config.QUEEN * opp:
                    return True
                break  # 被其他棋子擋住

        # 象/后（斜線方向）
        for dr, dc in piece_moves.DIAGONAL_MOVES:
            r, c = kr, kc
            while True:
                r += dr
                c += dc
                if not self.is_on_board((r, c)):
                    break
                target = self.board[r][c]
                if target == 0:
                    continue
                if target == config.BISHOP * opp or target == config.QUEEN * opp:
                    return True
                break

        # 王的攻擊（避免兩王親親）
        for dr, dc in piece_moves.KING_MOVES:
            r, c = kr + dr, kc + dc
            if self.is_on_board((r, c)):
                if self.board[r][c] == config.KING * opp:
                    return True

        # 兵的攻擊
        pawn_attack_row = kr + (-color)
        for dc in [-1, 1]:
            c = kc + dc
            if self.is_on_board((pawn_attack_row, c)):
                if self.board[pawn_attack_row][c] == config.PAWN * opp:
                    return True

        return False

    def is_legal_move(self, begin, end, promote=config.QUEEN):
        r1, c1 = begin
        color = 1 if self.board[r1][c1] > 0 else -1

        self.make_move(begin, end, promote)
        
        in_check = self.is_in_check(color)

        self.undo_move()

        return not in_check

    #邊界Safety Guard
    def is_on_board(self, end):
        r, c = end
        return 0 <= r <= 7 and 0 <= c <= 7

    #Knight moves
    def get_knight_moves(self, begin):

        r1, c1 = begin

        #判斷移動子顏色
        color1 = 1 if self.board[r1][c1] > 0 else -1

        #確認馬合法行動
        knight_moves = []

        for dr, dc in piece_moves.KNIGHT_MOVES:
            r2, c2 = r1 + dr, c1 + dc
            if self.is_on_board((r2, c2)):
                target = self.board[r2][c2]
                target_color = (1 if target > 0 else -1) if target != 0 else 0
                if target_color != color1:
                    knight_moves.append((r2, c2))

        return knight_moves

    def get_sliding_moves(self, begin, directions):
        #保留原始點(因為要跑好多個方向)
        r_start, c_start = begin
        
        # 判斷移動子顏色
        my_color = 1 if self.board[r_start][c_start] > 0 else -1
        
        slid_moves = []

        # 每個方向
        for dr, dc in directions:
            #重置到起點
            r, c = r_start, c_start
            while True:
                r += dr
                c += dc
                if not self.is_on_board((r, c)):
                    break

                #目標訊息
                target = self.board[r][c]
                
                if target == 0:
                    slid_moves.append((r, c))
                    continue 
                
                else:
                    #判斷棋子是否同色
                    target_color = 1 if target > 0 else -1
                    
                    if target_color != my_color:
                        #可吃,加入位置並停止
                        slid_moves.append((r, c))
                        break
                    else:
                        #被同色棋擋住
                        break
                        
        return(slid_moves)

        
    def get_rook_moves(self, pos):
        
        return self.get_sliding_moves(pos, piece_moves.ORTHOGONAL_MOVES)

    def get_bishop_moves(self, pos):
        
        return self.get_sliding_moves(pos, piece_moves.DIAGONAL_MOVES)

    def get_queen_moves(self, pos):
        
        return self.get_sliding_moves(pos, piece_moves.QUEEN_MOVES)

    def get_king_moves(self, begin):

        r1, c1 = begin

        #判斷移動子顏色
        color1 = 1 if self.board[r1][c1] > 0 else -1

        #確認王合法行動
        king_moves = []

        for dr, dc in piece_moves.KING_MOVES:
            r2, c2 = r1 + dr, c1 + dc
            if self.is_on_board((r2, c2)):
                target = self.board[r2][c2]
                target_color = (1 if target > 0 else -1) if target != 0 else 0
                if target_color != color1:
                    king_moves.append((r2, c2))
        
        #入堡
        if color1 == 1:
            if not self.white_king_moved and not self.is_in_check(color1):
                if not self.white_Hrook_moved:
                    if self.board[7][5] == 0 and self.board[7][6] == 0:
                        if not self._is_square_attacked((7, 5), color1) and \
                           not self._is_square_attacked((7, 6), color1):
                            king_moves.append((7, 6))
                if not self.white_Arook_moved:
                    if self.board[7][1] == 0 and self.board[7][2] == 0 and self.board[7][3] == 0:
                        if not self._is_square_attacked((7, 3), color1) and \
                           not self._is_square_attacked((7, 2), color1):
                            king_moves.append((7, 2))
        else:
            if not self.black_king_moved and not self.is_in_check(color1):
                if not self.black_Hrook_moved:
                    if self.board[0][5] == 0 and self.board[0][6] == 0:
                        if not self._is_square_attacked((0, 5), color1) and \
                           not self._is_square_attacked((0, 6), color1):
                            king_moves.append((0, 6))
                if not self.black_Arook_moved:
                    if self.board[0][1] == 0 and self.board[0][2] == 0 and self.board[0][3] == 0:
                        if not self._is_square_attacked((0, 3), color1) and \
                           not self._is_square_attacked((0, 2), color1):
                            king_moves.append((0, 2))
            
        return(king_moves)

    def _is_square_attacked(self, square, color):

        sr, sc = square
        king_val = config.KING * color
        opp = -color

        old_val = self.board[sr][sc]
        king_r, king_c = None, None
        for r in range(8):
            for c in range(8):
                if self.board[r][c] == king_val:
                    king_r, king_c = r, c
                    break
            if king_r is not None:
                break

        self.board[king_r][king_c] = 0
        self.board[sr][sc] = king_val

        attacked = self.is_in_check(color)

        # 還原
        self.board[sr][sc] = old_val
        self.board[king_r][king_c] = king_val

        return attacked

    def get_pawn_moves(self, begin):
         
        r1, c1 = begin
        pawn_moves = []

        #若是白子
        if self.board[r1][c1] > 0:
            color1 = 1
            direction = -1
            start_r = 6 #拿做判斷能不能走兩步
        else:
            color1 = -1
            direction = 1
            start_r = 1

        #直走1步 -> 看能否兩步
        r2, c2 = r1 + direction, c1
        if self.is_on_board((r2,c2)):
            if self.board[r2][c2] == 0:
                pawn_moves.append((r2,c2))
                if r1 == start_r:
                    r2b, c2b = r1 + (2 * direction), c1
                    if self.board[r2b][c2b] == 0:
                         pawn_moves.append((r2b,c2b))
        
        #斜向吃(後來發現可以整合但已經寫了)
        r2 = r1 + direction
        for dc in [1, -1]:
            c2 = c1 + dc
            if self.is_on_board((r2, c2)):
                target = self.board[r2][c2]
                if (color1 == 1 and target < 0) or \
                   (color1 == -1 and target > 0) or \
                   (r2, c2) == self.en_passant:
                    pawn_moves.append((r2, c2))
        
        return(pawn_moves)
    
    def get_all_legal_moves(self, color):

        all_moves = []

        for r in range(8):
            for c in range(8):
                piece = self.board[r][c]
                if piece == 0 or np.sign(piece) != color:
                    continue

                start_pos = (r, c)
                abs_piece = abs(piece)

                if abs_piece == config.PAWN:
                    candidates = self.get_pawn_moves(start_pos)
                elif abs_piece == config.ROOK:
                    candidates = self.get_rook_moves(start_pos)
                elif abs_piece == config.KNIGHT:
                    candidates = self.get_knight_moves(start_pos)
                elif abs_piece == config.BISHOP:
                    candidates = self.get_bishop_moves(start_pos)
                elif abs_piece == config.QUEEN:
                    candidates = self.get_queen_moves(start_pos)
                elif abs_piece == config.KING:
                    candidates = self.get_king_moves(start_pos)
                else:
                    candidates = []

                for end_pos in candidates:
                    if self.is_legal_move(start_pos, end_pos):
                        all_moves.append((start_pos, end_pos))

        return all_moves
    def get_capture_moves(self, color):
        
        legal_moves = self.get_all_legal_moves(color)
        capture_moves = []

        for move in legal_moves:
            begin, end = move
            r1, c1 = begin
            r2, c2 = end

            attacker_piece = self.board[r1][c1]
            target_piece = self.board[r2][c2]

            # 判斷是否為過路兵吃子
            is_en_passant = (abs(attacker_piece) == config.PAWN and (r2, c2) == self.en_passant)

            if target_piece != 0 or is_en_passant:
                if is_en_passant:
                    victim_val = config.MG_value.get(config.PAWN, 0)
                else:
                    victim_val = config.MG_value.get(abs(target_piece), 0)
                
                attacker_val = config.MG_value.get(abs(attacker_piece), 0)

                #MVV-LVA評分：越有價值的要被吃掉
                #乘上10放大受害者的重要性
                score = (victim_val * 10) - attacker_val
                
                capture_moves.append((score, move))

        # 依照分數由大到小排序
        capture_moves.sort(key=lambda x: x[0], reverse=True)

        return [move for score, move in capture_moves]
    
    def is_checkmate(self, color):

        return self.is_in_check(color) and len(self.get_all_legal_moves(color)) == 0

    def is_stalemate(self, color):

        return not self.is_in_check(color) and len(self.get_all_legal_moves(color)) == 0

    def make_move(self, begin, end, promote=config.QUEEN):
        r1, c1 = begin
        r2, c2 = end
        moving_piece = self.board[r1][c1]
        target_piece = self.board[r2][c2] 

        state = {
            'begin': begin,
            'end': end,
            'moving_piece': moving_piece,
            'target_piece': target_piece,
            'turn': self.turn,
            'wkm': self.white_king_moved,
            'bkm': self.black_king_moved,
            'whr': self.white_Hrook_moved,
            'war': self.white_Arook_moved,
            'bhr': self.black_Hrook_moved,
            'bar': self.black_Arook_moved,
            'ep': self.en_passant,
            'zobrist_key': self.zobrist_key 
        }
        self.history.append(state)
        
        r1, c1 = begin
        r2, c2 = end
        moving_piece = self.board[r1][c1]
        target_piece = self.board[r2][c2]
        
        if not self.white_king_moved and not self.white_Hrook_moved: self.zobrist_key ^= zobrist.CASTLING[0]
        if not self.white_king_moved and not self.white_Arook_moved: self.zobrist_key ^= zobrist.CASTLING[1]
        if not self.black_king_moved and not self.black_Hrook_moved: self.zobrist_key ^= zobrist.CASTLING[2]
        if not self.black_king_moved and not self.black_Arook_moved: self.zobrist_key ^= zobrist.CASTLING[3]
        if self.en_passant: self.zobrist_key ^= zobrist.EN_PASSANT[self.en_passant[1]]
        
        #讓move改變陣列和flag
        self.move(begin, end, promote) 
        
        
        self.zobrist_key ^= zobrist.PIECES[zobrist.piece_to_index(moving_piece)][r1 * 8 + c1]
        
        if target_piece != 0:
            self.zobrist_key ^= zobrist.PIECES[zobrist.piece_to_index(target_piece)][r2 * 8 + c2]

        if abs(moving_piece) == config.PAWN and target_piece == 0 and c1 != c2:

            ep_r = r1 
            ep_pawn = config.PAWN * (-1 if moving_piece > 0 else 1)
            self.zobrist_key ^= zobrist.PIECES[zobrist.piece_to_index(ep_pawn)][ep_r * 8 + c2]


        placed_piece = self.board[r2][c2]
        self.zobrist_key ^= zobrist.PIECES[zobrist.piece_to_index(placed_piece)][r2 * 8 + c2]

        if abs(moving_piece) == config.KING and abs(c2 - c1) == 2:
            if c2 == 6: 
                rook = self.board[r2][5]
                self.zobrist_key ^= zobrist.PIECES[zobrist.piece_to_index(rook)][r2 * 8 + 7]
                self.zobrist_key ^= zobrist.PIECES[zobrist.piece_to_index(rook)][r2 * 8 + 5]
            elif c2 == 2:
                rook = self.board[r2][3]
                self.zobrist_key ^= zobrist.PIECES[zobrist.piece_to_index(rook)][r2 * 8 + 0]
                self.zobrist_key ^= zobrist.PIECES[zobrist.piece_to_index(rook)][r2 * 8 + 3]

        if not self.white_king_moved and not self.white_Hrook_moved: self.zobrist_key ^= zobrist.CASTLING[0]
        if not self.white_king_moved and not self.white_Arook_moved: self.zobrist_key ^= zobrist.CASTLING[1]
        if not self.black_king_moved and not self.black_Hrook_moved: self.zobrist_key ^= zobrist.CASTLING[2]
        if not self.black_king_moved and not self.black_Arook_moved: self.zobrist_key ^= zobrist.CASTLING[3]
        if self.en_passant: self.zobrist_key ^= zobrist.EN_PASSANT[self.en_passant[1]]
        
        self.zobrist_key ^= zobrist.BLACK_TO_MOVE

    def undo_move(self):
        if not self.history:
            return
            
        state = self.history.pop()
        
        # 1. 還原各種標記與 Zobrist Hash
        self.turn = state['turn']
        self.white_king_moved = state['wkm']
        self.black_king_moved = state['bkm']
        self.white_Hrook_moved = state['whr']
        self.white_Arook_moved = state['war']
        self.black_Hrook_moved = state['bhr']
        self.black_Arook_moved = state['bar']
        self.en_passant = state['ep']
        self.zobrist_key = state['zobrist_key'] 
        
        begin_r, begin_c = state['begin']
        end_r, end_c = state['end']
        
        self.board[begin_r][begin_c] = state['moving_piece']
        self.board[end_r][end_c] = state['target_piece']
        

        if abs(state['moving_piece']) == config.KING and abs(end_c - begin_c) == 2:
            if end_c == 6:
                self.board[begin_r][7] = self.board[begin_r][5]
                self.board[begin_r][5] = 0
            elif end_c == 2:
                self.board[begin_r][0] = self.board[begin_r][3]
                self.board[begin_r][3] = 0
                
        if abs(state['moving_piece']) == config.PAWN and state['target_piece'] == 0 and begin_c != end_c:
        
            ep_color = -1 if state['moving_piece'] > 0 else 1
            self.board[begin_r][end_c] = config.PAWN * ep_color
        
        if abs(state['moving_piece']) == config.KING:
            if state['moving_piece'] > 0:
                self.white_king_pos = state['begin']
            else:
                self.black_king_pos = state['begin']


    def get_fen(self):
        fen = {
            1: 'P', -1: 'p',
            2: 'N', -2: 'n',
            3: 'B', -3: 'b',
            4: 'R', -4: 'r',
            5: 'Q', -5: 'q',
            6: 'K', -6: 'k'
        }

        #棋盤狀況
        Fen = ''
        for i in range(8):
            blank = 0
            for j in range(8):
                piece = self.board[i][j]
                if piece == 0:
                    blank += 1
                else:
                    if blank > 0:
                        Fen += str(blank)
                        blank = 0
                    
                    Fen += fen[piece]
            
            if blank > 0:
                Fen += str(blank)

            if i < 7:
                Fen += '/'

        #輪到誰
        Fen += ' '
        Fen += 'w' if self.turn == 1 else 'b'

        #入堡狀況
        Fen += ' '
        castling = ''
        
        #白短
        if not self.white_king_moved and not self.white_Hrook_moved: castling += 'K'
        #白長
        if not self.white_king_moved and not self.white_Arook_moved: castling += 'Q'
        #黑短
        if not self.black_king_moved and not self.black_Hrook_moved: castling += 'k'
        #黑長
        if not self.black_king_moved and not self.black_Arook_moved: castling += 'q'
        Fen += castling if castling else '-'

        #過路兵
        Fen += ' '
        if self.en_passant != None:
            Fen += self.to_algebraic(self.en_passant)
        else:
            Fen += '-'

        Fen += ' 0 1'

        return(Fen)

    def load_fen(self, fen_str):
        # 將 FEN 字串用「空格」切成不同區塊
        parts = fen_str.split()
        
        # --- 1. 還原棋盤陣列 ---
        self.board = np.zeros((8, 8), dtype=int)
        piece_map = {
            'P': 1, 'N': 2, 'B': 3, 'R': 4, 'Q': 5, 'K': 6,
            'p': -1, 'n': -2, 'b': -3, 'r': -4, 'q': -5, 'k': -6
        }
        
        # 依照 '/' 切割出 8 個橫列
        rows = parts[0].split('/')
        for r in range(8):
            c = 0
            for char in rows[r]:
                if char.isdigit():
                    # 如果是數字，代表連續的空格，Column 索引要往後推
                    c += int(char)
                else:
                    # 如果是字母，就把對應的數字放進棋盤
                    self.board[r][c] = piece_map[char]
                    c += 1
                    
        # --- 2. 還原輪次 ---
        self.turn = 1 if parts[1] == 'w' else -1
        
        # --- 3. 還原入堡權限 ---
        # 簡單暴力法：如果沒看到大寫 K，就當作白方國王或短車已經動過了，失去權利
        castling = parts[2]
        self.white_king_moved  = 'K' not in castling and 'Q' not in castling
        self.white_Hrook_moved = 'K' not in castling
        self.white_Arook_moved = 'Q' not in castling
        self.black_king_moved  = 'k' not in castling and 'q' not in castling
        self.black_Hrook_moved = 'k' not in castling
        self.black_Arook_moved = 'q' not in castling
        
        # --- 4. 還原過路兵 ---
        if parts[3] != '-':
            files = "abcdefgh"
            ep_c = files.index(parts[3][0])
            ep_r = 8 - int(parts[3][1])
            self.en_passant = (ep_r, ep_c)
        else:
            self.en_passant = None

        self.zobrist_key = zobrist.compute_initial_hash(self)
            
        print("GET！")

    def get_book_move(self, book_path):
        fen = self.get_fen()
        board = chess.Board(fen)

        try:
            with chess.polyglot.open_reader(book_path) as reader:
                entry = reader.find(board)
                move_str = entry.move.uci()
                return self.from_algebraic(move_str)
        except IndexError:
            return None
        except FileNotFoundError:
            print("Path wrong!!!")
            return None


if __name__ == "__main__":
    game = Board()
    game.display()