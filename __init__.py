import copy

def myai(board, stone_color):
    """
    オセロAI関数: ルールに従い、最も有利な手を選択する
    :param board: 8x8の2次元リスト (1:黒, -1:白, 0:空)
    :param stone_color: AIの石の色 (1 or -1)
    :return: (x, y) のタプル、またはパスの場合は None
    """
    
    # 1. 石を置ける場所（合法手）をリストアップ
    def get_legal_moves(curr_board, color):
        moves = []
        for y in range(8):
            for x in range(8):
                if can_put(curr_board, x, y, color):
                    moves.append((x, y))
        return moves

    # 2. その場所に置けるか、かつ挟める石があるか判定
    def can_put(curr_board, x, y, color):
        if curr_board[y][x] != 0:
            return False
        # 8方向チェック
        for dx, dy in [(-1,-1),(0,-1),(1,-1),(-1,0),(1,0),(-1,1),(0,1),(1,1)]:
            if count_flippable(curr_board, x, y, color, dx, dy) > 0:
                return True
        return False

    # 3. 指定した方向に何個ひっくり返せるか数える
    def count_flippable(curr_board, x, y, color, dx, dy):
        count = 0
        nx, ny = x + dx, y + dy
        while 0 <= nx < 8 and 0 <= ny < 8:
            if curr_board[ny][nx] == -color:
                count += 1
            elif curr_board[ny][nx] == color:
                return count
            else:
                break
            nx += dx
            ny += dy
        return 0

    # 4. 実際に石を置いて盤面を更新する（リバース処理）
    def flip_stones(curr_board, x, y, color):
        new_board = copy.deepcopy(curr_board)
        new_board[y][x] = color
        for dx, dy in [(-1,-1),(0,-1),(1,-1),(-1,0),(1,0),(-1,1),(0,1),(1,1)]:
            if count_flippable(new_board, x, y, color, dx, dy) > 0:
                nx, ny = x + dx, y + dy
                while new_board[ny][nx] == -color:
                    new_board[ny][nx] = color
                    nx += dx
                    ny += dy
        return new_board

    # 5. 盤面の評価（角を重視）
    def evaluate(curr_board, color):
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

    # --- メインロジック ---
    legal_moves = get_legal_moves(board, stone_color)
    
    if not legal_moves:
        return None  # パス

    best_move = None
    max_score = -float('inf')

    for move in legal_moves:
        # 石を置いた後の盤面をシミュレーション
        next_board = flip_stones(board, move[0], move[1], stone_color)
        # その盤面の良さを計算
        score = evaluate(next_board, stone_color)
        
        if score > max_score:
            max_score = score
            best_move = move

    return best_move
