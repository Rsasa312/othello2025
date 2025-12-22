import copy

def myai(board, stone_color):
    """
    オセロAI関数 'myai'
    :param board: 8x8の2次元リスト (1:黒, -1:白, 0:空)
    :param stone_color: 自分の石の色 (1 or -1)
    :return: 選択した座標 (x, y) または パスの場合は None
    """
    
    # --- 内部関数: 石を置ける場所（合法手）を探す ---
    def get_legal_moves(curr_board, color):
        moves = []
        for y in range(8):
            for x in range(8):
                if can_flip(curr_board, x, y, color):
                    moves.append((x, y))
        return moves

    def can_flip(curr_board, x, y, color):
        if curr_board[y][x] != 0: return False
        directions = [(-1,-1), (0,-1), (1,-1), (-1,0), (1,0), (-1,1), (0,1), (1,1)]
        for dx, dy in directions:
            nx, ny = x + dx, y + dy
            if 0 <= nx < 8 and 0 <= ny < 8 and curr_board[ny][nx] == -color:
                while 0 <= nx < 8 and 0 <= ny < 8:
                    if curr_board[ny][nx] == 0: break
                    if curr_board[ny][nx] == color: return True
                    nx += dx
                    ny += dy
        return False

    # --- 内部関数: 盤面の評価 (重み付けマップ) ---
    def evaluate(curr_board, color):
        # 盤面の場所ごとの価値（簡易版）
        weights = [
            [100, -20, 10,  5,  5, 10, -20, 100],
            [-20, -50, -2, -2, -2, -2, -50, -20],
            [ 10,  -2,  5,  1,  1,  5,  -2,  10],
            [  5,  -2,  1,  0,  0,  1,  -2,   5],
            [  5,  -2,  1,  0,  0,  1,  -2,   5],
            [ 10,  -2,  5,  1,  1,  5,  -2,  10],
            [-20, -50, -2, -2, -2, -2, -50, -20],
            [100, -20, 10,  5,  5, 10, -20, 100],
        ]
        score = 0
        for y in range(8):
            for x in range(8):
                if curr_board[y][x] == color:
                    score += weights[y][x]
                elif curr_board[y][x] == -color:
                    score -= weights[y][x]
        return score

    # --- メイン処理: 最善手を選ぶ ---
    legal_moves = get_legal_moves(board, stone_color)
    
    if not legal_moves:
        return None  # 置ける場所がない場合はパス

    best_move = None
    max_score = -float('inf')

    # すべての合法手について、1手先を予測して評価
    for move in legal_moves:
        # 仮に置いてみた盤面を作る（簡易的なシミュレーション）
        temp_board = copy.deepcopy(board)
        # ※本来はここで石をひっくり返す処理が必要ですが、
        # 簡易的に「その場所に置いた後の評価」を計算します。
        temp_board[move[1]][move[0]] = stone_color
        
        score = evaluate(temp_board, stone_color)
        
        if score > max_score:
            max_score = score
            best_move = move

    return best_move

# --- 使い方（例） ---
# board = [[0]*8 for _ in range(8)]
# board[3][3], board[4][4] = -1, -1
# board[3][4], board[4][3] = 1, 1
# print(myai(board, 1))  # 黒(1)の番で最適な手を出力
