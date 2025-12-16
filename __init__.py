import sys
sys.setrecursionlimit(2000)

def myai(board, color):
    """
    オセロAIのエントリポイント（sakura互換）
    3手先ミニマックス + 角優先 + 貪欲評価
    """
    opponent = 3 - color
    SEARCH_DEPTH = 3

    valid_moves = find_valid_moves(board, color, opponent)
    if not valid_moves:
        return None

    best_eval = -float('inf')
    best_move = None

    for r, c, flips in valid_moves:
        new_board = [row[:] for row in board]
        make_move(new_board, r, c, color, opponent)

        eval = minimax(
            new_board,
            opponent,
            SEARCH_DEPTH - 1,
            False,
            color,
            -float('inf'),
            float('inf')
        )

        if eval > best_eval:
            best_eval = eval
            best_move = (r, c)

    return best_move


def minimax(board, current_color, depth, is_max, ai_color, alpha, beta):
    opponent = 3 - current_color

    if depth == 0 or board_empty_count(board) == 0:
        return evaluate(board, ai_color)

    valid_moves = find_valid_moves(board, current_color, opponent)

    if not valid_moves:
        return minimax(board, opponent, depth - 1, not is_max, ai_color, alpha, beta)

    if is_max:
        value = -float('inf')
        for r, c, _ in valid_moves:
            new_board = [row[:] for row in board]
            make_move(new_board, r, c, current_color, opponent)
            value = max(value, minimax(new_board, opponent, depth - 1, False, ai_color, alpha, beta))
            alpha = max(alpha, value)
            if beta <= alpha:
                break
        return value
    else:
        value = float('inf')
        for r, c, _ in valid_moves:
            new_board = [row[:] for row in board]
            make_move(new_board, r, c, current_color, opponent)
            value = min(value, minimax(new_board, opponent, depth - 1, True, ai_color, alpha, beta))
            beta = min(beta, value)
            if beta <= alpha:
                break
        return value


def evaluate(board, color):
    size = len(board)
    opponent = 3 - color

    # 角・X打ち・辺を考慮した重み
    WEIGHTS = [
        [120, -40, 20,  5,  5, 20, -40, 120],
        [-40, -80, -1, -1, -1, -1, -80, -40],
        [ 20,  -1,  5,  1,  1,  5,  -1,  20],
        [  5,  -1,  1,  0,  0,  1,  -1,   5],
        [  5,  -1,  1,  0,  0,  1,  -1,   5],
        [ 20,  -1,  5,  1,  1,  5,  -1,  20],
        [-40, -80, -1, -1, -1, -1, -80, -40],
        [120, -40, 20,  5,  5, 20, -40, 120]
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

    # モビリティ（動ける手が多い方が有利）
    my_moves = len(find_valid_moves(board, color, opponent))
    opp_moves = len(find_valid_moves(board, opponent, color))
    score += (my_moves - opp_moves) * 10

    total_stones = size * size - board_empty_count(board)

    # 終盤は石数を重視（貪欲）
    if total_stones >= size * size * 0.7:
        score += stone_diff * 20

    # 完全終局
    if board_empty_count(board) == 0:
        return stone_diff * 1000

    return score


def board_empty_count(board):
    count = 0
    for row in board:
        count += row.count(0)
    return count


def find_valid_moves(board, color, opponent):
    size = len(board)
    valid_moves = []
    for r in range(size):
        for c in range(size):
            if board[r][c] == 0:
                flips = count_flips(board, r, c, color, opponent)
                if flips > 0:
                    valid_moves.append((r, c, flips))
    return valid_moves


def count_flips(board, row, col, color, opponent):
    size = len(board)
    flips = 0

    directions = [
        (-1, -1), (-1, 0), (-1, 1),
        (0, -1),          (0, 1),
        (1, -1),  (1, 0), (1, 1)
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
        (-1, -1), (-1, 0), (-1, 1),
        (0, -1),          (0, 1),
        (1, -1),  (1, 0), (1, 1)
    ]

    for dr, dc in directions:
        r, c = row + dr, col + dc
        temp = []

        while 0 <= r < size and 0 <= c < size:
            if board[r][c] == opponent:
                temp.append((r, c))
            elif board[r][c] == color:
                for fr, fc in temp:
                    board[fr][fc] = color
                break
            else:
                break
            r += dr
            c += dc
