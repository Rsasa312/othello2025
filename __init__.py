import sys
sys.setrecursionlimit(3000)

def myai(board, color):
    """
    オセロAI（sakura互換）
    ・実質3手先ミニマックス
    ・角の取得/阻止を探索で処理
    ・モビリティ最優先
    """
    opponent = 3 - color
    DEPTH = 3

    valid_moves = find_valid_moves(board, color, opponent)
    if not valid_moves:
        return None

    best_eval = -float('inf')
    best_move = None
    size = len(board)

    for r, c, _ in valid_moves:
        new_board = [row[:] for row in board]
        make_move(new_board, r, c, color, opponent)

        # 🔥 相手に角を即与える手は強制排除
        if gives_corner(new_board, opponent, color):
            eval = -10**9
        else:
            eval = minimax(
                new_board,
                opponent,
                DEPTH - 1,
                False,
                color,
                -10**9,
                10**9
            )

        if eval > best_eval:
            best_eval = eval
            best_move = (r, c)

    return best_move


def minimax(board, current_color, depth, is_max, ai_color, alpha, beta):
    opponent = 3 - current_color

    # 終局 or 深さ終了
    if depth == 0 or board_empty_count(board) == 0:
        return evaluate(board, ai_color)

    valid_moves = find_valid_moves(board, current_color, opponent)

    # パス処理：深さを減らさない
    if not valid_moves:
        return minimax(board, opponent, depth, not is_max, ai_color, alpha, beta)

    if is_max:
        value = -10**9
        for r, c, _ in valid_moves:
            new_board = [row[:] for row in board]
            make_move(new_board, r, c, current_color, opponent)

            # 角を与える未来は極端に悪い
            if gives_corner(new_board, opponent, current_color):
                score = -10**9
            else:
                score = minimax(new_board, opponent, depth - 1, False, ai_color, alpha, beta)

            value = max(value, score)
            alpha = max(alpha, value)
            if beta <= alpha:
                break
        return value
    else:
        value = 10**9
        for r, c, _ in valid_moves:
            new_board = [row[:] for row in board]
            make_move(new_board, r, c, current_color, opponent)

            if gives_corner(new_board, opponent, current_color):
                score = 10**9
            else:
                score = minimax(new_board, opponent, depth - 1, True, ai_color, alpha, beta)

            value = min(value, score)
            beta = min(beta, value)
            if beta <= alpha:
                break
        return value


def gives_corner(board, player, opponent):
    size = len(board)
    corners = [(0,0),(0,size-1),(size-1,0),(size-1,size-1)]
    moves = find_valid_moves(board, player, opponent)
    for r, c, _ in moves:
        if (r, c) in corners:
            return True
    return False


def evaluate(board, color):
    size = len(board)
    opponent = 3 - color

    # 角・辺・X打ち
    WEIGHTS = [
        [100, -40, 20,  5,  5, 20, -40, 100],
        [-40, -80, -5, -5, -5, -5, -80, -40],
        [ 20,  -5, 10,  3,  3, 10,  -5,  20],
        [  5,  -5,  3,  0,  0,  3,  -5,   5],
        [  5,  -5,  3,  0,  0,  3,  -5,   5],
        [ 20,  -5, 10,  3,  3, 10,  -5,  20],
        [-40, -80, -5, -5, -5, -5, -80, -40],
        [100, -40, 20,  5,  5, 20, -40, 100]
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

    # 🔥 モビリティ最優先
    my_moves = len(find_valid_moves(board, color, opponent))
    opp_moves = len(find_valid_moves(board, opponent, color))
    score += (my_moves - opp_moves) * 40

    total = size * size - board_empty_count(board)

    # 中盤は石を持ちすぎると不利
    if total < size * size * 0.65:
        score -= stone_diff * 4
    else:
        score += stone_diff * 25

    if board_empty_count(board) == 0:
        return stone_diff * 10000

    return score


def board_empty_count(board):
    return sum(row.count(0) for row in board)


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
