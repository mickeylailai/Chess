from core.board import Board
import config
import PST

def evaluate(game):

    mg_score = 0
    eg_score = 0
    phase = 0

    phase_weight = {config.PAWN: 0,
                    config.KNIGHT: 1,
                    config.BISHOP: 1,
                    config.ROOK: 2,
                    config.QUEEN: 4,
                    config.KING: 0
                    }
    
    mg_pst_map = {
        config.PAWN: PST.P_PST,
        config.KNIGHT: PST.N_PST,
        config.BISHOP: PST.B_PST,
        config.ROOK: PST.R_PST,
        config.QUEEN: PST.Q_PST,
        config.KING: PST.K_MGPST
    }

    eg_pst_map = {
        config.PAWN: PST.P_PST,
        config.KNIGHT: PST.N_PST,
        config.BISHOP: PST.B_PST,
        config.ROOK: PST.R_PST,
        config.QUEEN: PST.Q_PST,
        config.KING: PST.K_EGPST
    }

    #計算子力(PST + Material)
    for r in range(8):
        for c in range(8):
            piece = game.board[r][c]
            
            if piece == 0: 
                continue 
            
            color = 1 if piece > 0 else -1
            
            #Phase值
            phase += phase_weight[abs(piece)]

            #因為pst沒分黑白寫所以要換行
            pst_r = r if color == 1 else 7 - r

            mg_mat = config.MG_value.get(abs(piece), 0) #基本分
            eg_mat = config.EG_value.get(abs(piece), 0)

            mg_pst_val = mg_pst_map[abs(piece)][pst_r][c]#PST分
            eg_pst_val = eg_pst_map[abs(piece)][pst_r][c]

            mg_score += (mg_mat + mg_pst_val) * color
            eg_score += (eg_mat + eg_pst_val) * color

    phase = min(phase, 24) # 確保 phase 絕對不會超過 24 (by gemini)
    score = (mg_score * phase + eg_score * (24 - phase)) // 24 #公式

    return score * game.turn


            
        
    

