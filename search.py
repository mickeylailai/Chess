import math
import config  
from evaluator import evaluate
from core.board import Board
from tt import SimpleTT 
from core.board import zobrist

tt = SimpleTT()

EXACT = 0 #沒有剪枝
LOWERBOUND = 1 #發生beta剪枝 score可能更高
UPPERBOUND = 2 #走法都>alpha score可能更低

def quiescence_search(game, alpha, beta): #避免深度到0的時候接續被吃子等等

    stand_pat = evaluate(game)
    
    if stand_pat >= beta:
        return beta
    if alpha < stand_pat:
        alpha = stand_pat
        
    capture_moves = game.get_capture_moves(game.turn)
    
    for move in capture_moves:
        begin, end = move
        game.make_move(begin, end)
        score = -quiescence_search(game, -beta, -alpha)
        game.undo_move()
        
        if score >= beta:
            return beta
        if score > alpha:
            alpha = score
            
    return alpha

def negamax(game, depth, alpha, beta):

    old_alpha = alpha
    move_tt = None

    #先看有沒有查過了
    entry = tt.lookup(game.zobrist_key)

    #如果有而且深度更深那就取代
    if entry:
        depth_tt, score_tt, flag_tt, move_tt = entry
        if depth_tt >= depth:
            #去判斷flag, 如果EXACT直接回傳score, 不然就更新beta, alpha
            if flag_tt == EXACT:
                return(score_tt)
            elif flag_tt == LOWERBOUND:
                alpha = max(alpha, score_tt)
            elif flag_tt == UPPERBOUND:
                beta = min(beta, score_tt)
            
            if alpha >= beta: return(score_tt)

    #遞迴終止 
    #到指定深度
    if depth == 0:
        return quiescence_search(game, alpha, beta)
    
    #檢查合法步數
    legal_moves = game.get_all_legal_moves(game.turn)

    #Checkmate or Stalemate
    if not legal_moves:
        if game.is_checkmate(game.turn):
            return -99999 - depth 
        else:
            return 0 
    
    def get_move_score(move):
        if move == move_tt:
            return 9999999  
            
        begin, end = move
        target_piece = game.board[end[0]][end[1]]

        if target_piece != 0:
            attacker_piece = game.board[begin[0]][begin[1]]
            v_val = config.MG_value.get(abs(target_piece), 0)
            a_val = config.MG_value.get(abs(attacker_piece), 0)
            return (v_val * 10) - a_val + 1000000 
            
        return 0 


    legal_moves.sort(key=get_move_score, reverse=True)

    
    best_score = -math.inf
    best_move = None

    #遍歷走法
    for move in legal_moves:
        begin, end = move 

        game.make_move(begin, end)
        score = -negamax(game, depth - 1, -beta, -alpha)
        game.undo_move() #復原

        #Alpha-Beta剪枝
        if score > best_score:
            best_score = score
            best_move = move
        if score > alpha:
            alpha = score
        if alpha >= beta:
            break 
    
    if best_score <= old_alpha:
        flag = UPPERBOUND
    elif best_score >= beta:
        flag = LOWERBOUND
    else:
        flag = EXACT
        
    tt.store(game.zobrist_key, depth, best_score, flag, best_move)
    return best_score

def get_best_move(game, depth):
    legal_moves = game.get_all_legal_moves(game.turn)

    if not legal_moves:
        return None

    def get_root_move_score(move):
        begin, end = move
        target_piece = game.board[end[0]][end[1]]
        if target_piece != 0:
            return config.MG_value.get(abs(target_piece), 0) + 100000
        return 0
        
    legal_moves.sort(key=get_root_move_score, reverse=True)

    best_score = -math.inf
    best_move = None  
    alpha = -math.inf
    beta = math.inf

    for move in legal_moves:
        begin, end = move
        
        game.make_move(begin, end)
        score = -negamax(game, depth - 1, -beta, -alpha) 
        game.undo_move()

        if score > best_score:
            best_score = score
            best_move = move  
        if score > alpha:
            alpha = score

    return best_move