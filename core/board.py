import numpy as np
import sys
import os
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))
import chess
import chess.polyglot
import config
from . import piece_moves

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
        
    def display(self):

        # 棋子映射表
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
            # 印出行號
            print(f"{8-r}", end=" ") 
            
            # 印出棋子
            for c in range(8):
                piece_code = self.board[r][c]
                print(pieces_map[piece_code], end="")
            
            print(" ") 
        
        #行號
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


    def move(self, begin, end, promote = config.QUEEN):
        r1, c1 = begin
        r2, c2 = end

        #過路兵
        if abs(self.board[r1][c1]) == 1:
            if (r2, c2) == self.en_passant:
                self.board[r1][c2] = 0

        #castle判定
        #王,堡
        if self.board[r1][c1] == 6:
            self.white_king_moved = True
        if self.board[r1][c1] == -6:
            self.black_king_moved = True
        if self.board[r1][c1] == 4:
            if c1 == 7:
                self.white_Hrook_moved = True
            else:
                self.white_Arook_moved = True
        if self.board[r1][c1] == -4:
            if c1 == 7:
                self.black_Hrook_moved = True
            else:
                self.black_Arook_moved = True
        
        #若王入堡
        self.white_Lcastle = 0
        self.white_Scastle = 0
        self.black_Lcastle = 0
        self.black_Scastle = 0
        #白王
        if (r1, c1) == (7,4) and (r2, c2) == (7,6):
            self.board[7][5] = self.board[7][7]
            self.board[7][7] = 0
            self.white_Scastle = 1
        if (r1, c1) == (7,4) and (r2, c2) == (7,2):
            self.board[7][3] = self.board[7][0]
            self.board[7][0] = 0
            self.white_Lcastle = 1
        #黑王
        if (r1, c1) == (0,4) and (r2, c2) == (0,6):
            self.board[0][5] = self.board[0][7]
            self.board[0][7] = 0
            self.black_Scastle = 1
        if (r1, c1) == (0,4) and (r2, c2) == (0,2):
            self.board[0][3] = self.board[0][0]
            self.board[0][0] = 0
            self.black_Lcastle = 1

        #移過去
        self.board[r2][c2] = self.board[r1][c1]

        #原位empty
        self.board[r1][c1] = 0

        #Promote
        if abs(self.board[r2][c2]) == 1:
            if r2 == 0 or r2 == 7:
                
                color = 1 if self.board[r2][c2] > 0 else -1
                
                self.board[r2][c2] = promote * color
        
        #有沒有兩步的兵
        self.en_passant = None
        if abs(self.board[r2][c2]) == 1 and abs(r2 - r1) == 2:
            mid_r = (r1 + r2) // 2
            self.en_passant = (mid_r, c1)

        #換下個人
        self.turn *= -1
    
    #邊界Safety Guard
    def is_on_board(self, end):
        r,c = end

        if r > 7 or r < 0 or c > 7 or c < 0:
            return(False)
        else:
            return(True)
    
    #Knight moves
    def get_knight_moves(self, begin):

        r1, c1 = begin

        #判斷移動子顏色
        color1 = 1 if self.board[r1][c1] > 0 else -1

        #確認馬合法行動
        knight_moves = []

        for i in range(len(piece_moves.KNIGHT_MOVES)):
            
            #移動表對照下的移動位置
            dr, dc = piece_moves.KNIGHT_MOVES[i]
            end = [r1+dr, c1+dc]
            

            #邊界檢查
            if self.is_on_board(end) :
                if self.board[r1+dr][c1+dc] > 0:
                        color2 = 1
                elif self.board[r1+dr][c1+dc] < 0:
                        color2 = -1
                else:
                        color2 = 0

                if color1 != color2 or color2 == 0:
                    knight_moves.append(end)
                else:
                    continue
            else:
                continue

        return(knight_moves)

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
                
                #出界停止
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

        for i in range(len(piece_moves.KING_MOVES)):
            
            #移動表對照下的移動位置
            dr, dc = piece_moves.KING_MOVES[i]
            end = [r1+dr, c1+dc]
            

            #邊界檢查
            if self.is_on_board(end) :
                if self.board[r1+dr][c1+dc] > 0:
                        color2 = 1
                elif self.board[r1+dr][c1+dc] < 0:
                        color2 = -1
                else:
                        color2 = 0

                if color1 != color2 or color2 == 0:
                    king_moves.append(end)
                else:
                    continue
            else:
                continue
        
        #入堡
        if color1 == 1:
            if self.white_king_moved == False:
                if self.white_Arook_moved == False:
                    for i in range(1,4):
                        if self.board[7][i] != 0:
                            break
                        if i == 3:
                            king_moves.append((7,2))
                if self.white_Hrook_moved == False:
                    for i in range(5,7):
                        if self.board[7][i] != 0:
                            break
                        if i == 6:
                            king_moves.append((7,6))
        else:
            if self.black_king_moved == False:
                if self.black_Arook_moved == False:
                    for i in range(1,4):
                        if self.board[0][i] != 0:
                            break
                        if i == 3:
                            king_moves.append((0,2))
                if self.black_Hrook_moved == False:
                    for i in range(5,7):
                        if self.board[0][i] != 0:
                            break
                        if i == 6:
                            king_moves.append((0,6))
            
        return(king_moves)  
    
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
                    r2, c2 = r1 + (2*direction), c1
                    if self.board[r2][c2] == 0:
                         pawn_moves.append((r2,c2))
        
        #斜向吃(後來發現可以整合但已經寫了)
        if color1 == 1:
            r2 = r1 + direction
            
            #右前
            c2 = c1 + 1
            if self.is_on_board((r2,c2)):
                if self.board[r2][c2] < 0 or (r2, c2) == self.en_passant:
                    pawn_moves.append((r2,c2))

            #左前
            c2 = c1 - 1
            if self.is_on_board((r2,c2)):
                if self.board[r2][c2] < 0 or (r2, c2) == self.en_passant:
                    pawn_moves.append((r2,c2))
        else:
            r2 = r1 + direction
            
            #右前
            c2 = c1 - 1
            if self.is_on_board((r2,c2)):
                if self.board[r2][c2] > 0 or (r2, c2) == self.en_passant:
                    pawn_moves.append((r2,c2))

            #左前
            c2 = c1 + 1
            if self.is_on_board((r2,c2)):
                if self.board[r2][c2] > 0 or (r2, c2) == self.en_passant:
                    pawn_moves.append((r2,c2))
        
        return(pawn_moves)
    
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
        Cas = 0
        
        #白短
        if not self.white_king_moved and not self.white_Hrook_moved: 
            Fen += 'K'
            Cas = 1
        #白長
        if not self.white_king_moved and not self.white_Arook_moved: 
            Fen += 'Q'
            Cas = 1
        #黑短
        if not self.black_king_moved and not self.black_Hrook_moved: 
            Fen += 'k'
            Cas = 1
        #黑長
        if not self.black_king_moved and not self.black_Arook_moved: 
            Fen += 'q'
            Cas = 1
  
        if Cas == 0:
            Fen += '-'

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
        self.white_king_moved = True if ('K' not in castling and 'Q' not in castling) else False
        self.white_Hrook_moved = True if 'K' not in castling else False
        self.white_Arook_moved = True if 'Q' not in castling else False
        
        self.black_king_moved = True if ('k' not in castling and 'q' not in castling) else False
        self.black_Hrook_moved = True if 'k' not in castling else False
        self.black_Arook_moved = True if 'q' not in castling else False
        
        # --- 4. 還原過路兵 ---
        if parts[3] != '-':
            files = "abcdefgh"
            ep_c = files.index(parts[3][0])
            ep_r = 8 - int(parts[3][1])
            self.en_passant = (ep_r, ep_c)
        else:
            self.en_passant = None
            
        print("GET！")
    
    book_file = r"C:\Users\micke\OneDrive\桌面\Chess\Titans.bin"

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