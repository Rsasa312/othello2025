import sys

# 再帰の深さを増加
sys.setrecursionlimit(2000)

# --- 定数定義 ---
EMPTY = 0
BLACK = 1
WHITE = 2

# 盤面評価のための重みテーブル
WEIGHTS = [
    [120, -20,  20,   5,   5,  20, -20, 120],
    [-20, -40,  -5,  -5,  -5,  -5, -40, -20],
    [ 20,  -5,  15,   3,   3,  15,  -5,  20],
    [  5,  -5,   3,   3,   3,   3,  -5,   5],
    [  5,  -5,   3,   3,   3,   3,  -5,   5],
    [ 20,  -5,  15,   3,   3,  15,  -5,  20],
    [-20, -40,  -5,  -5,  -5,  -5, -40, -20],
    [120, -20,  20,   5,   5,  20, -20, 120]
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

    # 動的な探索深度
    empty_count = board_empty_count(board)
    total_squares = len(board) * len(board)
    
    if empty_count <= 10:
        search_depth = min(empty_count, 15)  # 終盤は完全読み
    elif empty_count <= 16:
        search_depth = 7
    elif empty_count <= 24:
        search_depth = 6
    else:
        search_depth = 5  # 序盤・中盤

    # 角が取れる手があれば最優先
    for r, c, flips in valid_moves:
        if is_corner(r, c, len(board)):
            return (r, c)

    best_move = None
    best_eval = -float('inf')
    alpha = -float('inf')
    beta = float('inf')

    # 手を簡易ソート（角、辺、その他）
    valid_moves.sort(key=lambda m: move_priority(m[0], m[1], m[2], len(board), empty_count), reverse=True)

    for r, c, flips in valid_moves:
        new_board = [row[:] for row in board]
        make_move(new_board, r, c, color, opponent)
        
        current_eval = minimax(new_board, opponent, search_depth - 1, False, color, alpha, beta)
        
        if current_eval > best_eval:
            best_eval = current_eval
            best_move = (r, c)
            alpha = max(alpha, current_eval)

    return best_move

def is_corner(r, c, size):
    """角かどうか"""
    return (r == 0 or r == size-1) and (c == 0 or c == size-1)

def move_priority(r, c, flips, size, empty_count):
    """手の優先度を返す（高いほど優先）"""
    priority = 0
    
    # 角は超優先
    if is_corner(r, c, size):
        priority += 10000
    
    # X位置（角の斜め隣）は避ける
    elif is_x_square(r, c, size):
        priority -= 10000
    
    # 辺は優先
    elif r == 0 or r == size-1 or c == 0 or c == size-1:
        priority += 100
    
    # 中盤以降は取れる石の数も考慮
    if empty_count < 40:
        priority += flips
    
    return priority

def is_x_square(r, c, size):
    """X位置（角の斜め隣）かどうか"""
    if size < 3:
        return False
    x_positions = [(1, 1), (1, size-2), (size-2, 1), (size-2, size-2)]
    return (r, c) in x_positions

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
            return evaluate_final(board, ai_color)
        
        # パス
        return minimax(board, opponent_color, depth - 1, not is_maximizing_player, ai_color, alpha, beta)
    
    # 簡易ソート（枝刈り効率向上）
    empty_count = board_empty_count(board)
    size = len(board)
    valid_moves.sort(key=lambda m: move_priority(m[0], m[1], m[2], size, empty_count), reverse=True)
    
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
    盤面評価関数
    """
    opponent = 3 - color
    size = len(board)
    score = 0
    
    empty_count = board_empty_count(board)
    total_squares = size * size
    game_progress = (total_squares - empty_count) / total_squares

    # 1. 位置評価（序盤・中盤で重要）
    position_weight = 1.0 if game_progress < 0.7 else 0.3
    for r in range(size):
        for c in range(size):
            if board[r][c] == color:
                score += WEIGHTS[r][c] * position_weight
            elif board[r][c] == opponent:
                score -= WEIGHTS[r][c] * position_weight
    
    # 2. モビリティ（序盤・中盤で最重要）
    if game_progress < 0.75:
        my_mobility = len(find_valid_moves(board, color, opponent))
        opp_mobility = len(find_valid_moves(board, opponent, color))
        
        if my_mobility == 0 and opp_mobility > 0:
            return -50000
        elif opp_mobility == 0 and my_mobility > 0:
            return 50000
        
        mobility_diff = my_mobility - opp_mobility
        score += mobility_diff * 50
    
    # 3. 石の数（終盤で重要）
    if game_progress >= 0.7:
        my_stones = sum(row.count(color) for row in board)
        opp_stones = sum(row.count(opponent) for row in board)
        stone_diff = my_stones - opp_stones
        
        if game_progress >= 0.85:
            score += stone_diff * 200
        else:
            score += stone_diff * 100
    
    # 4. 角の確保（超重要）
    corners = [(0, 0), (0, size-1), (size-1, 0), (size-1, size-1)]
    for r, c in corners:
        if board[r][c] == color:
            score += 800
        elif board[r][c] == opponent:
            score -= 800
    
    # 5. 辺の確保
    edge_count_mine = 0
    edge_count_opp = 0
    for r in range(size):
        if board[r][0] == color:
            edge_count_mine += 1
        elif board[r][0] == opponent:
            edge_count_opp += 1
        
        if board[r][size-1] == color:
            edge_count_mine += 1
        elif board[r][size-1] == opponent:
            edge_count_opp += 1
    
    for c in range(1, size-1):
        if board[0][c] == color:
            edge_count_mine += 1
        elif board[0][c] == opponent:
            edge_count_opp += 1
        
        if board[size-1][c] == color:
            edge_count_mine += 1
        elif board[size-1][c] == opponent:
            edge_count_opp += 1
    
    score += (edge_count_mine - edge_count_opp) * 20

    return score

def evaluate_final(board, color):
    """
    ゲーム終了時の評価
    """
    opponent = 3 - color
    my_stones = sum(row.count(color) for row in board)
    opp_stones = sum(row.count(opponent) for row in board)
    
    stone_diff = my_stones - opp_stones
    
    if stone_diff > 0:
        return 100000 + stone_diff * 100
    elif stone_diff < 0:
        return -100000 + stone_diff * 100
    else:
        return 0

# --- ルール関連のヘルパー関数 ---

def board_empty_count(board):
    """盤面上の空きマスの数"""
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
    """指定位置に置いた場合に取れる石の数"""
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
    """石を打ち、裏返す"""
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
