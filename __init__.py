import copy

def myai(board, color):
    # 設定：何手先まで読むか（3〜5程度が速度と強さのバランスが良い）
    DEPTH = 4

    # 1. 盤面の重み付け（静的評価マップ）
    # 隅は高く、隅の隣(X打ち)は低く設定
    EVAL_MAP = [
        [100, -20, 10,  5,  5, 10, -20, 100],
        [-20, -50, -2, -2, -2, -2, -50, -20],
        [ 10,  -2,  1,  1,  1,  1,  -2,  10],
        [  5,  -2,  1,  0,  0,  1,  -2,   5],
        [  5,  -2,  1,  0,  0,  1,  -2,   5],
        [ 10,  -2,  1,  1,  1,  1,  -2,  10],
        [-20, -50, -2, -2, -2, -2, -50, -20],
        [100, -20, 10,  5,  5, 10, -20, 100],
    ]

    def get_valid_moves(temp_board, temp_color):
        moves = []
        directions = [(-1, -1), (-1, 0), (-1, 1), (0, -1), (0, 1), (1, -1), (1, 0), (1, 1)]
        opponent = 3 - temp_color
        for r in range(8):
            for c in range(8):
                if temp_board[r][c] != 0: continue
                for dr, dc in directions:
                    nr, nc = r + dr, c + dc
                    if 0 <= nr < 8 and 0 <= nc < 8 and temp_board[nr][nc] == opponent:
                        while 0 <= nr < 8 and 0 <= nc < 8:
                            if temp_board[nr][nc] == 0: break
                            if temp_board[nr][nc] == temp_color:
                                moves.append((r, c))
                                break
                            nr += dr
                            nc += dc
                        else: continue
                        break
        return list(set(moves))

    def flip_stones(temp_board, move, temp_color):
        new_board = copy.deepcopy(temp_board)
        r, c = move
        new_board[r][c] = temp_color
        opponent = 3 - temp_color
        directions = [(-1, -1), (-1, 0), (-1, 1), (0, -1), (0, 1), (1, -1), (1, 0), (1, 1)]
        for dr, dc in directions:
            path = []
            nr, nc = r + dr, c + dc
            while 0 <= nr < 8 and 0 <= nc < 8 and new_board[nr][nc] == opponent:
                path.append((nr, nc))
                nr += dr
                nc += dc
            if 0 <= nr < 8 and 0 <= nc < 8 and new_board[nr][nc] == temp_color:
                for pr, pc in path:
                    new_board[pr][pc] = temp_color
        return new_board

    def evaluate(temp_board, temp_color):
        # 盤面の評価値を計算
        score = 0
        opponent = 3 - temp_color
        for r in range(8):
            for c in range(8):
                if temp_board[r][c] == temp_color:
                    score += EVAL_MAP[r][c]
                elif temp_board[r][c] == opponent:
                    score -= EVAL_MAP[r][c]
        return score

    def minimax(temp_board, depth, alpha, beta, is_maximizing, ai_color):
        valid_moves = get_valid_moves(temp_board, ai_color if is_maximizing else 3 - ai_color)
        
        if depth == 0 or not valid_moves:
            return evaluate(temp_board, ai_color)

        if is_maximizing:
            max_eval = float('-inf')
            for move in valid_moves:
                new_board = flip_stones(temp_board, move, ai_color)
                eval_val = minimax(new_board, depth - 1, alpha, beta, False, ai_color)
                max_eval = max(max_eval, eval_val)
                alpha = max(alpha, eval_val)
                if beta <= alpha: break
            return max_eval
        else:
            min_eval = float('inf')
            for move in valid_moves:
                new_board = flip_stones(temp_board, move, 3 - ai_color)
                eval_val = minimax(new_board, depth - 1, alpha, beta, True, ai_color)
                min_eval = min(min_eval, eval_val)
                beta = min(beta, eval_val)
                if beta <= alpha: break
            return min_eval

    # メインロジック
    valid_moves = get_valid_moves(board, color)
    if not valid_moves: return None

    best_move = None
    best_value = float('-inf')

    for move in valid_moves:
        new_board = flip_stones(board, move, color)
        # 相手の手番としてMinimax開始
        board_value = minimax(new_board, DEPTH - 1, float('-inf'), float('inf'), False, color)
        if board_value > best_value:
            best_value = board_value
            best_move = move

    return best_move
