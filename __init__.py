import sys

# --- 定数定義 ---
EMPTY = 0
BLACK = 1
WHITE = 2

def myai(board, color):
    """
    戦略強化版AI:
    1. 角が取れるなら取る
    2. 角を占有している場合のみ、その周辺(C, X)を許可
    3. 角が空白なら、その周辺(C, X)への着手を禁止
    4. それ以外は、最も多くの石を取れる手を選択
    """
    opponent = 3 - color
    valid_moves = find_valid_moves(board, color, opponent)
    
    if not valid_moves:
        return None

    size = len(board)
    corners = [(0, 0), (0, size-1), (size-1, 0), (size-1, size-1)]
    
    # 危険地帯（角の隣：C打ち、X打ち）の定義
    danger_map = {
        (0, 0): [(0, 1), (1, 0), (1, 1)],
        (0, size-1): [(0, size-2), (1, size-1), (1, size-2)],
        (size-1, 0): [(size-2, 0), (size-1, 1), (size-2, 1)],
        (size-1, size-1): [(size-2, size-1), (size-1, size-2), (size-2, size-2)]
    }

    # --- 1. 角が取れるかチェック ---
    for r, c, flips in valid_moves:
        if (r, c) in corners:
            return (r, c)

    # --- 2. 候補手のフィルタリング ---
    filtered_moves = []
    for r, c, flips in valid_moves:
        is_danger_pos = False
        allowed_by_corner = False
        
        # この手が「どの角の周辺か」を特定
        for corner, adjacents in danger_map.items():
            if (r, c) in adjacents:
                is_danger_pos = True
                # もしその角が既に自分の石なら、打っても良い（優先度高）
                if board[corner[0]][corner[1]] == color:
                    allowed_by_corner = True
                break
        
        if is_danger_pos:
            if allowed_by_corner:
                # 角を占有している場合の周辺打ちは高評価（便宜上flipsをブースト）
                filtered_moves.append((r, c, flips + 100))
            else:
                # 角が空白（または相手の石）なら、ここには打たない
                continue
        else:
            # 危険地帯ではない普通の手
            filtered_moves.append((r, c, flips))

    # --- 3. 最も石が取れる場所を選択 ---
    # filtered_movesが空（危険地帯しか打つ場所がない）場合は元のvalid_movesから選ぶ
    target_list = filtered_moves if filtered_moves else valid_moves
    
    if not target_list:
        return None

    # flips（第3要素）が最大のものを選ぶ
    best_move = max(target_list, key=lambda x: x[2])
    return (best_move[0], best_move[1])

# --- ルール関連のヘルパー関数 ---
def find_valid_moves(board, color, opponent):
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
    size = len(board)
    total_flips = 0
    directions = [(-1, -1), (-1, 0), (-1, 1), (0, -1), (0, 1), (1, -1), (1, 0), (1, 1)]
    
    for dr, dc in directions:
        temp_flips = 0
        r, c = row + dr, col + dc
        while 0 <= r < size and 0 <= c < size:
            if board[r][c] == EMPTY:
                break
            elif board[r][c] == opponent:
                temp_flips += 1
            elif board[r][c] == color:
                total_flips += temp_flips
                break
            else:
                break
            r += dr
            c += dc
    return total_flips
