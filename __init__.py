import copy

# 8方向
DIRS = [(-1,-1),(-1,0),(-1,1),(0,-1),(0,1),(1,-1),(1,0),(1,1)]

def inside(x, y):
    return 0 <= x < 8 and 0 <= y < 8

def opponent(c):
    return -c

def valid_moves(board, color):
    moves = []
    for x in range(8):
        for y in range(8):
            if board[x][y] != 0:
                continue
            for dx, dy in DIRS:
                nx, ny = x+dx, y+dy
                found = False
                while inside(nx, ny) and board[nx][ny] == opponent(color):
                    found = True
                    nx += dx
                    ny += dy
                if found and inside(nx, ny) and board[nx][ny] == color:
                    moves.append((x, y))
                    break
    return moves

def apply_move(board, move, color):
    x, y = move
    newb = copy.deepcopy(board)
    newb[x][y] = color
    for dx, dy in DIRS:
        nx, ny = x+dx, y+dy
        flips = []
        while inside(nx, ny) and newb[nx][ny] == opponent(color):
            flips.append((nx, ny))
            nx += dx
            ny += dy
        if flips and inside(nx, ny) and newb[nx][ny] == color:
            for fx, fy in flips:
                newb[fx][fy] = color
    return newb

def count_stones(board, color):
    return sum(board[x][y] == color for x in range(8) for y in range(8))

def evaluate(board, color):
    score = 0

    # 石数（貪欲）
    score += 2 * (count_stones(board, color) - count_stones(board, opponent(color)))

    # 角
    corners = [(0,0),(0,7),(7,0),(7,7)]
    for x, y in corners:
        if board[x][y] == color:
            score += 50
        elif board[x][y] == opponent(color):
            score -= 50

    # 行動可能数（相手を減らす）
    score += len(valid_moves(board, color))
    score -= len(valid_moves(board, opponent(color)))

    return score

def minimax(board, color, depth, maximizing):
    moves = valid_moves(board, color)
    if depth == 0 or not moves:
        return evaluate(board, color)

    if maximizing:
        best = -10**9
        for m in moves:
            b2 = apply_move(board, m, color)
            val = minimax(b2, opponent(color), depth-1, False)
            best = max(best, val)
        return best
    else:
        worst = 10**9
        for m in moves:
            b2 = apply_move(board, m, color)
            val = minimax(b2, opponent(color), depth-1, True)
            worst = min(worst, val)
        return worst

def myai(board, color):
    moves = valid_moves(board, color)
    if not moves:
        return None

    # 角があれば即取る
    for m in moves:
        if m in [(0,0),(0,7),(7,0),(7,7)]:
            return m

    best_move = moves[0]
    best_score = -10**9

    for m in moves:
        b2 = apply_move(board, m, color)
        score = minimax(b2, opponent(color), 2, False)  # 合計3手先
        if score > best_score:
            best_score = score
            best_move = m

    return best_move
