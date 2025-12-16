import sys
sys.setrecursionlimit(5000)

BOARD_SIZE = 8
EMPTY, BLACK, WHITE = 0, 1, 2
WEIGHTS = [
    [ 50, -8, 5, 5, 5, 5, -8, 50],
    [ -8, -8, 1, 1, 1, 1, -8, -8],
    [  5,  1, 2, 2, 2, 2,  1,  5],
    [  5,  1, 2, 0, 0, 2,  1,  5],
    [  5,  1, 2, 0, 0, 2,  1,  5],
    [  5,  1, 2, 2, 2, 2,  1,  5],
    [ -8, -8, 1, 1, 1, 1, -8, -8],
    [ 50, -8, 5, 5, 5, 5, -8, 50]
]
DIRECTIONS = [
    (-1, -1), (-1, 0), (-1, 1),
    (0, -1),           (0, 1),
    (1, -1),  (1, 0),  (1, 1)
]


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

    alpha = -float('inf')
    beta = float('inf')

    for r, c, flips in valid_moves:
        new_board = [row[:] for row in board]
        make_move(new_board, r, c, color, opponent)
        
        current_eval = minimax(new_board, opponent, SEARCH_DEPTH - 1, False, color, alpha, beta)
        
        if current_eval > best_eval:
            best_eval = current_eval
            best_move = (r, c)
        
        alpha = max(alpha, current_eval)
        if alpha >= beta:
            break
            
    return best_move

def minimax(board, current_player_color, depth, is_maximizing_player, ai_color, alpha, beta):
    """
    ミニマックス探索（アルファベータ枝刈り付き）
    """
    opponent_color = 3 - current_player_color

    if depth == 0:
        return evaluate(board, ai_color)
    
    valid_moves = find_valid_moves(board, current_player_color, opponent_color)

    if not valid_moves:
        opponent_moves = find_valid_moves(board, opponent_color, current_player_color)
        
        if not opponent_moves:
            return evaluate(board, ai_color) * 1000000
        
        return minimax(board, opponent_color, depth, not is_maximizing_player, ai_color, alpha, beta)
            
    if is_maximizing_player:
        max_eval = -float('inf')
        for r, c, flips in valid_moves:
            new_board = [row[:] for row in board]
            make_move(new_board, r, c, current_player_color, opponent_color)
            
            eval = minimax(new_board, opponent_color, depth - 1, False, ai_color, alpha, beta)
            max_eval = max(max_eval, eval)
            
            alpha = max(alpha, eval)
            if alpha >= beta:
                break 
        return max_eval
    else: # is_minimizing_player
        min_eval = float('inf')
        for r, c, flips in valid_moves:
            new_board = [row[:] for row in board]
            make_move(new_board, r, c, current_player_color, opponent_color)
            
            eval = minimax(new_board, opponent_color, depth - 1, True, ai_color, alpha, beta)
            min_eval = min(min_eval, eval)
            
            beta = min(beta, eval)
            if alpha >= beta:
                break
        return min_eval


def evaluate(board, color):
    """
    現在の盤面を評価し、colorにとっての点数を返す。
    強化された評価関数: 位置の重み、モビリティ、確定石、フロンティアの4要素を考慮。
    """
    opponent = 3 - color
    score = 0
    total_stones = 64 - board_empty_count(board)

    position_score = 0
    for r in range(BOARD_SIZE):
        for c in range(BOARD_SIZE):
            if board[r][c] == color:
                position_score += WEIGHTS[r][c]
            elif board[r][c] == opponent:
                position_score -= WEIGHTS[r][c]
    
    my_stable = find_stable_stones(board, color)
    op_stable = find_stable_stones(board, opponent)
    stable_diff = my_stable - op_stable
    
    stable_score = stable_diff * 30 
    
    my_mobility = len(find_valid_moves(board, color, opponent))
    op_mobility = len(find_valid_moves(board, opponent, color))
    
    mobility_diff = my_mobility - op_mobility
    
    mobility_score = mobility_diff * 10
    
    my_frontier = count_frontier_stones(board, color)
    op_frontier = count_frontier_stones(board, opponent)
    
    frontier_diff = op_frontier - my_frontier
    
    frontier_score = frontier_diff * 5
    
    stone_count_diff = 0
    for r in range(BOARD_SIZE):
        for c in range(BOARD_SIZE):
            if board[r][c] == color:
                stone_count_diff += 1
            elif board[r][c] == opponent:
                stone_count_diff -= 1

    disk_score = 0
    if total_stones >= 64 - 20:
        disk_score = stone_count_diff * 100
        
    if total_stones == 64:
        return stone_count_diff * 1000000

    score = position_score + mobility_score + stable_score + frontier_score + disk_score

    return score



def board_empty_count(board):
    """盤面上の空きマスの数を数えるヘルパー関数"""
    count = 0
    for row in board:
        count += row.count(EMPTY)
    return count

def find_valid_moves(board, color, opponent):
    """
    現在の盤面における有効な手を全てリストアップする。
    """
    valid_moves = []
    for row in range(BOARD_SIZE):
        for col in range(BOARD_SIZE):
            if board[row][col] == EMPTY:
                flips = count_flips(board, row, col, color, opponent)
                if flips > 0:
                    valid_moves.append((row, col, flips)) 
    return valid_moves

def count_flips(board, row, col, color, opponent):
    """
    指定位置に置いた場合に取れる石の数を数える。
    """
    flips = 0
    for dr, dc in DIRECTIONS:
        temp_flips = 0
        r, c = row + dr, col + dc

        while 0 <= r < BOARD_SIZE and 0 <= c < BOARD_SIZE:
            if board[r][c] == EMPTY:
                break
            elif board[r][c] == opponent:
                temp_flips += 1
            else:
                flips += temp_flips
                break
            r += dr
            c += dc
    return flips

def make_move(board, row, col, color, opponent):
    """
    指定の位置に石を打ち、裏返す操作を行う（ボードを直接変更する）。
    """
    board[row][col] = color
    
    for dr, dc in DIRECTIONS:
        temp_flips_coords = []
        r, c = row + dr, col + dc

        while 0 <= r < BOARD_SIZE and 0 <= c < BOARD_SIZE:
            if board[r][c] == EMPTY:
                break
            elif board[r][c] == opponent:
                temp_flips_coords.append((r, c))
            else: # board[r][c] == color
                for fr, fc in temp_flips_coords:
                    board[fr][fc] = color
                break
            r += dr
            c += dc


def count_frontier_stones(board, color):
    """
    フロンティア（相手に隣接している自分の石）の数を数える。
    """
    frontier_count = 0
    for r in range(BOARD_SIZE):
        for c in range(BOARD_SIZE):
            if board[r][c] == color:
                for dr, dc in DIRECTIONS:
                    nr, nc = r + dr, c + dc
                    if 0 <= nr < BOARD_SIZE and 0 <= nc < BOARD_SIZE and board[nr][nc] == EMPTY:
                        frontier_count += 1
                        break
    return frontier_count

def find_stable_stones(board, color):
    """
    確定石（安定石）の数を数える。
    この実装では、よりシンプルな「四隅からの探索」で確定石を検出します。
    """
    stable_count = 0
    is_stable = [[False] * BOARD_SIZE for _ in range(BOARD_SIZE)]
    
    corners = [(0, 0), (0, 7), (7, 0), (7, 7)]
    for r, c in corners:
        if board[r][c] == color and not is_stable[r][c]:
            queue = [(r, c)]
            is_stable[r][c] = True
            
            while queue:
                cr, cc = queue.pop(0)
                stable_count += 1
                                
                for dr, dc in DIRECTIONS:
                    nr, nc = cr + dr, cc + dc
                    if 0 <= nr < BOARD_SIZE and 0 <= nc < BOARD_SIZE and \
                       board[nr][nc] == color and not is_stable[nr][nc]:
                        
                        
                        is_stable[nr][nc] = True
                        queue.append((nr, nc))
    

    
    return stable_count
