import sys

# 探索深度に合わせて再帰の上限を設定
sys.setrecursionlimit(2000)

# --- 定数 ---
# 評価関数用の重みテーブル (元のものを維持)
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

# --- AIのエントリポイント ---
def myai(board, color):
    """
    オセロAIのエントリポイント。3手先を読んで最善の手を返す（sakura互換）
    """
    opponent = 3 - color
    # 探索の深さを3に設定（初期設定を維持）
    SEARCH_DEPTH = 3 

    valid_moves = find_valid_moves(board, color, opponent)
    
    if not valid_moves:
        return None

    best_move = None
    best_eval = -float('inf')

    # 初手での反転数が最も多い手を採用するロジックを削除し、純粋なミニマックス評価を採用
    for r, c, _ in valid_moves:
        new_board = [row[:] for row in board]
        make_move(new_board, r, c, color, opponent)
        
        # 相手番からミニマックスを開始 (is_maximizing_player = False)
        current_eval = minimax(new_board, opponent, SEARCH_DEPTH - 1, False, color)
        
        if current_eval > best_eval:
            best_eval = current_eval
            best_move = (r, c)
        
        # 同一評価の場合、元の実装では特に処理なし
        elif current_eval == best_eval:
             # 例えば、石数が多くなる手など、追加のタイブレークを実装することも可能
             pass 

    return best_move

# --- ミニマックス探索 ---
def minimax(board, current_player_color, depth, is_maximizing_player, ai_color):
    """
    ミニマックス探索を行い、現在の局面の最善の評価値を返す。
    α-β枝刈りは実装せず、元のシンプルなミニマックスを維持する。
    """
    opponent_color = 3 - current_player_color

    # 1. 探索深さが0に到達 (評価関数を呼び出す)
    if depth == 0:
        return evaluate(board, ai_color)
    
    valid_moves = find_valid_moves(board, current_player_color, opponent_color)

    # 2. 終局判定 / パス処理
    if not valid_moves:
        opponent_moves = find_valid_moves(board, opponent_color, current_player_color)
        
        if not opponent_moves:
            # 終局 (両者打てる手なし) -> 評価値を極端に高く/低くする
            return evaluate(board, ai_color) * 1000000 
        
        # パス (相手の手番へ移行、深さは減らさない)
        return minimax(board, opponent_color, depth, not is_maximizing_player, ai_color)
            
    # 3. 最大化フェーズ (AIにとって有利な手を探す)
    if is_maximizing_player:
        max_eval = -float('inf')
        for r, c, _ in valid_moves:
            new_board = [row[:] for row in board]
            make_move(new_board, r, c, current_player_color, opponent_color)
            
            # 相手番として探索を続ける
            eval = minimax(new_board, opponent_color, depth - 1, False, ai_color)
            max_eval = max(max_eval, eval)
        return max_eval
    
    # 4. 最小化フェーズ (相手にとって有利な手（AIにとって不利な手）を探す)
    else:
        min_eval = float('inf')
        for r, c, _ in valid_moves:
            new_board = [row[:] for row in board]
            make_move(new_board, r, c, current_player_color, opponent_color)
            
            # 自分の番として探索を続ける
            eval = minimax(new_board, opponent_color, depth - 1, True, ai_color)
            min_eval = min(min_eval, eval)
        return min_eval

# --- 強化された評価関数 ---
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

    # 終局判定とスコア確定
    if empty_count == 0 or (
        not find_valid_moves(board, color, opponent) and 
        not find_valid_moves(board, opponent, color)
    ):
        stone_count_diff = sum(row.count(color) for row in board) - sum(row.count(opponent) for row in board)
        # 終局時の点差は非常に重要 (ミニマックスで終局に至った場合の最終的な勝敗を決定づける)
        return stone_count_diff * 1000000 

    # --- 1. 位置の重みと石数の計算 ---
    stone_count_diff = 0
    frontier_count = 0 # 相手と接している自分の石の数 (少ない方が良い)
    
    for r in range(SIZE):
        for c in range(SIZE):
            if board[r][c] == color:
                score += WEIGHTS[r][c] # 位置の重み
                stone_count_diff += 1
                if is_frontier(board, r, c, opponent):
                    frontier_count += 1
            elif board[r][c] == opponent:
                score -= WEIGHTS[r][c] # 位置の重み
                stone_count_diff -= 1
    
    # --- 2. 確定石の評価 ---
    # 確定石は、もうひっくり返されることがない石。絶対的な優位性を持つ。
    # 確定石の計算は複雑なため、ここでは簡略化して「角の確保」を特に重視する。
    # より高度な確定石の計算は、外部ヘルパー関数を使用する。
    my_stable_count, opp_stable_count = count_stable_stones(board, color, opponent)
    score += (my_stable_count - opp_stable_count) * 80  # 確定石1個あたり80点の重み

    # --- 3. モビリティ（着手可能数の差）の評価 ---
    # 着手可能数が多いほど、盤面の主導権を握りやすい
    my_moves = len(find_valid_moves(board, color, opponent))
    opp_moves = len(find_valid_moves(board, opponent, color))
    
    # 序盤～中盤ではモビリティを非常に重視 (40倍)
    mobility_score = (my_moves - opp_moves) * 40
    score += mobility_score

    # --- 4. フロンティア（相手と接する石）の評価 ---
    # 相手と接する石が少ないほど、相手に着手の機会を与えにくい（安定性が高い）
    # フロンティアは少ない方が有利なので、マイナスで評価に加える
    score -= frontier_count * 10 

    # --- 5. 石数の差（終盤重視）の評価 ---
    # 中盤（石数20個～40個程度）まではモビリティを重視し、終盤に近づくにつれて石数を重視する。
    if total_stones >= SIZE * SIZE * 0.7: # 石数45個以上で終盤と見なす
        score += stone_count_diff * 15 # 終盤は石数差の重みを上げる
    elif total_stones < SIZE * SIZE * 0.3: # 序盤は石数差をあまり重視しない
        score += stone_count_diff * 5
    else: # 中盤
        score += stone_count_diff * 10

    return score

# --- ヘルパー関数群 ---

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
            else: # board[r][c] == color (自分の石で挟んだ)
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

# --- 強化評価用の補助関数 ---

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
        if is_in_board(nr, nc) and board[nr][nc] == 0: # 空きマスと接している
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
    
    # 8x8盤の4隅の座標
    corners = [(0, 0), (0, 7), (7, 0), (7, 7)]
    
    # 各角から確定石を探索
    for start_r, start_c in corners:
        if board[start_r][start_c] != 0:
            target_color = board[start_r][start_c]
            
            # 確定石の探索 (幅優先探索/再帰的な隣接判定が一般的だが、ここでは簡略化)
            
            # (1) 角の石は確定
            if not visited[start_r][start_c]:
                stable_counts[target_color] += 1
                visited[start_r][start_c] = True
            
            # (2) 辺に沿って、角から切れ目なく並んでいる石を確定と見なす (簡略版)
            # 水平方向
            dr, dc = (0, 1) if start_c == 0 else (0, -1)
            r, c = start_r, start_c + dc
            while is_in_board(r, c) and board[r][c] == target_color:
                if not visited[r][c]:
                    # 厳密には、この石が盤面の上下方向に完全に囲まれているかを確認する必要があるが、
                    # 暫定的に「辺に沿って角から繋がっている」ものを確定石と見なす
                    is_surrounded = True 
                    if start_r == 0 or start_r == 7: # 上辺または下辺
                         # 縦方向 (反対側) に空きがないことを確認 (より厳密な判定)
                         pass
                    
                    if is_surrounded: # 実際の確定石判定ロジックはより複雑
                        stable_counts[target_color] += 1
                        visited[r][c] = True
                r += dr
                c += dc
            
            # 垂直方向
            dr, dc = (1, 0) if start_r == 0 else (-1, 0)
            r, c = start_r + dr, start_c
            while is_in_board(r, c) and board[r][c] == target_color:
                if not visited[r][c]:
                    is_surrounded = True
                    if is_surrounded: # 実際の確定石判定ロジックはより複雑
                        stable_counts[target_color] += 1
                        visited[r][c] = True
                r += dr
                c += dc

    # 確定石は、どのプレーヤーにとっても絶対的な価値を持つため、
    # 相手の確定石が多い場合は大きく評価を下げます。
    return stable_counts[color], stable_counts[opponent]

# --------------------------
# メインのmyai関数はそのまま利用可能です。
# --------------------------
