import sys
sys.setrecursionlimit(2000)

def myai(board, color):
    """
    改良版オセロAI
    ・3手先読み
    ・角最優先
    ・Xマス回避
    ・終盤は石数重視
    """
    opponent = 3 - color
    SEARCH_DEPTH = 3

    valid_moves = find_valid_moves(board, color, opponent)
    if not valid_moves:
        return None

    best_move = None
    best_eval = -float('inf')

    for r, c, _ in valid_moves:
        new_board = [row[:] for row in board]
        make_move(new_board, r, c, color, opponent)

        value = minimax(
            new_board,
            opponent,
            SEARCH_DEPTH - 1,
            False,
            color
        )

        if value > best_eval:
            best_eval = value
            best_move = (r, c)

    return best_move


def minimax(board, current_color, depth, is_maximizing, ai_color):
    opponent = 3 - current_color

    if depth == 0:
        return evaluate(board, ai_color)

    moves = find_valid_moves(board, current_color, opponent)

    if not moves:
        opp_moves = find_valid_moves(board, opponent, current_color)
        if not opp_moves:
            return evaluate(board, ai_color) * 1000
        return minimax(board, opponent, depth - 1, not is_maximizing, ai_color)

    if is_maximizing:
        best = -float('inf')
        for r, c, _ in moves:
            new_board = [row[:] for row in board]
            make_move(new_board, r, c, current_color, opponent)
            best = max(
                best,
                minimax(new_board, opponent, depth - 1, False, ai_color)
            )
        return best
    else:
        best = float('inf')
        for r, c, _ in moves:
            new_board = [row[:] for row in board]
            make_move(new_board, r, c, current_color, opponent)
            best = min(
                best,
                minimax(new_board, opponent, depth - 1, True, ai_color)
            )
        return best


def evaluate(board, color):
    size = len(board)
    opponent = 3 - color

    WEIGHTS = [
        [ 50, -8,  5,  5,  5,  5, -8, 50],
        [ -8, -8,  1,  1,  1,  1, -8, -8],
        [  5,  1,  2,  2,  2,  2,  1,  5],
        [  5,  1,  2,  0,  0,  2,  1,  5],
        [  5,  1,  2,  0,  0,  2,  1,  5],
        [  5,  1,  2,  2,  2,  2,  1,  5],
        [ -8, -8,  1,  1,  1,  1, -8, -8],
        [ 50, -8,  5,  5,  5,  5, -8, 50]
    ]

    score = 0
    stone_diff = 0

    for r in range(size):
        for c in range(size):
            if board[r][c] == color:
                score += WEIGHTS[r][c]
                stone_diff += 1
            elif board[r][c] == opponent:
                score -= WEIGHTS[r][c]
                stone_diff -= 1

    # 角評価（最重要）
    CORNERS = [(0,0),(0,7),(7,0),(7,7)]
    for r, c in CORNERS:
        if board[r][c] == color:
            score += 120
        elif board[r][c] == opponent:
            score -= 120

    # Xマス回避
    X_SQUARES = [(1,1),(1,6),(6,1),(6,6)]
    for r, c in X_SQUARES:
        if board[r][c] == color:
            score -= 50
        elif board[r][c] == opponent:
            score += 50

    empty = board_empty_count(board)
    total = size * size - empty

    # 終盤は貪欲に石数重視
    if total >= size * size * 0.7:
        score += stone_diff * 15

    # 完全終了
    if empty == 0:
        return stone_diff * 1000

    return score


def board_empty_count(board):
    count = 0
    for row in board:
        count += row.count(0)
    return count


def find_valid_moves(board, color, opponent):
    size = len(board)
    moves = []
    for r in range(size):
        for c in range(size):
            if board[r][c] == 0:
                flips = count_flips(board, r, c, color, opponent)
                if flips > 0:
                    moves.append((r, c, flips))
    return moves


def count_flips(board, row, col, color, opponent):
    size = len(board)
    flips = 0
    directions = [
        (-1,-1),(-1,0),(-1,1),
        (0,-1),        (0,1),
        (1,-1),(1,0),(1,1)
    ]

    for dr, dc in directions:
        r, c = row + dr, col + dc
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

    directions = [
        (-1,-1),(-1,0),(-1,1),
        (0,-1),        (0,1),
        (1,-1),(1,0),(1,1)
    ]

    for dr, dc in directions:
        r, c = row + dr, col + dc
        flips = []
        while 0 <= r < size and 0 <= c < size:
            if board[r][c] == opponent:
                flips.append((r, c))
            elif board[r][c] == color:
                for fr, fc in flips:
                    board[fr][fc] = color
                break
            else:
                break
            r += dr
            c += dc
