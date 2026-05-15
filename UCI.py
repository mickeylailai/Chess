import sys
import config
import search
from core.board import Board

def move_to_uci(board, move):
    begin, end = move
    res = board.to_algebraic(begin) + board.to_algebraic(end)
    
    # 兵升變補 q
    piece = board.board[begin[0]][begin[1]]
    if abs(piece) == config.PAWN and (end[0] == 0 or end[0] == 7):
        res += 'q'
        
    return res

def uci_loop():
    game = Board()
    
    # 持續收 GUI 指令
    while True:
        try:
            line = input().strip()
        except EOFError:
            break
            
        if not line:
            continue
            
        tokens = line.split()
        command = tokens[0]
        
        if command == "uci":
            # 回報引擎資訊
            print("id name MickeyChess")
            print("id author Mickey")
            print("uciok")
            sys.stdout.flush() # 立刻輸出
            
        elif command == "isready":
            # 回應已準備好
            print("readyok")
            sys.stdout.flush()
            
        elif command == "ucinewgame":
            # 新局重置
            game = Board()
            search.tt.table.clear() # 清 TT
            
        elif command == "position":
            # 設定盤面
            moves_idx = -1
            if "moves" in tokens:
                moves_idx = tokens.index("moves")
                
            if len(tokens) > 1 and tokens[1] == "startpos":
                game = Board() # 初始盤面
            elif len(tokens) > 1 and tokens[1] == "fen":
                # 載入 FEN
                fen_end = moves_idx if moves_idx != -1 else len(tokens)
                fen_str = " ".join(tokens[2:fen_end])
                game.load_fen(fen_str)
                
            # 套用後續走法
            if moves_idx != -1:
                for move_str in tokens[moves_idx + 1:]:
                    begin, end, promote = game.from_algebraic(move_str)
                    game.make_move(begin, end, promote)
                    
        elif command == "go":
            depth = 5 # 預設深度
            if "depth" in tokens:
                idx = tokens.index("depth")
                depth = int(tokens[idx + 1])
            
            best_move = search.get_best_move(game, depth=depth)
            
            # 回報最佳步
            if best_move:
                print(f"bestmove {move_to_uci(game, best_move)}")
            else:
                print("bestmove 0000") # 無合法步
            sys.stdout.flush()
            
        elif command == "quit":
            # 結束
            break

if __name__ == "__main__":
    # 啟動 UCI
    uci_loop()