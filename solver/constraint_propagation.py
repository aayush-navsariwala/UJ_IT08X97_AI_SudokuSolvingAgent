# Returns a list of valid numbers that can be placed at the given cell without violating the sudoku rules 
def get_possible_values(board, row, col):
    # Skips if the cell is already filled 
    if board.grid[row][col] != 0:
        return []

    # Start with all digits from 1 to 9
    possible = set(range(1, 10))

    # Eliminate numbers already present in the same row
    possible -= set(board.grid[row])

    # Eliminate numbers already present in the same column
    possible -= {board.grid[r][col] for r in range(9)}

    # Eliminate numbers in the same 3x3 subgrid
    box_row, box_col = 3 * (row // 3), 3 * (col // 3)
    for r in range(box_row, box_row + 3):
        for c in range(box_col, box_col + 3):
            possible.discard(board.grid[r][c])

    return list(possible)

# Solves the sudoku board using pure constraint propagation
def solve(board):
    progress = True
    
    # Keeps applying constraint propagation until no further progress is made
    while progress:
        progress = False
        for row in range(9):
            for col in range(9):
                if board.grid[row][col] == 0:
                    options = get_possible_values(board, row, col)
                    if len(options) == 1:
                        # Fill in the determined value
                        board.grid[row][col] = options[0]
                        # When a cell is filled, keep propagating
                        progress = True
                        
    # After all deterministic cells are filled, check if the board is complete
    for row in range(9):
        for col in range(9):
            # If there are still places with 0, the board is not solved
            if board.grid[row][col] == 0:
                return False
    
    # The board was solved without guessing 
    return True