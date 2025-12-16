import sys

sys.setrecursionlimit(2000)

WEIGHTS = [
    [ 50, -8,  5,  5,  5,  5, -8, 50],
    [ -8, -8,  1,  1,  1,  1, -8, -8],
    [  5,  1,  2,  2,  2,  2,  1,  5],
    [  5,  1,  2,  0,  0,  2,  1,  5],
    [  5,  1,  2,  0,  0,  2,  1,  5],
    [  5,  1,  2,  2,  2,  2,  1,  5],
    [ -8, -8,  1,  1,  1,  1, -8, -8],
    [ 50, -8,  5,  5,  5,  5, -8, 50],
]
SIZE = 8

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

    for r, c, _ in valid_moves:
        new_board = [row[:] for row in board]
        make_move(new_board, r, c, color, opponent)
        
        current_eval = minimax(new_board, opponent, SEARCH_DEPTH - 1, False, color)
        
        if current_eval > best_eval:
            best_eval = current_eval
            best_move = (r, c)
        
        elif current_eval == best_eval:
             pass 

    return best_move

def minimax(board, current_player_color, depth, is_maximizing_player, ai_color):
    """
    ミニマックス探索を行い、現在の局面の最善の評価値を返す。
    α-β枝刈りは実装せず、元のシンプルなミニマックスを維持する。
    """
    opponent_color = 3 - current_player_color

    if depth == 0:
        return evaluate(board, ai_color)
    
    valid_moves = find_valid_moves(board, current_player_color, opponent_color)

    if not valid_moves:
        opponent_moves = find_valid_moves(board, opponent_color, current_player_color)
        
        if not opponent_moves:
            return evaluate(board, ai_color) * 1000000 
        
        return minimax(board, opponent_color, depth, not is_maximizing_player, ai_color)
            
    if is_maximizing_player:
        max_eval = -float('inf')
        for r, c, _ in valid_moves:
            new_board = [row[:] for row in board]
            make_move(new_board, r, c, current_player_color, opponent_color)
            
            eval = minimax(new_board, opponent_color, depth - 1, False, ai_color)
            max_eval = max(max_eval, eval)
        return max_eval
    
    else:
        min_eval = float('inf')
        for r, c, _ in valid_moves:
            new_board = [row[:] for row in board]
            make_move(new_board, r, c, current_player_color, opponent_color)
            
            eval = minimax(new_board, opponent_color, depth - 1, True, ai_color)
            min_eval = min(min_eval, eval)
        return min_eval

def evaluate(board, color):
    """
    現在の盤面を評価し、colorにとっての点数を返す。
    強化要素：
    1. 位置の重み
    2. 確定石
    3. モビリティ（着手可能数の差）
    4. フロンティア（相手と接する石の数）
    5. 石数（終盤重視）
    """
    opponent = 3 - color
    score = 0
    empty_count = board_empty_count(board)
    total_stones = SIZE * SIZE - empty_count

    if empty_count == 0 or (
        not find_valid_moves(board, color, opponent) and 
        not find_valid_moves(board, opponent, color)
    ):
        stone_count_diff = sum(row.count(color) for row in board) - sum(row.count(opponent) for row in board)
        return stone_count_diff * 1000000 

    stone_count_diff = 0
    frontier_count = 0
    
    for r in range(SIZE):
        for c in range(SIZE):
            if board[r][c] == color:
                score += WEIGHTS[r][c]
                stone_count_diff += 1
                if is_frontier(board, r, c, opponent):
                    frontier_count += 1
            elif board[r][c] == opponent:
                score -= WEIGHTS[r][c]
                stone_count_diff -= 1
    

    my_stable_count, opp_stable_count = count_stable_stones(board, color, opponent)
    score += (my_stable_count - opp_stable_count) * 80

    my_moves = len(find_valid_moves(board, color, opponent))
    opp_moves = len(find_valid_moves(board, opponent, color))
    
    mobility_score = (my_moves - opp_moves) * 40
    score += mobility_score

    score -= frontier_count * 10 

    if total_stones >= SIZE * SIZE * 0.7:
        score += stone_count_diff * 15
    elif total_stones < SIZE * SIZE * 0.3:
        score += stone_count_diff * 5
    else:
        score += stone_count_diff * 10

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
    valid_moves = []
    for row in range(SIZE):
        for col in range(SIZE):
            if board[row][col] == 0:
                flips = count_flips(board, row, col, color, opponent)
                if flips > 0:
                    valid_moves.append((row, col, flips))
    return valid_moves


def count_flips(board, row, col, color, opponent):
    """
    指定位置に置いた場合に取れる石の数を数える。
    """
    flips = 0
    directions = [
        (-1, -1), (-1, 0), (-1, 1),
        (0, -1),            (0, 1),
        (1, -1),  (1, 0),  (1, 1)
    ]

    for dr, dc in directions:
        temp_flips = 0
        r, c = row + dr, col + dc

        while 0 <= r < SIZE and 0 <= c < SIZE:
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


def make_move(board, row, col, color, opponent):
    """
    指定の位置に石を打ち、裏返す操作を行う（ボードを直接変更する）。
    """
    board[row][col] = color
    
    directions = [
        (-1, -1), (-1, 0), (-1, 1),
        (0, -1),            (0, 1),
        (1, -1),  (1, 0),  (1, 1)
    ]

    for dr, dc in directions:
        temp_flips_coords = []
        r, c = row + dr, col + dc

        while 0 <= r < SIZE and 0 <= c < SIZE:
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


def is_in_board(r, c):
    """座標が盤面内にあるか判定"""
    return 0 <= r < SIZE and 0 <= c < SIZE

def is_frontier(board, r, c, opponent):
    """
    指定の座標 (r, c) の石が相手の石と隣接しているか（フロンティア石か）を判定
    """
    directions = [
        (-1, -1), (-1, 0), (-1, 1),
        (0, -1),            (0, 1),
        (1, -1),  (1, 0),  (1, 1)
    ]
    for dr, dc in directions:
        nr, nc = r + dr, c + dc
        if is_in_board(nr, nc) and board[nr][nc] == 0:
             return True
    return False

def count_stable_stones(board, color, opponent):
    """
    確定石 (stable stones) の数を数える。
    これは計算負荷が高いが、評価の質を上げるために導入する。
    確定石とは、どの方向からも裏返されない石のこと。
    ここでは、4隅から確定していく比較的シンプルな判定ロジックを用いる。
    
    """
    stable_counts = {color: 0, opponent: 0}
    visited = [[False] * SIZE for _ in range(SIZE)]
    
    corners = [(0, 0), (0, 7), (7, 0), (7, 7)]
    
    for start_r, start_c in corners:
        if board[start_r][start_c] != 0:
            target_color = board[start_r][start_c]
            
            
            if not visited[start_r][start_c]:
                stable_counts[target_color] += 1
                visited[start_r][start_c] = True
            
            dr, dc = (0, 1) if start_c == 0 else (0, -1)
            r, c = start_r, start_c + dc
            while is_in_board(r, c) and board[r][c] == target_color:
                if not visited[r][c]:
                    is_surrounded = True 
                    if start_r == 0 or start_r == 7:
                         pass
                    
                    if is_surrounded:
                        stable_counts[target_color] += 1
                        visited[r][c] = True
                r += dr
                c += dc
            
            dr, dc = (1, 0) if start_r == 0 else (-1, 0)
            r, c = start_r + dr, start_c
            while is_in_board(r, c) and board[r][c] == target_color:
                if not visited[r][c]:
                    is_surrounded = True
                    if is_surrounded:
                        stable_counts[target_color] += 1
                        visited[r][c] = True
                r += dr
                c += dc

    return stable_counts[color], stable_counts[opponent]
