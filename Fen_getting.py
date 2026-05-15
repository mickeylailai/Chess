import time
import pyperclip

def start_listening(previous_fen=""):
    while True:
        
        # 讀剪貼簿
        current_text = pyperclip.paste().strip()
        
        # 新 FEN 才回傳
        if current_text.count('/') == 7 and current_text != previous_fen:
            print(f"\n[獲取新 FEN]: {current_text}")
            return current_text
            
        # 降 CPU
        time.sleep(0.5)