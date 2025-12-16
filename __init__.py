import sys
import random

# 再帰の深さを増加
sys.setrecursionlimit(2000)

# --- 定数定義 ---
EMPTY = 0
BLACK = 1
WHITE = 2

# --- AIのエントリポイント ---

def myai(board, color):
    """
    複数の候補から確率的に選ぶAI
    """
    opponent = 3 - color
    valid_moves = find_valid_moves(board, color, opponent)
    
    if not valid_moves:
        return None

    empty_count = board_empty_count(board)
    
    # 探索深度
    if empty_count <= 8:
        search_depth = empty_count
    elif empty_count <= 14:
        search_depth = 7
    else:
        search_depth = 5

    # 各手を評価
    move_evals = []
    alpha = -float('inf')
    beta = float('inf')

    for r, c, flips in valid_moves:
        new_board = [row[:] for row in board]
        make_move(new_board, r, c, color, opponent)
        
        eval_score = minimax(new_board, opponent, search_depth - 1, False, color, alpha, beta)
        move_evals.append((r, c, eval_score))
        alpha = max(alpha, eval_score)

    # 評価値でソート
    move_evals.sort(key=lambda x: x[2], reverse=True)
    
    # 上位30%の手からランダムに選ぶ
    top_n = max(1, len(move_evals) // 3)
    top_moves = move_evals[:top_n]
    
    # ランダムに選択（ただし最善手の確率を高くする）
    weights = [1.0 / (i + 1) for i in range(len(top_moves))]
    selected = random.choices(top_moves, weights=weights, k=1)[0]
    
    return (selected[0], selected[1])

# --- ミニマックス探索 ---

def minimax(board, current_player_color, depth, is_maximizing_player, ai_color, alpha, beta):
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
            my_stones = sum(row.count(ai_color) for row in board)
            opp_stones = sum(row.count(3 - ai_color) for row in board)
            return (my_stones - opp_stones) * 10000
        
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
    バランスの取れた評価関数
    """
    opponent = 3 - color
    size = len(board)
    score = 0
    
    empty_count = board_empty_count(board)
    total = size * size
    progress = (total - empty_count) / total
    
    # 位置の重み
    weights = [
        [100, -25,  10,   5,   5,  10, -25, 100],
        [-25, -50,   1,   1,   1,   1, -50, -25],
        [ 10,   1,   5,   2,   2,   5,   1,  10],
        [  5,   1,   2,   1,   1,   2,   1,   5],
        [  5,   1,   2,   1,   1,   2,   1,   5],
        [ 10,   1,   5,   2,   2,   5,   1,  10],
        [-25, -50,   1,   1,   1,   1, -50, -25],
        [100, -25,  10,   5,   5,  10, -25, 100]
    ]
    
    # 1. 位置評価
    position_weight = 1.5 if progress < 0.6 else 0.8
    for r in range(size):
        for c in range(size):
            if board[r][c] == color:
                score += weights[r][c] * position_weight
            elif board[r][c] == opponent:
                score -= weights[r][c] * position_weight
    
    # 2. モビリティ
    if progress < 0.8:
        my_mobility = len(find_valid_moves(board, color, opponent))
        opp_mobility = len(find_valid_moves(board, opponent, color))
        
        if my_mobility == 0 and opp_mobility > 0:
            score -= 10000
        elif opp_mobility == 0 and my_mobility > 0:
            score += 10000
        else:
            score += (my_mobility - opp_mobility) * 20
    
    # 3. 石の数（終盤のみ）
    if progress >= 0.75:
        my_stones = sum(row.count(color) for row in board)
        opp_stones = sum(row.count(opponent) for row in board)
        score += (my_stones - opp_stones) * 50
    
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
