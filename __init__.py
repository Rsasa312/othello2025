# Generation ID: Hutch_1763365873709_9229idond (前半)

def myai(board, color):
    """
    オセロの最適な手を返す関数
    """
    def is_valid_move(board, row, col, color):
        if board[row][col] != 0:
            return False
        
        opponent = 3 - color
        directions = [(-1, -1), (-1, 0), (-1, 1), (0, -1), (0, 1), (1, -1), (1, 0), (1, 1)]
        
        for dr, dc in directions:
            r, c = row + dr, col + dc
            found_opponent = False
            
            while 0 <= r < len(board) and 0 <= c < len(board[0]):
                if board[r][c] == opponent:
                    found_opponent = True
                elif board[r][c] == color:
                    if found_opponent:
                        return True
                else:
                    break
                r += dr
                c += dc
        
        return False
    
    def get_valid_moves(board, color):
        moves = []
        for i in range(len(board)):
            for j in range(len(board[0])):
                if is_valid_move(board, i, j, color):
                    moves.append((i, j))
        return moves
    
    def count_pieces(board, color):
        return sum(row.count(color) for row in board)
    
    def evaluate_position(board, color, row, col):
        corners = [(0, 0), (0, len(board[0]) - 1), (len(board) - 1, 0), (len(board) - 1, len(board[0]) - 1)]
        edges = [(0, j) for j in range(len(board[0]))] + \
                [(len(board) - 1, j) for j in range(len(board[0]))] + \
                [(i, 0) for i in range(len(board))] + \
                [(i, len(board[0]) - 1) for i in range(len(board))]
        
        if (row, col) in corners:
            return 100
        elif (row, col) in edges:
            return 10
        else:
            return 1
    
    valid_moves = get_valid_moves(board, color)
    
    if not valid_moves:
        return None
    
    best_move = max(valid_moves, key=lambda move: evaluate_position(board, color, move[0], move[1]))
    
    return best_move

# Generation ID: Hutch_1763365873709_9229idond (後半)
