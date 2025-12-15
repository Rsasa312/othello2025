def myai(board, color):
    """
    sakura.othello と対戦できるオセロAI
    返り値: (x, y) または None（パス）
    """
    BLACK = 1
    WHITE = 2
    opponent = WHITE if color == BLACK else BLACK

    best_move = None
    best_count = -1

    corners = [(0, 0), (0, 5), (5, 0), (5, 5)]
    avoid = [(1, 1), (1, 4), (4, 1), (4, 4)]

    for row in range(6):
        for col in range(6):
            if board[row][col] != 0:
                continue

            count = count_flips(board, row, col, color, opponent)
            if count == 0:
                continue

            # 角を最優先
            if (col, row) in corners:
                return (col, row)

            # 危険マスを回避
            if (col, row) in avoid:
                continue

            if count > best_count:
                best_move = (col, row)
                best_count = count

    return best_move  # 無ければ None（パス）

def count_flips(board, row, col, color, opponent):
    directions = [
        (-1, -1), (-1, 0), (-1, 1),
        (0, -1),          (0, 1),
        (1, -1),  (1, 0), (1, 1)
    ]

    total_flips = 0

    for dr, dc in directions:
        r, c = row + dr, col + dc
        flips = 0

        while 0 <= r < 6 and 0 <= c < 6 and board[r][c] == opponent:
            flips += 1
            r += dr
            c += dc

        if flips > 0 and 0 <= r < 6 and 0 <= c < 6 and board[r][c] == color:
            total_flips += flips

    return total_flips
