import sys
sys.setrecursionlimit(10000)

def myai(board, color):
    opponent = 3 - color
    DEPTH = 3

    moves = find_valid_moves(board, color, opponent)
    if not moves:
        return None

    best_val = -10**9
    best_move = None

    for r, c, _ in moves:
        b = [row[:] for row in board]
        make_move(b, r, c, color, opponent)

        empties = board_empty_count(b)

        if empties <= 10:
            val = exact_minimax(b, opponent, color)
        else:
            val = minimax(b, opponent, DEPTH-1, False, color)

        if val > best_val:
            best_val = val
            best_move = (r, c)

    return best_move


# ---------- 終盤完全探索（安全版） ----------

def exact_minimax(board, current, ai_color):
    opponent = 3 - current

    moves = find_valid_moves(board, current, opponent)

    if not moves:
        opp_moves = find_valid_moves(board, opponent, current)
        if not opp_moves:
            return final_score(board, ai_color)
        return exact_minimax(board, opponent, ai_color)

    if current == ai_color:
        best = -10**9
        for r, c, _ in moves:
            b = [row[:] for row in board]
            make_move(b, r, c, current, opponent)
            best = max(best, exact_minimax(b, opponent, ai_color))
        return best
    else:
        best = 10**9
        for r, c, _ in moves:
            b = [row[:] for row in board]
            make_move(b, r, c, current, opponent)
            best = min(best, exact_minimax(b, opponent, ai_color))
        return best


def final_score(board, color):
    diff = 0
    for row in board:
        for x in row:
            if x == color:
                diff += 1
            elif x == 3 - color:
                diff -= 1
    return diff * 1000


# ---------- 中盤探索 ----------

def minimax(board, current, depth, is_max, ai_color):
    opponent = 3 - current

    if depth == 0:
        return evaluate(board, ai_color)

    moves = find_valid_moves(board, current, opponent)

    if not moves:
        return minimax(board, opponent, depth, not is_max, ai_color)

    if is_max:
        best = -10**9
        for r, c, _ in moves:
            b = [row[:] for row in board]
            make_move(b, r, c, current, opponent)
            best = max(best, minimax(b, opponent, depth-1, False, ai_color))
        return best
    else:
        best = 10**9
        for r, c, _ in moves:
            b = [row[:] for row in board]
            make_move(b, r, c, current, opponent)
            best = min(best, minimax(b, opponent, depth-1, True, ai_color))
        return best


def evaluate(board, color):
    opponent = 3 - color
    score = 0
    for r in range(8):
        for c in range(8):
            if board[r][c] == color:
                score += 1
            elif board[r][c] == opponent:
                score -= 1
    return score


# ---------- ユーティリティ（元コード互換） ----------

def board_empty_count(board):
    return sum(row.count(0) for row in board)

def find_valid_moves(board, color, opponent):
    size = len(board)
    res = []
    for r in range(size):
        for c in range(size):
            if board[r][c] == 0:
                f = count_flips(board, r, c, color, opponent)
                if f > 0:
                    res.append((r, c, f))
    return res

def count_flips(board, row, col, color, opponent):
    size = len(board)
    flips = 0
    dirs = [(-1,-1),(-1,0),(-1,1),(0,-1),(0,1),(1,-1),(1,0),(1,1)]
    for dr, dc in dirs:
        r, c = row+dr, col+dc
        temp = 0
        while 0 <= r < size and 0 <= c < size:
            if board[r][c] == opponent:
                temp += 1
            elif board[r][c] == color:
                flips += temp
                break
            else:
                break
            r += dr
            c += dc
    return flips

def make_move(board, row, col, color, opponent):
    size = len(board)
    board[row][col] = color
    dirs = [(-1,-1),(-1,0),(-1,1),(0,-1),(0,1),(1,-1),(1,0),(1,1)]
    for dr, dc in dirs:
        r, c = row+dr, col+dc
        temp = []
        while 0 <= r < size and 0 <= c < size:
            if board[r][c] == opponent:
                temp.append((r,c))
            elif board[r][c] == color:
                for tr, tc in temp:
                    board[tr][tc] = color
                break
            else:
                break
            r += dr
            c += dc
