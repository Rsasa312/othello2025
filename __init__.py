import sys

sys.setrecursionlimit(2000)

def myai(board, color):
    """
    オセロAIのエントリポイント。3手先を読んで最善の手を返す（sakura互換）
    """
    opponent = 3 - color
    SEARCH_DEPTH = 3 

    valid_moves = find_valid_moves(board, color, opponent) 
    
    if not valid_moves:
        return None

    best_move = None
    best_eval = -float('inf')

    for r, c, flips in valid_moves:
        new_board = [row[:] for row in board]
        make_move(new_board, r, c, color, opponent)
        
        current_eval = minimax(new_board, opponent, SEARCH_DEPTH - 1, False, color)
        
        if current_eval > best_eval:
            best_eval = current_eval
            best_move = (r, c)
        
        elif current_eval == best_eval and best_move is not None:
            pass 

    return best_move


def minimax(board, current_player_color, depth, is_maximizing_player, ai_color):
    """
    ミニマックス探索を行い、現在の局面の最善の評価値を返す。
    """
    opponent_color = 3 - current_player_color

    if depth == 0:
        return evaluate(board, ai_color)
    
    valid_moves = find_valid_moves(board, current_player_color, opponent_color)

    if not valid_moves:
        opponent_moves = find_valid_moves(board, opponent_color, current_player_color)
        
        if not opponent_moves:
            return evaluate(board, ai_color) * 1000 
        
        return minimax(board, opponent_color, depth - 1, not is_maximizing_player, ai_color)
            
    if is_maximizing_player:
        max_eval = -float('inf')
        for r, c, flips in valid_moves:
            new_board = [row[:] for row in board]
            make_move(new_board, r, c, current_player_color, opponent_color)
            
            eval = minimax(new_board, opponent_color, depth - 1, False, ai_color)
            max_eval = max(max_eval, eval)
        return max_eval
    else:
        min_eval = float('inf')
        for r, c, flips in valid_moves:
            new_board = [row[:] for row in board]
            make_move(new_board, r, c, current_player_color, opponent_color)
            
            eval = minimax(new_board, opponent_color, depth - 1, True, ai_color)
            min_eval = min(min_eval, eval)
        return min_eval


def evaluate(board, color):
    """
    現在の盤面を評価し、colorにとっての点数を返す。
    """
    size = len(board)
    opponent = 3 - color
    score = 0
    
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

    stone_count_diff = 0
    for r in range(size):
        for c in range(size):
            if board[r][c] == color:
                score += WEIGHTS[r][c]
                stone_count_diff += 1
            elif board[r][c] == opponent:
                score -= WEIGHTS[r][c]
                stone_count_diff -= 1

    # 角評価（超重要）
    corners = [(0,0),(0,7),(7,0),(7,7)]
    for r, c in corners:
        if board[r][c] == color:
            score += 120
        elif board[r][c] == opponent:
            score -= 120

    # Xマス（角隣）ペナルティ
    x_squares = [(1,1),(1,6),(6,1),(6,6)]
    for r, c in x_squares:
        if board[r][c] == color:
            score -= 60
        elif board[r][c] == opponent:
            score += 60

    total_stones = size * size - board_empty_count(board)

    # 終盤は石数を強く反映
    if total_stones >= size * size * 0.7:
        score += stone_count_diff * 15

    if board_empty_count(board) == 0:
        return stone_count_diff * 1000

    return score


def board_empty_count(board):
    """盤面上の空きマスの数を数えるヘルパー関数"""
    count = 0
    for row in board:
        count += row.count(0)
    return count


def find_valid_moves(board, color, opponent):
    """
    現在の盤面における有効な手を全てリストアップする。
    """
    size = len(board)
    valid_moves = []
    for row in range(size):
        for col in range(size):
            if board[row][col] == 0:
                flips = count_flips(board, row, col, color, opponent)
                if flips > 0:
                    valid_moves.append((row, col, flips))
    return valid_moves


def count_flips(board, row, col, color, opponent):
    """
    指定位置に置いた場合に取れる石の数を数える。
    """
    size = len(board)
    flips = 0

    directions = [
        (-1, -1), (-1, 0), (-1, 1),
        (0, -1),            (0, 1),
        (1, -1),  (1, 0),  (1, 1)
    ]

    for dr, dc in directions:
        temp_flips = 0
        r, c = row + dr, col + dc

        while 0 <= r < size and 0 <= c < size:
            if board[r][c] == 0:
                break
            elif board[r][c] == opponent:
                temp_flips += 1
            else: # board[r][c] == color
                flips += temp_flips
                break
            r += dr
            c += dc

    return flips


def make_move(board, row, col, color, opponent):
    """
    指定の位置に石を打ち、裏返す操作を行う（ボードを直接変更する）。
    """
    size = len(board)
    board[row][col] = color
    
    directions = [
        (-1, -1), (-1, 0), (-1, 1),
        (0, -1),            (0, 1),
        (1, -1),  (1, 0),  (1, 1)
    ]

    for dr, dc in directions:
        temp_flips_coords = []
        r, c = row + dr, col + dc

        while 0 <= r < size and 0 <= c < size:
            if board[r][c] == 0:
                break
            elif board[r][c] == opponent:
                temp_flips_coords.append((r, c))
            else: # board[r][c] == color
                for fr, fc in temp_flips_coords:
                    board[fr][fc] = color
                break
            r += dr
            c += dc
