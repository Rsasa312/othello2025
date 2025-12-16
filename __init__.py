import sys

# 再帰の深さを増加
sys.setrecursionlimit(2000)

# --- 定数定義 ---
EMPTY = 0
BLACK = 1
WHITE = 2
BASE_SEARCH_DEPTH = 3  # 基本探索深度

# 盤面評価のための重みテーブル (改善版)
WEIGHTS = [
    [100, -20,  10,   5,   5,  10, -20, 100],
    [-20, -50,  -2,  -2,  -2,  -2, -50, -20],
    [ 10,  -2,   5,   1,   1,   5,  -2,  10],
    [  5,  -2,   1,   0,   0,   1,  -2,   5],
    [  5,  -2,   1,   0,   0,   1,  -2,   5],
    [ 10,  -2,   5,   1,   1,   5,  -2,  10],
    [-20, -50,  -2,  -2,  -2,  -2, -50, -20],
    [100, -20,  10,   5,   5,  10, -20, 100]
]

# --- AIのエントリポイント ---

def myai(board, color):
    """
    オセロAIのエントリポイント。動的な深さで最善の手を返す。
    """
    opponent = 3 - color
    
    valid_moves = find_valid_moves(board, color, opponent)
    
    if not valid_moves:
        return None

    # ゲーム進行度に応じて探索深度を調整
    empty_count = board_empty_count(board)
    total_squares = len(board) * len(board)
    
    if empty_count <= 12:  # 終盤
        search_depth = 8
    elif empty_count <= 20:  # 中盤後期
        search_depth = 5
    else:  # 序盤〜中盤
        search_depth = BASE_SEARCH_DEPTH

    best_move = None
    best_eval = -float('inf')

    for r, c, flips in valid_moves:
        new_board = [row[:] for row in board]
        make_move(new_board, r, c, color, opponent)
        
        current_eval = minimax(new_board, opponent, search_depth - 1, False, color)
        
        if current_eval > best_eval:
            best_eval = current_eval
            best_move = (r, c)

    return best_move

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
            return evaluate(board, ai_color) * 1000
        
        return minimax(board, opponent_color, depth - 1, not is_maximizing_player, ai_color, alpha, beta)
            
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
    改善版評価関数
    """
    opponent = 3 - color
    size = len(board)
    score = 0
    stone_count_diff = 0

    # 1. 位置の重みの計算
    for r in range(size):
        for c in range(size):
            if board[r][c] == color:
                score += WEIGHTS[r][c]
                stone_count_diff += 1
            elif board[r][c] == opponent:
                score -= WEIGHTS[r][c]
                stone_count_diff -= 1
    
    empty_count = board_empty_count(board)
    total_stones = size * size - empty_count

    # ゲームフェーズの判定
    game_phase = total_stones / (size * size)

    # 2. 確定石の差（改善版）
    my_stable = count_stable_stones_improved(board, color)
    opponent_stable = count_stable_stones_improved(board, opponent)
    stable_diff = my_stable - opponent_stable
    score += stable_diff * 100

    # 3. 着手可能数の差（序盤・中盤で重要）
    if game_phase < 0.75:
        my_mobility = len(find_valid_moves(board, color, opponent))
        opponent_mobility = len(find_valid_moves(board, opponent, color))
        mobility_diff = my_mobility - opponent_mobility
        score += mobility_diff * 15

    # 4. フロンティアの差（改善版）
    if game_phase < 0.7:
        my_frontier = count_frontier_stones_improved(board, color)
        opponent_frontier = count_frontier_stones_improved(board, opponent)
        frontier_diff = my_frontier - opponent_frontier
        score -= frontier_diff * 8

    # 5. 石の差による補正（終盤で重要度増加）
    if game_phase >= 0.85:
        score += stone_count_diff * 50
    elif game_phase >= 0.75:
        score += stone_count_diff * 20

    # 6. ゲーム終了判定
    if empty_count == 0:
        return stone_count_diff * 10000

    return score

# --- 改善版ヒューリスティクス ---

def count_stable_stones_improved(board, color):
    """
    改善版確定石カウント
    角から完全に安定している石を正確にカウント
    """
    size = len(board)
    stable = [[False] * size for _ in range(size)]
    opponent = 3 - color
    
    # 角の確認
    corners = [(0, 0), (0, size-1), (size-1, 0), (size-1, size-1)]
    
    for corner_r, corner_c in corners:
        if board[corner_r][corner_c] == color:
            mark_stable_from_corner(board, stable, corner_r, corner_c, color, size)
    
    return sum(row.count(True) for row in stable)

def mark_stable_from_corner(board, stable, start_r, start_c, color, size):
    """
    角から確定石を再帰的にマーク
    """
    if stable[start_r][start_c] or board[start_r][start_c] != color:
        return
    
    stable[start_r][start_c] = True
    
    # 辺に沿った方向を優先的に探索
    directions = []
    
    # 角の位置に応じた探索方向を決定
    if start_r == 0 and start_c == 0:  # 左上
        directions = [(0, 1), (1, 0)]
    elif start_r == 0 and start_c == size-1:  # 右上
        directions = [(0, -1), (1, 0)]
    elif start_r == size-1 and start_c == 0:  # 左下
        directions = [(0, 1), (-1, 0)]
    else:  # 右下
        directions = [(0, -1), (-1, 0)]
    
    for dr, dc in directions:
        nr, nc = start_r + dr, start_c + dc
        if 0 <= nr < size and 0 <= nc < size:
            if board[nr][nc] == color and not stable[nr][nc]:
                # 辺にある、または既に確定石に隣接している場合のみ拡張
                if is_on_edge(nr, nc, size) or has_stable_neighbor(stable, nr, nc, size):
                    mark_stable_from_corner(board, stable, nr, nc, color, size)

def is_on_edge(r, c, size):
    """辺にあるかチェック"""
    return r == 0 or r == size-1 or c == 0 or c == size-1

def has_stable_neighbor(stable, r, c, size):
    """隣接する確定石があるかチェック"""
    directions = [(-1,0), (1,0), (0,-1), (0,1)]
    for dr, dc in directions:
        nr, nc = r + dr, c + dc
        if 0 <= nr < size and 0 <= nc < size and stable[nr][nc]:
            return True
    return False

def count_frontier_stones_improved(board, color):
    """
    改善版フロンティアカウント（重複を防ぐ）
    """
    size = len(board)
    frontier_set = set()
    
    directions = [
        (-1, -1), (-1, 0), (-1, 1),
        (0, -1),            (0, 1),
        (1, -1),  (1, 0),  (1, 1)
    ]

    for r in range(size):
        for c in range(size):
            if board[r][c] == color:
                for dr, dc in directions:
                    nr, nc = r + dr, c + dc
                    if 0 <= nr < size and 0 <= nc < size and board[nr][nc] == EMPTY:
                        frontier_set.add((r, c))
                        break
                            
    return len(frontier_set)

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
