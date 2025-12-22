import random

EMPTY = 0
BLACK = 1
WHITE = 2

# ======================
# AIエントリポイント
# ======================
def myai(board, color):
    opponent = 3 - color
    valid_moves = find_valid_moves(board, color, opponent)

    if not valid_moves:
        return None

    empty_cnt = board_empty_count(board)

    best_score = float('-inf')
    best_move = None

    for r, c, flips in valid_moves:
        new_board = [row[:] for row in board]
        make_move(new_board, r, c, color, opponent)

        # 相手の最善手を1手だけ読む
        opp_moves = find_valid_moves(new_board, opponent, color)
        if opp_moves:
            worst_opp = float('inf')
            for orow, ocol, _ in opp_moves:
                tmp = [row[:] for row in new_board]
                make_move(tmp, orow, ocol, opponent, color)
                score = evaluate(tmp, color, empty_cnt)
                worst_opp = min(worst_opp, score)
            score = worst_opp
        else:
            score = evaluate(new_board, color, empty_cnt)

        # 同点ランダム
        if score > best_score or (
            score == best_score and random.random() < 0.5
        ):
            best_score = score
            best_move = (r, c)

    return best_move


# ======================
# 評価関数
# ======================
def evaluate(board, color, empty_cnt):
    opponent = 3 - color
    size = len(board)
    score = 0

    # 位置評価
    weights = [
        [120, -40,  20,   5,   5,  20, -40, 120],
        [-40, -60,  -5,  -5,  -5,  -5, -60, -40],
        [ 20,  -5,  15,   3,   3,  15,  -5,  20],
        [  5,  -5,   3,   1,   1,   3,  -5,   5],
        [  5,  -5,   3,   1,   1,   3,  -5,   5],
        [ 20,  -5,  15,   3,   3,  15,  -5,  20],
        [-40, -60,  -5,  -5,  -5,  -5, -60, -40],
        [120, -40,  20,   5,   5,  20, -40, 120]
    ]

    for r in range(size):
        for c in range(size):
            if board[r][c] == color:
                score += weights[r][c]
            elif board[r][c] == opponent:
                score -= weights[r][c]

    # モビリティ（相手の手を減らす）
    my_moves = len(find_valid_moves(board, color, opponent))
    opp_moves = len(find_valid_moves(board, opponent, color))
    score += (my_moves - opp_moves) * 5

    # 終盤は枚数重視
    if empty_cnt <= 18:
        score += count_stones(board, color) * 2
        score -= count_stones(board, opponent) * 2

    return score


# ======================
# 補助関数
# ======================
def board_empty_count(board):
    return sum(row.count(EMPTY) for row in board)


def count_stones(board, color):
    return sum(row.count(color) for row in board)


def find_valid_moves(board, color, opponent):
    size = len(board)
    moves = []
    for r in range(size):
        for c in range(size):
            if board[r][c] == EMPTY:
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
        tmp = 0
        while 0 <= r < size and 0 <= c < size:
            if board[r][c] == opponent:
                tmp += 1
            elif board[r][c] == color:
                flips += tmp
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
        temp = []
        r, c = row + dr, col + dc
        while 0 <= r < size and 0 <= c < size:
            if board[r][c] == opponent:
                temp.append((r, c))
            elif board[r][c] == color:
                for tr, tc in temp:
                    board[tr][tc] = color
                break
            else:
                break
            r += dr
            c += dc
