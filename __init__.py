import sys

# 再帰の深さを増加
sys.setrecursionlimit(2000)

# --- 定数定義 ---
EMPTY = 0
BLACK = 1
WHITE = 2
SEARCH_DEPTH = 5

# --- AIのエントリポイント ---

def myai(board, color):
    """
    逆張り戦略：序盤は石を少なく、モビリティを重視
    """
    opponent = 3 - color
    valid_moves = find_valid_moves(board, color, opponent)
    
    if not valid_moves:
        return None

    empty_count = board_empty_count(board)
    
    # 探索深度
    if empty_count <= 10:
        search_depth = min(empty_count, 12)
    elif empty_count <= 18:
        search_depth = 6
    else:
        search_depth = SEARCH_DEPTH

    best_move = None
    best_eval = -float('inf')
    alpha = -float('inf')
    beta = float('inf')

    for r, c, flips in valid_moves:
        new_board = [row[:] for row in board]
        make_move(new_board, r, c, color, opponent)
        
        current_eval = minimax(new_board, opponent, search_depth - 1, False, color, alpha, beta, empty_count)
        
        if current_eval > best_eval:
            best_eval = current_eval
            best_move = (r, c)
            alpha = max(alpha, current_eval)

    return best_move

# --- ミニマックス探索 ---

def minimax(board, current_player_color, depth, is_maximizing_player, ai_color, alpha, beta, initial_empty):
    """
    ミニマックス探索（アルファベータ枝刈り付き）
    """
    opponent_color = 3 - current_player_color

    if depth == 0:
        return evaluate(board, ai_color, initial_empty)
    
    valid_moves = find_valid_moves(board, current_player_color, opponent_color)

    if not valid_moves:
        opponent_moves = find_valid_moves(board, opponent_color, current_player_color)
        
        if not opponent_moves:
            # ゲーム終了
            my_stones = sum(row.count(ai_color) for row in board)
            opp_stones = sum(row.count(3 - ai_color) for row in board)
            return (my_stones - opp_stones) * 10000
        
        # パス
        return minimax(board, opponent_color, depth - 1, not is_maximizing_player, ai_color, alpha, beta, initial_empty)
    
    if is_maximizing_player:
        max_eval = -float('inf')
        for r, c, flips in valid_moves:
            new_board = [row[:] for row in board]
            make_move(new_board, r, c, current_player_color, opponent_color)
            
            eval = minimax(new_board, opponent_color, depth - 1, False, ai_color, alpha, beta, initial_empty)
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
            
            eval = minimax(new_board, opponent_color, depth - 1, True, ai_color, alpha, beta, initial_empty)
            min_eval = min(min_eval, eval)
            beta = min(beta, eval)
            if beta <= alpha:
                break
        return min_eval

# --- 評価関数 ---

def evaluate(board, color, initial_empty):
    """
    ゲーム段階に応じた評価関数
    """
    opponent = 3 - color
    size = len(board)
    score = 0
    
    total_squares = size * size
    current_empty = board_empty_count(board)
    game_progress = (total_squares - current_empty) / total_squares
    
    # 重みテーブル（角とX位置を強調）
    weights = [
        [120, -30,  15,   8,   8,  15, -30, 120],
        [-30, -40,  -2,  -2,  -2,  -2, -40, -30],
        [ 15,  -2,   5,   3,   3,   5,  -2,  15],
        [  8,  -2,   3,   2,   2,   3,  -2,   8],
        [  8,  -2,   3,   2,   2,   3,  -2,   8],
        [ 15,  -2,   5,   3,   3,   5,  -2,  15],
        [-30, -40,  -2,  -2,  -2,  -2, -40, -30],
        [120, -30,  15,   8,   8,  15, -30, 120]
    ]
    
    # 1. 位置評価
    for r in range(size):
        for c in range(size):
            if board[r][c] == color:
                score += weights[r][c]
            elif board[r][c] == opponent:
                score -= weights[r][c]
    
    # 2. モビリティ（序盤・中盤で超重要）
    my_mobility = len(find_valid_moves(board, color, opponent))
    opp_mobility = len(find_valid_moves(board, opponent, color))
    
    if game_progress < 0.75:
        # 序盤・中盤はモビリティを最重視
        if my_mobility == 0 and opp_mobility > 0:
            score -= 50000
        elif opp_mobility == 0 and my_mobility > 0:
            score += 50000
        else:
            mobility_weight = 80 if game_progress < 0.5 else 50
            score += (my_mobility - opp_mobility) * mobility_weight
    
    # 3. 石の数（序盤は少ない方が良い！終盤は多い方が良い）
    my_stones = sum(row.count(color) for row in board)
    opp_stones = sum(row.count(opponent) for row in board)
    stone_diff = my_stones - opp_stones
    
    if game_progress < 0.4:
        # 序盤：石が少ない方が有利（逆評価）
        score -= stone_diff * 15
    elif game_progress < 0.7:
        # 中盤：石の数はあまり気にしない
        score += stone_diff * 5
    else:
        # 終盤：石が多い方が有利
        score += stone_diff * 100
    
    # 4. 角の確保（常に超重要）
    corners = [(0, 0), (0, size-1), (size-1, 0), (size-1, size-1)]
    for r, c in corners:
        if board[r][c] == color:
            score += 1000
        elif board[r][c] == opponent:
            score -= 1000
    
    return score

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
