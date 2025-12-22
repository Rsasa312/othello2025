import sys
sys.setrecursionlimit(2000)

# --- 定数定義 ---
EMPTY = 0
BLACK = 1
WHITE = 2

def myai(board, color):
    """
    改善版AI: ゲーム段階に応じた戦略を採用
    - 序盤: 中央制御と機動力重視
    - 中盤: 位置評価バランス
    - 終盤: 確定石と石数最大化
    """
    opponent = 3 - color
    valid_moves = find_valid_moves(board, color, opponent)
    
    if not valid_moves:
        return None
    
    empty_count = board_empty_count(board)
    total_squares = len(board) * len(board)
    
    # ゲーム段階の判定
    if empty_count > total_squares * 0.7:  # 序盤
        return choose_opening_move(board, valid_moves, color, opponent)
    elif empty_count > total_squares * 0.3:  # 中盤
        return choose_midgame_move(board, valid_moves, color, opponent)
    else:  # 終盤
        return choose_endgame_move(board, valid_moves, color, opponent)

def choose_opening_move(board, valid_moves, color, opponent):
    """序盤: 機動力(相手の選択肢を増やさない)を重視"""
    best_move = None
    best_score = float('-inf')
    
    for r, c, flips in valid_moves:
        new_board = [row[:] for row in board]
        make_move(new_board, r, c, color, opponent)
        
        # 相手の手数を評価(少ない方が良い)
        opponent_moves = len(find_valid_moves(new_board, opponent, color))
        mobility_score = -opponent_moves * 10
        
        # 位置評価
        position_score = evaluate_position(new_board, color)
        
        # 危険な場所(角の隣)を避ける
        danger_penalty = get_danger_penalty(r, c, len(board))
        
        total_score = mobility_score + position_score * 0.5 + danger_penalty
        
        if total_score > best_score:
            best_score = total_score
            best_move = (r, c)
    
    return best_move

def choose_midgame_move(board, valid_moves, color, opponent):
    """中盤: バランス重視の評価"""
    best_move = None
    best_score = float('-inf')
    
    for r, c, flips in valid_moves:
        new_board = [row[:] for row in board]
        make_move(new_board, r, c, color, opponent)
        
        # 複数要素を組み合わせた評価
        position_score = evaluate_position(new_board, color)
        mobility = evaluate_mobility(new_board, color, opponent)
        stability = evaluate_stability(new_board, color)
        
        total_score = position_score + mobility * 5 + stability * 3
        
        if total_score > best_score:
            best_score = total_score
            best_move = (r, c)
    
    return best_move

def choose_endgame_move(board, valid_moves, color, opponent):
    """終盤: 石数最大化を重視"""
    best_move = None
    best_score = float('-inf')
    
    for r, c, flips in valid_moves:
        new_board = [row[:] for row in board]
        make_move(new_board, r, c, color, opponent)
        
        # 石数差
        my_count = sum(row.count(color) for row in new_board)
        opp_count = sum(row.count(opponent) for row in new_board)
        disc_diff = my_count - opp_count
        
        # 確定石の数
        stability = evaluate_stability(new_board, color)
        
        total_score = disc_diff * 2 + stability * 5
        
        if total_score > best_score:
            best_score = total_score
            best_move = (r, c)
    
    return best_move

def evaluate_position(board, color):
    """位置評価(角と辺を重視)"""
    opponent = 3 - color
    size = len(board)
    score = 0
    
    # 標準的な重み行列
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
    
    for r in range(size):
        for c in range(size):
            if board[r][c] == color:
                score += weights[r][c]
            elif board[r][c] == opponent:
                score -= weights[r][c]
    
    return score

def evaluate_mobility(board, color, opponent):
    """機動力評価(自分の手数 - 相手の手数)"""
    my_moves = len(find_valid_moves(board, color, opponent))
    opp_moves = len(find_valid_moves(board, opponent, color))
    return my_moves - opp_moves

def evaluate_stability(board, color):
    """確定石の評価(角と辺の確定石を計算)"""
    size = len(board)
    score = 0
    
    # 角の確定石
    corners = [(0, 0), (0, size-1), (size-1, 0), (size-1, size-1)]
    for r, c in corners:
        if board[r][c] == color:
            score += 25
    
    # 辺の確定石(簡易版)
    edges = []
    for i in range(size):
        edges.extend([(0, i), (size-1, i), (i, 0), (i, size-1)])
    
    for r, c in set(edges):
        if board[r][c] == color:
            score += 5
    
    return score

def get_danger_penalty(r, c, size):
    """危険な位置(角の隣のX位置とC位置)へのペナルティ"""
    # X位置(角の斜め隣)
    x_positions = [(1, 1), (1, size-2), (size-2, 1), (size-2, size-2)]
    if (r, c) in x_positions:
        return -100
    
    # C位置(角の縦横隣)
    c_positions = []
    for corner_r, corner_c in [(0, 0), (0, size-1), (size-1, 0), (size-1, size-1)]:
        if corner_r == 0:
            c_positions.append((1, corner_c))
        elif corner_r == size-1:
            c_positions.append((size-2, corner_c))
        if corner_c == 0:
            c_positions.append((corner_r, 1))
        elif corner_c == size-1:
            c_positions.append((corner_r, size-2))
    
    if (r, c) in c_positions:
        return -50
    
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
