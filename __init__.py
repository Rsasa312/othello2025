# Generation ID: Hutch_1764575395735_jzsedj9a1 (前半)

def myai(board, color):
    """
    オセロAI:
    ・角を最優先
    ・危険マスを避ける
    ・取れる石が最大の手を選ぶ
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

            # 危険マスは避ける
            if (col, row) in avoid:
                continue

            if count > best_count:
                best_move = (col, row)
                best_count = count

    # 合法手が無い場合は None（パス）
    return best_move


def count_flips(board, row, col, color, opponent):
    """
    指定位置に石を置いた時に取れる石の数をカウント
    """
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


def apply_move(board, row, col, color):
    """
    ボードに石を置いて、取れる石をひっくり返す
    """
    BLACK = 1
    WHITE = 2
    opponent = WHITE if color == BLACK else BLACK

    directions = [
        (-1, -1), (-1, 0), (-1, 1),
        (0, -1),          (0, 1),
        (1, -1),  (1, 0), (1, 1)
    ]

    new_board = [r[:] for r in board]
    new_board[row][col] = color

    for dr, dc in directions:
        r, c = row + dr, col + dc
        flips = []

        while 0 <= r < 6 and 0 <= c < 6 and new_board[r][c] == opponent:
            flips.append((r, c))
            r += dr
            c += dc

        if flips and 0 <= r < 6 and 0 <= c < 6 and new_board[r][c] == color:
            for fr, fc in flips:
                new_board[fr][fc] = color

    return new_board


def print_board(board):
    """
    ボードを表示
    """
    for row in board:
        print(row)
    print()


def play_othello():
    """
    オセロゲーム:
    myai(黒) vs sakura.othello(白)
    """
    from sakura import othello

    board = [
        [0,0,0,0,0,0],
        [0,0,0,0,0,0],
        [0,0,1,2,0,0],
        [0,0,2,1,0,0],
        [0,0,0,0,0,0],
        [0,0,0,0,0,0]
    ]

    BLACK = 1
    WHITE = 2

    print("ゲーム開始")
    print_board(board)

    while True:
        # 黒のターン
        move = myai(board, BLACK)
        if move is not None:
            print(f"黒の手: {move}")
            board = apply_move(board, move[1], move[0], BLACK)
        else:
            print("黒はパス")

        # 白のターン
        white_move = othello.play()
        if white_move is not None:
            print(f"白の手: {white_move}")
            board = apply_move(board, white_move[1], white_move[0], WHITE)
        else:
            print("白はパス")

        print_board(board)

# Generation ID: Hutch_1764575395735_jzsedj9a1 (後半)
