import sys
import config
import search
from core.board import Board

def move_to_uci(board, move):
    begin, end = move
    res = board.to_algebraic(begin) + board.to_algebraic(end)
    
    # 檢查是否為兵的升變 (走到第 0 或 第 7 列)
    piece = board.board[begin[0]][begin[1]]
    if abs(piece) == config.PAWN and (end[0] == 0 or end[0] == 7):
        res += 'q'
        
    return res

def uci_loop():
    game = Board()
    
    # 無窮迴圈，持續監聽 GUI 傳來的指令
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
            # 宣告身分
            print("id name MickeyChess")
            print("id author Mickey")
            print("uciok")
            sys.stdout.flush() #確保訊息即時傳給 GUI
            
        elif command == "isready":
            # GUI 檢查引擎是否準備好
            print("readyok")
            sys.stdout.flush()
            
        elif command == "ucinewgame":
            # 開始新的一局
            game = Board()
            search.tt.table.clear() # 清空置換表，避免上一局的記憶干擾
            
        elif command == "position":
            # GUI 告訴引擎現在的盤面長怎樣
            # 格式 1: position startpos moves e2e4 e7e5
            # 格式 2: position fen <fen_string> moves e2e4
            moves_idx = -1
            if "moves" in tokens:
                moves_idx = tokens.index("moves")
                
            if len(tokens) > 1 and tokens[1] == "startpos":
                game = Board() # 回到初始盤面
            elif len(tokens) > 1 and tokens[1] == "fen":
                # 組裝 FEN 字串並讀取
                fen_end = moves_idx if moves_idx != -1 else len(tokens)
                fen_str = " ".join(tokens[2:fen_end])
                game.load_fen(fen_str)
                
            #將歷史走法全部走一遍
            if moves_idx != -1:
                for move_str in tokens[moves_idx + 1:]:
                    begin, end, promote = game.from_algebraic(move_str)
                    game.make_move(begin, end, promote)
                    
        elif command == "go":
            depth = 5 #預設深度
            if "depth" in tokens:
                idx = tokens.index("depth")
                depth = int(tokens[idx + 1])
            
            best_move = search.get_best_move(game, depth=depth)
            
            #回報最佳走法
            if best_move:
                print(f"bestmove {move_to_uci(game, best_move)}")
            else:
                print("bestmove 0000") #沒步可走 (被將死或逼和)
            sys.stdout.flush()
            
        elif command == "quit":
            #關閉引擎
            break

if __name__ == "__main__":
    #啟動 UCI 監聽
    uci_loop()