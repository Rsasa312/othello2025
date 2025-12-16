import sys

# 再帰の深さを増加
sys.setrecursionlimit(2000)

# --- 定数定義 ---
EMPTY = 0
BLACK = 1
WHITE = 2
BASE_SEARCH_DEPTH = 4  # 基本探索深度を4に増加

# 盤面評価のための重みテーブル（序盤・中盤用）
WEIGHTS_EARLY = [
    [120, -20,  20,   5,   5,  20, -20, 120],
    [-20, -40,  -5,  -5,  -5,  -5, -40, -20],
    [ 20,  -5,  15,   3,   3,  15,  -5,  20],
    [  5,  -5,   3,   3,   3,   3,  -5,   5],
    [  5,  -5,   3,   3,   3,   3,  -5,   5],
    [ 20,  -5,  15,   3,   3,  15,  -5,  20],
    [-20, -40,  -5,  -5,  -5,  -5, -40, -20],
    [120, -20,  20,   5,   5,  20, -20, 120]
]

# 終盤用の重みテーブル（石の数が重要）
WEIGHTS_LATE = [
    [100,  10,  10,  10,  10,  10,  10, 100],
    [ 10,  10,  10,  10,  10,  10,  10,  10],
    [ 10,  10,  10,  10,  10,  10,  10,  10],
    [ 10,  10,  10,  10,  10,  10,  10,  10],
    [ 10,  10,  10,  10,  10,  10,  10,  10],
    [ 10,  10,  10,  10,  10,  10,  10,  10],
    [ 10,  10,  10,  10,  10,  10,  10,  10],
    [100,  10,  10,  10,  10,  10,  10, 100]
]

# --- AIのエントリポイント ---

def myai(board, color):
    """
    オセロAIのエントリポイント
    """
    opponent = 3 - color
    
    valid_moves = find_valid_moves(board, color, opponent)
    
    if not valid_moves:
        return None

    empty_count = board_empty_count(board)
    
    # 動的な探索深度
    if empty_count <= 10:
        search_depth = min(empty_count, 10)  # 完全読み切り
    elif empty_count <= 16:
        search_depth = 6
    elif empty_count <= 25:
        search_depth = 5
    else:
        search_depth = BASE_SEARCH_DEPTH

    # 手を評価値でソート（良さそうな手を先に探索）
    valid_moves = sort_moves(board, valid_moves, color, opponent, empty_count)

    best_move = None
    best_eval = -float('inf')
    alpha = -float('inf')
    beta = float('inf')

    for r, c, flips in valid_moves:
        new_board = [row[:] for row in board]
        make_move(new_board, r, c, color, opponent)
        
        current_eval = minimax(new_board, opponent, search_depth - 1, False, color, alpha, beta)
        
        if current_eval > best_eval:
            best_eval = current_eval
            best_move = (r, c)
            alpha = max(alpha, current_eval)

    return best_move

def sort_moves(board, moves, color, opponent, empty_count):
    """
    手を優先順位でソート（良い手を先に探索してα-β枝刈りの効率を上げる）
    """
    def move_priority(move):
        r, c, flips = move
        priority = 0
        
        # 角は最優先
        if (r == 0 or r == 7) and (c == 0 or c == 7):
            priority += 10000
        
        # 辺は優先（ただし角の隣のX位置を除く）
        elif (r == 0 or r == 7 or c == 0 or c == 7):
            # X位置（角の斜め隣）は避ける
            if not is_x_square(r, c):
                priority += 1000
            else:
                priority -= 5000  # X位置は避ける
        
        # X位置は避ける
        elif is_x_square(r, c):
            priority -= 5000
        
        # 取れる石が多い手を優先（中盤以降）
        if empty_count < 40:
            priority += flips * 10
        
        return priority
    
    return sorted(moves, key=move_priority, reverse=True)

def is_x_square(r, c):
    """X位置（角の斜め隣）かどうかをチェック"""
    x_squares = [(1, 1), (1, 6), (6, 1), (6, 6)]
    return (r, c) in x_squares

# --- ミニマックス探索 ---

def minimax(board, current_player_color, depth, is_maximizing_player, ai_color, alpha=-float('inf'), beta=float('inf')):
    """
    ミニマックス探索（アルファベータ枝刈り付き）
    """
    opponent_color = 3 - current_player_color

    if depth == 0:
        return evaluate(board, ai_color)
    
    valid_moves = find_valid_moves(board, current_player_color, opponent_color)

    if not valid_moves:
        opponent_moves = find_valid_moves(board, opponent_color, current_player_color)
        
        if not opponent_moves:
            # ゲーム終了
            my_count = count_stones(board, ai_color)
            opp_count = count_stones(board, 3 - ai_color)
            if my_count > opp_count:
                return 100000
            elif my_count < opp_count:
                return -100000
            else:
                return 0
        
        # パス
        return minimax(board, opponent_color, depth - 1, not is_maximizing_player, ai_color, alpha, beta)
    
    # 手をソート（効率的な枝刈りのため）
    empty_count = board_empty_count(board)
    valid_moves = sort_moves(board, valid_moves, current_player_color, opponent_color, empty_count)
    
    if is_maximizing_player:
        max_eval = -float('inf')
        for r, c, flips in valid_moves:
            new_board = [row[:] for row in board]
            make_move(new_board, r, c, current_player_color, opponent_color)
            
            eval = minimax(new_board, opponent_color, depth - 1, False, ai_color, alpha, beta)
            max_eval = max(max_eval, eval)
            alpha = max(alpha, eval)
            if beta <= alpha:
                break
        return max_eval
    else:
        min_eval = float('inf')
        for r, c, flips in valid_moves:
            new_board = [row[:] for row in board]
            make_move(new_board, r, c, current_player_color, opponent_color)
            
            eval = minimax(new_board, opponent_color, depth - 1, True, ai_color, alpha, beta)
            min_eval = min(min_eval, eval)
            beta = min(beta, eval)
            if beta <= alpha:
                break
        return min_eval

# --- 評価関数 ---

def evaluate(board, color):
    """
    シンプルだが効果的な評価関数
    """
    opponent = 3 - color
    size = len(board)
    score = 0
    
    empty_count = board_empty_count(board)
    total_stones = size * size - empty_count
    game_phase = total_stones / (size * size)
    
    # 使用する重みテーブルを選択
    if game_phase < 0.75:
        weights = WEIGHTS_EARLY
    else:
        weights = WEIGHTS_LATE
    
    # 1. 位置評価
    position_score = 0
    my_stones = 0
    opp_stones = 0
    
    for r in range(size):
        for c in range(size):
            if board[r][c] == color:
                position_score += weights[r][c]
                my_stones += 1
            elif board[r][c] == opponent:
                position_score -= weights[r][c]
                opp_stones += 1
    
    score += position_score
    
    # 2. モビリティ（序盤・中盤で重要）
    if game_phase < 0.8:
        my_mobility = len(find_valid_moves(board, color, opponent))
        opp_mobility = len(find_valid_moves(board, opponent, color))
        
        # モビリティが0の場合は大きなペナルティ
        if my_mobility == 0 and opp_mobility > 0:
            score -= 5000
        elif opp_mobility == 0 and my_mobility > 0:
            score += 5000
        else:
            mobility_diff = my_mobility - opp_mobility
            score += mobility_diff * 30
    
    # 3. 石の差（終盤で重要）
    if game_phase >= 0.75:
        stone_diff = my_stones - opp_stones
        score += stone_diff * 100
    
    # 4. 角の確保ボーナス
    corners = [(0, 0), (0, 7), (7, 0), (7, 7)]
    for r, c in corners:
        if board[r][c] == color:
            score += 500
        elif board[r][c] == opponent:
            score -= 500
    
    # 5. 確定石（角から連結している辺の石）
    stable_diff = count_edge_stable_stones(board, color) - count_edge_stable_stones(board, opponent)
    score += stable_diff * 80
    
    return score

def count_edge_stable_stones(board, color):
    """
    角から辺に沿って安定している石をカウント
    """
    size = len(board)
    count = 0
    
    # 上辺
    if board[0][0] == color:
        for c in range(1, size):
            if board[0][c] == color:
                count += 1
            else:
                break
    
    if board[0][size-1] == color:
        for c in range(size-2, -1, -1):
            if board[0][c] == color:
                count += 1
            else:
                break
    
    # 下辺
    if board[size-1][0] == color:
        for c in range(1, size):
            if board[size-1][c] == color:
                count += 1
            else:
                break
    
    if board[size-1][size-1] == color:
        for c in range(size-2, -1, -1):
            if board[size-1][c] == color:
                count += 1
            else:
                break
    
    # 左辺
    if board[0][0] == color:
        for r in range(1, size):
            if board[r][0] == color:
                count += 1
            else:
                break
    
    if board[size-1][0] == color:
        for r in range(size-2, -1, -1):
            if board[r][0] == color:
                count += 1
            else:
                break
    
    # 右辺
    if board[0][size-1] == color:
        for r in range(1, size):
            if board[r][size-1] == color:
                count += 1
            else:
                break
    
    if board[size-1][size-1] == color:
        for r in range(size-2, -1, -1):
            if board[r][size-1] == color:
                count += 1
            else:
                break
    
    return count

def count_stones(board, color):
    """指定色の石の数を数える"""
    return sum(row.count(color) for row in board)

# --- ルール関連のヘルパー関数 ---

def board_empty_count(board):
    """盤面上の空きマスの数を数える"""
    return sum(row.count(EMPTY) for row in board)

def find_valid_moves(board, color, opponent):
    """有効な手を全てリストアップ"""
    size = len(board)
    valid_moves = []
    for row in range(size):
        for col in range(size):
            if board[row][col] == EMPTY:
                flips = count_flips(board, row, col, color, opponent)
                if flips > 0:
                    valid_moves.append((row, col, flips))
    return valid_moves

def count_flips(board, row, col, color, opponent):
    """指定位置に置いた場合に取れる石の数を数える"""
    size = len(board)
    flips = 0

    directions = [
        (-1, -1), (-1, 0), (-1, 1),
        (0, -1),            (0, 1),
        (1, -1),  (1, 0),  (1, 1)
    ]

    for dr, dc in directions:
        temp_flips = 0
        r, c = row + dr, col + dc

        while 0 <= r < size and 0 <= c < size:
            if board[r][c] == EMPTY:
                break
            elif board[r][c] == opponent:
                temp_flips += 1
            else:
                flips += temp_flips
                break
            r += dr
            c += dc

    return flips

def make_move(board, row, col, color, opponent):
    """石を打ち、裏返す操作を行う"""
    size = len(board)
    board[row][col] = color
    
    directions = [
        (-1, -1), (-1, 0), (-1, 1),
        (0, -1),            (0, 1),
        (1, -1),  (1, 0),  (1, 1)
    ]

    for dr, dc in directions:
        temp_flips_coords = []
        r, c = row + dr, col + dc

        while 0 <= r < size and 0 <= c < size:
            if board[r][c] == EMPTY:
                break
            elif board[r][c] == opponent:
                temp_flips_coords.append((r, c))
            else:
                for fr, fc in temp_flips_coords:
                    board[fr][fc] = color
                break
            r += dr
            c += dc
