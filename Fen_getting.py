import time
import pyperclip

def start_listening(previous_fen=""):
    while True:
        
        # 讀取剪貼簿中的文字
        current_text = pyperclip.paste().strip()
        
        # 如果格式符合 Fen (有7個 '/') 且不是上一次的 Fen
        if current_text.count('/') == 7 and current_text != previous_fen:
            print(f"\n[獲取新 FEN]: {current_text}")
            return current_text
            
        # 暫停 0.5 秒，避免 CPU 佔用率過高
        time.sleep(0.5)