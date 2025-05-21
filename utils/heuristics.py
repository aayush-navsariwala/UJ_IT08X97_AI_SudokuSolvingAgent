def get_valid_numbers(grid, row, col):
    used = set(grid[row])
    used.update(grid[i][col] for i in range(9))
    box_r, box_c = 3 * (row // 3), 3 * (col // 3)
    for r in range(box_r, box_r + 3):
        for c in range(box_c, box_c + 3):
            used.add(grid[r][c])
    return [n for n in range(1, 10) if n not in used]


def find_mrv_cell(grid):
    min_options = 10 
    best_cell = None
    for row in range(9):
        for col in range(9):
            if grid[row][col] == 0:
                options = get_valid_numbers(grid, row, col)
                if len(options) < min_options:
                    min_options = len(options)
                    best_cell = (row, col)
    return best_cell


def least_constraining_values(grid, row, col):
    options = get_valid_numbers(grid, row, col)
    impact = {}
    for val in options:
        grid[row][col] = val
        count = sum(len(get_valid_numbers(grid, r, c))
                    for r in range(9) for c in range(9)
                    if grid[r][c] == 0)
        impact[val] = count
        grid[row][col] = 0
    return sorted(options, key=lambda x: impact[x])


def get_column_density(matrix):
    return min(range(len(matrix[0])), key=lambda col: sum(row[col] for row in matrix))


def get_column_with_least_nodes(root):
    # Returns the column with the fewest nodes from header list used in DLX 
    best = None
    min_size = float('inf')
    node = root.R
    while node != root:
        if node.size < min_size:
            best = node
            min_size = node.size
            node = node.R
        return best
    