import sys

# 再帰の深さを増加
sys.setrecursionlimit(2000)

# --- 定数定義 ---
EMPTY = 0
BLACK = 1
WHITE = 2

# --- AIのエントリポイント ---

def myai(board, color):
    """
    最悪手AIを反転：1手先の評価で最善手を選ぶ
    探索は一切なし
    """
    opponent = 3 - color
    valid_moves = find_valid_moves(board, color, opponent)
    
    if not valid_moves:
        return None

    # 最も評価値の高い手（最善手）を選ぶ
    best_move = None
    best_eval = -float('inf')

    for r, c, flips in valid_moves:
        new_board = [row[:] for row in board]
        make_move(new_board, r, c, color, opponent)
        
        # 1手先の評価のみ
        eval_score = simple_evaluate(new_board, color)
        
        if eval_score > best_eval:
            best_eval = eval_score
            best_move = (r, c)

    return best_move

def simple_evaluate(board, color):
    """
    シンプル評価：位置の重みのみ
    最悪手AIと同じ評価関数
    """
    opponent = 3 - color
    size = len(board)
    score = 0
    
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
