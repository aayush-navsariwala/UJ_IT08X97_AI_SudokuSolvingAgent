# Check if placing num at row and col is valid based on sudoku rules
def is_valid(board, row, col, num):
    return board.is_valid(row, col, num)

# Recursive backtracking function to solve the board
def solve(board):
    # Iterate through each cell of the 9x9 grid
    for row in range(9):
        for col in range(9):
            # Look for an empty cell which is represented as 0
            if board.grid[row][col] == 0:
                # Try number from 1 to 9
                for num in range(1, 10):
                    if is_valid(board, row, col, num):
                        # Place the number temporarily
                        board.grid[row][col] = num
                        # Recursively attempt to solve the rest of the board
                        if solve(board):
                            return True
                        # If it is not solvable, backtrack by resetting that cell
                        board.grid[row][col] = 0
                # If no number fits, return false to trigger the backtracking
                return False
    # If all cells are filled correctly, return true as solved     
    return True
