def myai(board, color):
    """
    戦略的優先順位に基づいて着手位置を返す
    """
    size = len(board)
    opponent = 3 - color
    valid_moves = []

    # 全ての打てる場所とその反転数をリスト化
    for row in range(size):
        for col in range(size):
            if board[row][col] == 0:
                flips = count_flips(board, row, col, color, opponent)
                if flips > 0:
                    valid_moves.append({'pos': (col, row), 'flips': flips})

    if not valid_moves:
        return None

    corners = [(0, 0), (0, size-1), (size-1, 0), (size-1, size-1)]
    
    # 角の隣接マス（C打ち・X打ち）の定義
    # 各角に対して、その隣接する座標をマッピング
    adj_to_corners = {
        (0, 0): [(0, 1), (1, 0), (1, 1)],
        (0, size-1): [(0, size-2), (1, size-1), (1, size-2)],
        (size-1, 0): [(size-2, 0), (size-1, 1), (size-2, 1)],
        (size-1, size-1): [(size-2, size-1), (size-1, size-2), (size-2, size-2)]
    }

    # 1. 角が取れるかチェック
    corner_moves = [m for m in valid_moves if m['pos'] in corners]
    if corner_moves:
        # 最も多く取れる角を返す
        corner_moves.sort(key=lambda x: x['flips'], reverse=True)
        return corner_moves[0]['pos']

    # 2. すでに自分が取っている角の隣をチェック
    my_corner_adj_moves = []
    for c_pos, adj_list in adj_to_corners.items():
        # もしその角が自分の色なら、その隣接マスは「安全」かつ「戦略的」
        if board[c_pos[1]][c_pos[0]] == color:
            for m in valid_moves:
                if m['pos'] in adj_list:
                    my_corner_adj_moves.append(m)
    
    if my_corner_adj_moves:
        my_corner_adj_moves.sort(key=lambda x: x['flips'], reverse=True)
        return my_corner_adj_moves[0]['pos']

    # 3. 角が空いている場合、その隣（危険地帯）を除外したリストを作成
    safe_moves = []
    danger_zones = []
    for c_pos, adj_list in adj_to_corners.items():
        if board[c_pos[1]][c_pos[0]] == 0:  # 角が空白
            danger_zones.extend(adj_list)
    
    safe_moves = [m for m in valid_moves if m['pos'] not in danger_zones]

    # 4. 最終決定
    if safe_moves:
        # 危険地帯以外の場所で、最も多く取れる場所
        safe_moves.sort(key=lambda x: x['flips'], reverse=True)
        return safe_moves[0]['pos']
    else:
        # どこも危険な場合（または角が全て埋まっている場合）は、全体から最大を選ぶ
        valid_moves.sort(key=lambda x: x['flips'], reverse=True)
        return valid_moves[0]['pos']
