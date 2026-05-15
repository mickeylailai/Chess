class SimpleTT:
    def __init__(self):
        self.table = {}  #用字典存：{(depth, score, flag, best_move)}

    def store(self, key, depth, score, flag, move):
        #去看深度如果比較深就換掉
        if key in self.table:
            if depth >= self.table[key][0]:
                self.table[key] = (depth, score, flag, move)
        else:
            self.table[key] = (depth, score, flag, move)

    def lookup(self, key):
        return self.table.get(key)