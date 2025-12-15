# Generation ID: Hutch_1763364959942_kj0qep3xy (前半)

def myai(board, color):
    """
    オセロで最も多くの石が取れる位置を返す
    """
    size = len(board)
    opponent = 3 - color

    valid_moves = []

    for row in range(size):
        for col in range(size):
            if board[row][col] == 0:
                flips = count_flips(board, row, col, color, opponent)
                if flips > 0:
                    valid_moves.append((col, row, flips))

    if not valid_moves:
        return None

    corners = [(0, 0), (0, size-1), (size-1, 0), (size-1, size-1)]

    corner_moves = [m for m in valid_moves if (m[0], m[1]) in corners]

    if corner_moves:
        corner_moves.sort(key=lambda x: x[2], reverse=True)
        return (corner_moves[0][0], corner_moves[0][1])

    valid_moves.sort(key=lambda x: x[2], reverse=True)
    return (valid_moves[0][0], valid_moves[0][1])


def count_flips(board, row, col, color, opponent):
    """
    指定位置に置いた場合に取れる石の数を数える
    """
    size = len(board)
    flips = 0

    directions = [(-1, -1), (-1, 0), (-1, 1), (0, -1), (0, 1), (1, -1), (1, 0), (1, 1)]

    for dr, dc in directions:
        temp_flips = 0
        r, c = row + dr, col + dc

        while 0 <= r < size and 0 <= c < size:
            if board[r][c] == 0:
                break
            elif board[r][c] == opponent:
                temp_flips += 1
            else:
                flips += temp_flips
                break

            r += dr
            c += dc

    return flips


def apply_move(board, row, col, color):
    """
    盤面に着手を適用する
    """
    size = len(board)
    opponent = 3 - color
    board[row][col] = color

    directions = [(-1, -1), (-1, 0), (-1, 1), (0, -1), (0, 1), (1, -1), (1, 0), (1, 1)]

    for dr, dc in directions:
        temp_flips = []
        r, c = row + dr, col + dc

        while 0 <= r < size and 0 <= c < size:
            if board[r][c] == 0:
                break
            elif board[r][c] == opponent:
                temp_flips.append((r, c))
            else:
                for tr, tc in temp_flips:
                    board[tr][tc] = color
                break

            r += dr
            c += dc

# Generation ID: Hutch_1763364959942_kj0qep3xy (後半)

board = [[0,0,0,0,0,0],
         [0,0,0,0,0,0],
         [0,0,1,2,0,0],
         [0,0,2,1,0,0],
         [0,0,0,0,0,0],
         [0,0,0,0,0,0]]
color = 1
myai(board, color)
