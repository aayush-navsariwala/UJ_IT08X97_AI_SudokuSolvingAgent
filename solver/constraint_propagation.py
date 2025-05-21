from utils.heuristics import find_mrv_cell
from core.board import SudokuBoard

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
def constraint_propagation(board):
    progress = True
    
    # Keeps applying constraint propagation until no further progress is made
    while progress:
        progress = False
        # Using MRV to pick the cell
        cell = find_mrv_cell(board.grid)
        if cell:
            row, col = cell
            options = get_possible_values(board, row, col)
            if len(options) == 1:
                board.grid[row][col] = options[0]
                progress = True
        else:
            # If no empty cells are left or no progress
            break
    return board
        
def solve(board):
    print("🧠 Running Constraint Propagation solve()")
    # Apply constraint propagation
    constraint_propagation(board)
    
    # After propagation, check if fully solved                        
    for row in board.grid:
        if 0 in row:
            break
    else:
        return True
    
    # Pick the next cell using MRV
    cell = find_mrv_cell(board.grid)
    if not cell:
        print("❌ No more solvable cells found — invalid board?")
        return False
    
    row, col = cell
    values = get_possible_values(board, row, col)
    
    if not values:
        print(f"❌ No valid values for cell ({row}, {col}) — dead end")
        return False
    
    for val in values:
        board.grid[row][col] = val
        board_copy = SudokuBoard([r.copy() for r in board.grid])
        if solve(board_copy):
            board.grid = [r.copy() for r in board_copy.grid]
            return True
        board.grid[row][col] = 0
        
    print(f"❌ Backtracking failed at ({row}, {col}) — no options worked")
    return False