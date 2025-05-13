def is_valid(board, row, col, num):
    return board.is_valid(row, col, num)

def solve(board):
    for row in range(9):
        for col in range(9):
            if board.grid[row][col] == 0:
                for num in range(1, 10):
                    if is_valid(board, row, col, num):
                        board.grid[row][col] = num
                        if solve(board):
                            return True
                        board.grid[row][col] = 0
                return False
    return True
