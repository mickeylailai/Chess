import time
import random
import numpy as np
import sys
import os
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))
import config
from core.board import Board

def get_all_valid_moves(game, color):
    
    all_moves = []
    
    for r in range(8):
        for c in range(8):
            piece = game.board[r][c]
            # 確保是目前的回合方 (正負號判斷)
            if piece != 0 and np.sign(piece) == color:
                start_pos = (r, c)
                moves = []
                
                # 判斷棋子類型並獲取走法
                abs_piece = abs(piece)
                if abs_piece == config.PAWN:
                    moves = game.get_pawn_moves(start_pos)
                elif abs_piece == config.ROOK:
                    moves = game.get_rook_moves(start_pos)
                elif abs_piece == config.KNIGHT:
                    moves = game.get_knight_moves(start_pos)
                elif abs_piece == config.BISHOP:
                    moves = game.get_bishop_moves(start_pos)
                elif abs_piece == config.QUEEN:
                    moves = game.get_queen_moves(start_pos)
                elif abs_piece == config.KING:
                    moves = game.get_king_moves(start_pos)
                
                # 將 (起點, 終點) 存入列表
                for end_pos in moves:
                    all_moves.append((start_pos, end_pos))
                    
    return all_moves

if __name__ == "__main__":
    game = Board()
    
    # 貼上你剛剛提供的經典 e4 e5 開局 FEN
    test_fen = "rnbqkbnr/pppp1ppp/8/4p3/4P3/8/PPPP1PPP/RNBQKBNR w KQkq e6 0 2"
    
    print("=== 正在透過任意門載入盤面 ===")
    game.load_fen(test_fen)
    game.display()
    
    # 看看 FEN 裡面帶的過路兵目標有沒有被正確讀取
    print(f"目前的過路兵幽靈格子 (en_passant) 座標是：{game.en_passant}")
    
    print("\n=== AI 正在查閱開局庫... ===")
    # 呼叫開局庫 (請確認你的 .bin 檔名與路徑正確)
    book_file = r"C:\Users\micke\OneDrive\桌面\Chess\Titans.bin" 
    result = game.get_book_move(book_file)
    
    if result is not None:
        begin, end, promote = result
        print(f"✅ AI 決定走出這一步: 起點 {begin} -> 終點 {end}")
        
        # 執行這步棋！
        game.move(begin, end, promote)
        
        print("\n=== AI 移動後的盤面 ===")
        game.display()
    else:
        print("🤔 查無此步，AI 不知道該怎麼辦。")