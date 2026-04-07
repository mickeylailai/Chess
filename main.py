import time
import random
import numpy as np
import sys
import os

sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))
import config
from evaluator import evaluate
from core.board import Board
from Fen_getting import start_listening
import search

if __name__ == "__main__":
    print("程式已啟動，持續監聽剪貼簿中的 FEN 碼... (按 Ctrl+C 關閉)")
    

    current_fen = ""
    
    try:
        while True:

            current_fen = start_listening(current_fen)
            
            game = Board()
            game.load_fen(current_fen)
            game.display()

            score_adv = evaluate(game)
            print(f"評估分數: {score_adv}\n")

            # 開局庫
            result = game.get_book_move(r"C:\Users\micke\OneDrive\桌面\Chess\Titans.bin")

            if result:
                begin, end, promote = result
                str_begin = game.to_algebraic(begin)
                str_end = game.to_algebraic(end)
                print(f"{str_begin} -> {str_end}")

            else:
                print("can not find")
                print("Start to search")

                start_time = time.time()

                best_move = search.get_best_move(game, depth=5)
                end_time = time.time()

                if best_move:
                    begin, end = best_move
                    str_begin = game.to_algebraic(begin)
                    str_end = game.to_algebraic(end)
                    print(f"The best move by searching is : {str_begin} -> {str_end}") 
                    print(f"using: {end_time - start_time:.2f} seconds")

                else:
                    print("No Solution")
            
            print("-" * 50) # 印出分隔線，準備迎接下一步
            
    except KeyboardInterrupt:
        print("\n程式已手動關閉。")