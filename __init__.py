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
