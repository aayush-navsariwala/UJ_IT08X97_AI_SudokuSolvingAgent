from utils.heuristics import find_mrv_cell, least_constraining_values

# Check if placing num at row and col is valid based on sudoku rules
def is_valid(board, row, col, num):
    return board.is_valid(row, col, num)

# Recursive backtracking function with MRV and LCV heuristics
def solve(board):
    # Using MRV to find the most constrained cell
    mrv_cell = find_mrv_cell(board.grid)
    if not mrv_cell:
        return True
    
    row, col = mrv_cell
    
    # Using LCV to prioritise the values that constrain the least
    for num in least_constraining_values(board.grid, row, col):
        if is_valid(board, row, col, num):
            board.grid[row][col] = num
            if solve(board):
                return True
            # Backtrack
            board.grid[row][col] = 0 
    # Trigger backtracking    
    return False