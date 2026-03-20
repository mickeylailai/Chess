import time
import pyperclip
from board import Board

def start_listening():
    last_fen = "" 
    while True:
        # 讀取剪貼簿中的文字
        current_text = pyperclip.paste().strip()
        
        #如果是Fen才接受
        if current_text != last_fen and current_text.count('/') == 7:
            last_fen = current_text
            print(f"\n📥 接收到新盤面: {last_fen}")
            
            #棋盤載入
            game = Board()
            game.load_fen(last_fen)
            game.display()
            
            #開局庫
            result = game.get_book_move(r"C:\Users\micke\OneDrive\桌面\Chess\Titans.bin")
            
            if result:
                begin, end, promote = result
                print(f"{begin} -> {end}")
            else:
                print("查無資料")
                
        time.sleep(0.5)

if __name__ == "__main__":
    start_listening()