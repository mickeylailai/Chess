import random

# 工具函式
def get_file(sq): return sq % 8
def get_rank(sq): return sq // 8

# 評分權重
SCORE_DOUBLED = -20
SCORE_ISOLATED = -15
SCORE_CONNECTED = +10
SCORE_PASSED = +30

#通路兵獎勵(越靠近敵方底線越高)
PASSED_BONUS = [0, 0, 10, 20, 35, 55, 80, 0] 

def find_doubled(pawns):
    #疊兵要看同條file
    file_counts = {}
    for sq in pawns:
        f = get_file(sq)
        file_counts[f] = file_counts.get(f, 0) + 1
    return {sq for sq in pawns if file_counts[get_file(sq)] > 1} #掃過所有的兵，只要發現這顆兵所在的file上，總兵數超過1個，就把這顆兵的位置(sq)回傳

def find_isolated(pawns):
    my_files = {get_file(sq) for sq in pawns}
    isolated = set()
    for sq in pawns:
        f = get_file(sq)
        if (f - 1) not in my_files and (f + 1) not in my_files:
            isolated.add(sq)
    return isolated

def find_connected(pawns):
    connected = set()
    for sq in pawns:
        f, r = get_file(sq), get_rank(sq)
        neighbors = {
            (r) * 8 + (f - 1), (r) * 8 + (f + 1),         
            (r - 1) * 8 + (f - 1), (r - 1) * 8 + (f + 1), 
            (r + 1) * 8 + (f - 1), (r + 1) * 8 + (f + 1)  
        }
        if neighbors & pawns:
            connected.add(sq)
    return connected

def find_passed(my_pawns, enemy_pawns, color):
    passed = set()
    enemy_files = {}
    for sq in enemy_pawns:
        f, r = get_file(sq), get_rank(sq)
        if f not in enemy_files:
            enemy_files[f] = r
        else:
            if color == 1:
                enemy_files[f] = min(enemy_files[f], r)
            else:
                enemy_files[f] = max(enemy_files[f], r)

    for sq in my_pawns:
        f, r = get_file(sq), get_rank(sq)
        blocked = False
        
        for df in [-1, 0, 1]:
            nf = f + df
            if nf in enemy_files:
                enemy_r = enemy_files[nf]
                if color == 1 and enemy_r < r: blocked = True
                if color == -1 and enemy_r > r: blocked = True
                
        if not blocked:
            passed.add(sq)
            
    return passed


class PawnEvaluator:
    def __init__(self):
        self.zobrist = [[random.getrandbits(64) for _ in range(64)] for _ in range(2)]
        self.table = {}

    def extract_pawns(self, board_array):
        #壓成1D
        white_pawns = set()
        black_pawns = set()
        for r in range(8):
            for c in range(8):
                if board_array[r][c] == 1:   #白兵
                    white_pawns.add(r * 8 + c)
                elif board_array[r][c] == -1: #黑兵
                    black_pawns.add(r * 8 + c)
        return white_pawns, black_pawns

    def compute_hash(self, white_pawns, black_pawns):
        h = 0
        for sq in white_pawns: h ^= self.zobrist[0][sq]
        for sq in black_pawns: h ^= self.zobrist[1][sq]
        return h

    def evaluate_structure(self, white_pawns, black_pawns):
        score = 0
        
        w_d = find_doubled(white_pawns)
        w_i = find_isolated(white_pawns)
        w_c = find_connected(white_pawns)
        w_p = find_passed(white_pawns, black_pawns, color=1)

        score += len(w_d) * SCORE_DOUBLED
        score += len(w_i) * SCORE_ISOLATED
        score += len(w_c) * SCORE_CONNECTED
        for sq in w_p:
            score += SCORE_PASSED + PASSED_BONUS[get_rank(sq)]

        b_d = find_doubled(black_pawns)
        b_i = find_isolated(black_pawns)
        b_c = find_connected(black_pawns)
        b_p = find_passed(black_pawns, white_pawns, color=-1)

        score -= len(b_d) * SCORE_DOUBLED
        score -= len(b_i) * SCORE_ISOLATED
        score -= len(b_c) * SCORE_CONNECTED
        for sq in b_p:
            score -= SCORE_PASSED + PASSED_BONUS[7 - get_rank(sq)]

        return score

    def probe(self, board_array):
        w_pawns, b_pawns = self.extract_pawns(board_array)
        key = self.compute_hash(w_pawns, b_pawns)

        if key in self.table:
            return self.table[key]

        score = self.evaluate_structure(w_pawns, b_pawns)
        self.table[key] = score
        return score
    
