import random

EMPTY = 0
BLACK = 1
WHITE = 2

def myai(board, color):
    opponent = 3 - color
    valid_moves = find_valid_moves(board, color, opponent)

    if not valid_moves:
        return None

    empty_cnt = board_empty_count(board)

    # 終盤は最大評価、それ以外は最小評価
    if empty_cnt <= 12:
        best_eval = float('-inf')
        best_move = None
        for r, c, flips in valid_moves:
            new_board = [row[:] for row in board]
            make_move(new_board, r, c, color, opponent)

            eval_score = evaluate(new_board, color) + flips * 0.1

            if eval_score > best_eval or (
                eval_score == best_eval and random.random() < 0.5
            ):
                best_eval = eval_score
                best_move = (r, c)
        return best_move

    else:
        worst_eval = float('inf')
        worst_move = None
        for r, c, flips in valid_moves:
            new_board = [row[:] for row in board]
            make_move(new_board, r, c, color, opponent)

            eval_score = evaluate(new_board, color) + flips * 0.1

            if eval_score < worst_eval or (
                eval_score == worst_eval and random.random() < 0.5
            ):
                worst_eval = eval_score
                worst_move = (r, c)
        return worst_move


def evaluate(board, color):
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


def board_empty_count(board):
    return sum(row.count(EMPTY) for row in board)


def find_valid_moves(board, color, opponent):
    size = len(board)
    valid_moves = []
    for r in range(size):
        for c in range(size):
            if board[r][c] == EMPTY:
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
            if board[r][c] == EMPTY:
                break
            elif board[r][c] == opponent:
                temp += 1
            else:
                flips += temp
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
            if board[r][c] == EMPTY:
                break
            elif board[r][c] == opponent:
                temp.append((r, c))
            else:
                for tr, tc in temp:
                    board[tr][tc] = color
                break
            r += dr
            c += dc
