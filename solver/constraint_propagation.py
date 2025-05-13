def get_possible_values(board, row, col):
    if board.grid[row][col] != 0:
        return []

    possible = set(range(1, 10))

    # Eliminate based on row
    possible -= set(board.grid[row])

    # Eliminate based on column
    possible -= {board.grid[r][col] for r in range(9)}

    # Eliminate based on 3x3 box
    box_row, box_col = 3 * (row // 3), 3 * (col // 3)
    for r in range(box_row, box_row + 3):
        for c in range(box_col, box_col + 3):
            possible.discard(board.grid[r][c])

    return list(possible)


def find_next_cell(board):
    min_options = 10
    best_cell = None
    for row in range(9):
        for col in range(9):
            if board.grid[row][col] == 0:
                options = get_possible_values(board, row, col)
                if len(options) < min_options:
                    min_options = len(options)
                    best_cell = (row, col, options)
                    if min_options == 1:
                        return best_cell
    return best_cell


def solve(board):
    # Apply constraint propagation with recursive logic
    cell = find_next_cell(board)
    if not cell:
        return True  # Solved

    row, col, options = cell
    for num in options:
        board.grid[row][col] = num
        if solve(board):
            return True
        board.grid[row][col] = 0  # backtrack
    return False