import sys

# 再帰の深さを増加
sys.setrecursionlimit(2000)

# --- 定数定義 ---
EMPTY = 0
BLACK = 1
WHITE = 2
SEARCH_DEPTH = 4  # 3から4に増やす

# 盤面評価のための重みテーブル (Positional Weights)
WEIGHTS = [
    [100, -20,  10,   5,   5,  10, -20, 100],
    [-20, -40,  -5,  -5,  -5,  -5, -40, -20],
    [ 10,  -5,   5,   3,   3,   5,  -5,  10],
    [  5,  -5,   3,   1,   1,   3,  -5,   5],
    [  5,  -5,   3,   1,   1,   3,  -5,   5],
    [ 10,  -5,   5,   3,   3,   5,  -5,  10],
    [-20, -40,  -5,  -5,  -5,  -5, -40, -20],
    [100, -20,  10,   5,   5,  10, -20, 100]
]

# --- AIのエントリポイント ---

def myai(board, color):
    """
    オセロAIのエントリポイント。
    """
    opponent = 3 - color
    
    valid_moves = find_valid_moves(board, color, opponent)
    
    if not valid_moves:
        return None

    # 終盤は探索を深くする
    empty_count = board_empty_count(board)
    if empty_count <= 12:
        search_depth = min(empty_count, 12)
    else:
        search_depth = SEARCH_DEPTH

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
            # ゲーム終了
            return evaluate_final(board, ai_color)
        
        # パス
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
    現在の盤面を評価し、colorにとっての点数を返す。
    """
    opponent = 3 - color
    size = len(board)
    score = 0

    # 1. 位置の重み
    for r in range(size):
        for c in range(size):
            if board[r][c] == color:
                score += WEIGHTS[r][c]
            elif board[r][c] == opponent:
                score -= WEIGHTS[r][c]
    
    # 2. モビリティ（着手可能数）
    my_mobility = len(find_valid_moves(board, color, opponent))
    opponent_mobility = len(find_valid_moves(board, opponent, color))
    
    # モビリティが0は致命的
    if my_mobility == 0 and opponent_mobility > 0:
        score -= 10000
    elif opponent_mobility == 0 and my_mobility > 0:
        score += 10000
    else:
        mobility_diff = my_mobility - opponent_mobility
        score += mobility_diff * 20

    # 3. 終盤では石の数も考慮
    empty_count = board_empty_count(board)
    if empty_count <= 15:
        my_stones = sum(row.count(color) for row in board)
        opp_stones = sum(row.count(opponent) for row in board)
        score += (my_stones - opp_stones) * 50

    return score

def evaluate_final(board, color):
    """
    ゲーム終了時の評価（石の差のみ）
    """
    opponent = 3 - color
    my_stones = sum(row.count(color) for row in board)
    opp_stones = sum(row.count(opponent) for row in board)
    
    stone_diff = my_stones - opp_stones
    
    if stone_diff > 0:
        return 100000 + stone_diff
    elif stone_diff < 0:
        return -100000 + stone_diff
    else:
        return 0

# --- ルール関連のヘルパー関数 ---

def board_empty_count(board):
    """盤面上の空きマスの数を数える"""
    return sum(row.count(EMPTY) for row in board)

def find_valid_moves(board, color, opponent):
    """
    現在の盤面における有効な手を全てリストアップする。
    """
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
    """
    指定位置に置いた場合に取れる石の数を数える。
    """
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
    """
    指定の位置に石を打ち、裏返す操作を行う。
    """
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
