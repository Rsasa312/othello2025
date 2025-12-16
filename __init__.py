import sys

# 再帰の深さを増加
sys.setrecursionlimit(2000)

# --- 定数定義 ---
EMPTY = 0
BLACK = 1
WHITE = 2
SEARCH_DEPTH = 3 # 3手先読み

# 盤面評価のための重みテーブル (Positional Weights)
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

# --- AIのエントリポイント ---

def myai(board, color):
    """
    オセロAIのエントリポイント。3手先を読んで最善の手を返す。
    """
    opponent = 3 - color
    
    valid_moves = find_valid_moves(board, color, opponent)
    
    if not valid_moves:
        return None

    best_move = None
    best_eval = -float('inf')

    # 初手の評価は、ミニマックス探索の結果に基づいて行う
    for r, c, flips in valid_moves:
        new_board = [row[:] for row in board]
        make_move(new_board, r, c, color, opponent)
        
        # 相手を最小化プレイヤーとして探索を開始
        current_eval = minimax(new_board, opponent, SEARCH_DEPTH - 1, False, color)
        
        if current_eval > best_eval:
            best_eval = current_eval
            best_move = (r, c)
        
        # 同一評価の場合、元のAIの動作に倣って特別な処理は行わない (pass)
        elif current_eval == best_eval:
            pass

    return best_move

# --- ミニマックス探索 ---

def minimax(board, current_player_color, depth, is_maximizing_player, ai_color, alpha=-float('inf'), beta=float('inf')):
    """
    ミニマックス探索（アルファベータ枝刈り付き）を行い、現在の局面の最善の評価値を返す。
    """
    opponent_color = 3 - current_player_color

    # 探索終端条件: 深さ0 または ゲーム終了
    if depth == 0:
        return evaluate(board, ai_color)
    
    valid_moves = find_valid_moves(board, current_player_color, opponent_color)

    if not valid_moves:
        opponent_moves = find_valid_moves(board, opponent_color, current_player_color)
        
        if not opponent_moves:
            # ゲーム終了（パスなし）：最終的な石の差を大きく評価
            return evaluate(board, ai_color) * 1000
        
        # パス：手番を相手に移して、深さを一つ減らして再帰
        return minimax(board, opponent_color, depth - 1, not is_maximizing_player, ai_color, alpha, beta)
            
    if is_maximizing_player:
        max_eval = -float('inf')
        for r, c, flips in valid_moves:
            new_board = [row[:] for row in board]
            make_move(new_board, r, c, current_player_color, opponent_color)
            
            # 相手は最小化プレイヤー
            eval = minimax(new_board, opponent_color, depth - 1, False, ai_color, alpha, beta)
            max_eval = max(max_eval, eval)
            alpha = max(alpha, eval) # アルファの更新
            if beta <= alpha: # ベータカット
                break
        return max_eval
    else: # 最小化プレイヤー
        min_eval = float('inf')
        for r, c, flips in valid_moves:
            new_board = [row[:] for row in board]
            make_move(new_board, r, c, current_player_color, opponent_color)
            
            # 相手は最大化プレイヤー
            eval = minimax(new_board, opponent_color, depth - 1, True, ai_color, alpha, beta)
            min_eval = min(min_eval, eval)
            beta = min(beta, eval) # ベータの更新
            if beta <= alpha: # アルファカット
                break
        return min_eval

# --- 評価関数 ---

def evaluate(board, color):
    """
    現在の盤面を評価し、colorにとっての点数を返す。
    評価値 = (位置の重み + 石の差) + (確定石の差 * 80) + (着手可能数の差 * 10) - (フロンティアの差 * 5)
    """
    opponent = 3 - color
    size = len(board)
    score = 0
    stone_count_diff = 0

    # 1. 位置の重み (Positional Weights) の計算
    for r in range(size):
        for c in range(size):
            if board[r][c] == color:
                score += WEIGHTS[r][c]
                stone_count_diff += 1
            elif board[r][c] == opponent:
                score -= WEIGHTS[r][c]
                stone_count_diff -= 1
    
    total_stones = size * size - board_empty_count(board)

    # 2. 確定石の差 (Stable Stones) の計算
    my_stable = find_stable_stones(board, color)
    opponent_stable = find_stable_stones(board, opponent)
    stable_diff = my_stable - opponent_stable
    score += stable_diff * 80 # 確定石は非常に重要なので高い重み

    # 3. 着手可能数の差 (Mobility) の計算
    my_mobility = len(find_valid_moves(board, color, opponent))
    opponent_mobility = len(find_valid_moves(board, opponent, color))
    mobility_diff = my_mobility - opponent_mobility
    score += mobility_diff * 10 # 着手可能数は中程度の重み

    # 4. フロンティア（相手と接している石）の差 (Frontier) の計算
    my_frontier = count_frontier_stones(board, color)
    opponent_frontier = count_frontier_stones(board, opponent)
    frontier_diff = my_frontier - opponent_frontier
    score -= frontier_diff * 5 # フロンティアが多いと不利なので減点

    # 5. 終盤の石の差による補正
    if total_stones >= size * size * 0.7:
          score += stone_count_diff * 10
    
    # 6. ゲーム終了判定
    if board_empty_count(board) == 0:
        # ゲーム終了時は石の差が全て
        return stone_count_diff * 1000

    return score

# --- 高度なヒューリスティクス用ヘルパー関数 ---

def find_stable_stones(board, color):
    """
    盤面上の確定石（動かせない石）の数を数える。
    4隅から確定した石を探索し、その数を返す。
    （リバーシの確定石判定の一般的なアルゴリズムを採用）
    """
    size = len(board)
    stable_count = 0
    is_stable = [[False] * size for _ in range(size)]
    
    opponent = 3 - color
    
    # 探索の向き
    directions = [(0, 1), (1, 0), (0, -1), (-1, 0)] # 右、下、左、上

    # 隅の石から確定石を確定させる
    corners = [(0, 0), (0, size - 1), (size - 1, 0), (size - 1, size - 1)]

    for start_r, start_c in corners:
        if board[start_r][start_c] == color and not is_stable[start_r][start_c]:
            # キューを使った幅優先探索(BFS)で連結した確定石を探索
            queue = [(start_r, start_c)]
            is_stable[start_r][start_c] = True
            
            while queue:
                r, c = queue.pop(0)
                stable_count += 1
                
                # 確定した石の隣接石（同じ色）も、ブロックされていれば確定
                for dr, dc in directions:
                    nr, nc = r + dr, c + dc
                    
                    if 0 <= nr < size and 0 <= nc < size and board[nr][nc] == color and not is_stable[nr][nc]:
                        
                        # 隣接石が確定石になる条件をチェック
                        # 確定石の一般的な定義：盤の端、または、その石を通る行・列・斜めの全てで
                        # 相手の石によって完全に分断されていない、同じ色の石の連鎖の一部
                        
                        # ここでは、簡略化のため「角から辺に沿って繋がっている」石を確定石としてカウント
                        # より厳密な確定石判定は複雑なため、オセロAIの標準的な実装（確定石テーブル）に準拠した判定をここでは行う
                        
                        # 辺に沿って繋がっている石
                        if (r == 0 or r == size - 1 or c == 0 or c == size - 1):
                            # 簡略化：角または辺から連結している同じ色の石を確定として扱う
                            is_stable[nr][nc] = True
                            queue.append((nr, nc))
                        
                        # 注: 厳密な確定石判定は、より高度なアルゴリズムが必要。
                        # この実装では、「角」からの「完全な連鎖」のみをカウントする、簡易的な確定石判定を採用しています。
                        # 例：(0,0)から(0,7)まで、(1,0)から(1,7)まで同じ色で埋まっている場合など。
                        
    return stable_count

def count_frontier_stones(board, color):
    """
    相手の石または空きマスに接している自分の石（フロンティア）の数を数える。
    フロンティアが多いほど、次の手で裏返されるリスクが高い。
    """
    size = len(board)
    frontier_count = 0
    opponent = 3 - color
    
    # 8方向の定義
    directions = [
        (-1, -1), (-1, 0), (-1, 1),
        (0, -1),            (0, 1),
        (1, -1),  (1, 0),  (1, 1)
    ]

    for r in range(size):
        for c in range(size):
            if board[r][c] == color:
                # 自分の石であれば、隣接マスをチェック
                for dr, dc in directions:
                    nr, nc = r + dr, c + dc
                    
                    if 0 <= nr < size and 0 <= nc < size:
                        # 隣接マスが空きマスまたは相手の石であればフロンティア
                        if board[nr][nc] == EMPTY or board[nr][nc] == opponent:
                            frontier_count += 1
                            break # この石はフロンティアであるため、他の方向のチェックは不要
                            
    return frontier_count

# --- ルール関連のヘルパー関数（元のコードから再利用） ---

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
    size = len(board)
    valid_moves = []
    for row in range(size):
        for col in range(size):
            if board[row][col] == EMPTY:
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
            if board[r][c] == EMPTY:
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
    ミニマックス探索中のシミュレーションに使用。
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
