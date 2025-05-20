from utils.heuristics import get_column_with_least_nodes

# Base node class for the DLX structure
class DLXNode:
    def __init__(self, row=-1, col=-1):
        # Four way doubly linked pointers
        self.L = self.R = self.U = self.D = self
        self.C = self
        self.row = row
        self.col = col

# Special node for the column header which extends DLXNode
class ColumnNode(DLXNode):
    def __init__(self, name):
        super().__init__()
        # Number of nodes in the column
        self.size = 0
        # Column index
        self.name = name

# Main DLX class for handling exact cover matrix
class DancingLinks:
    def __init__(self, matrix):
        # Root of the header list
        self.root = ColumnNode("root")
        # List of column headers
        self.columns = []
        # Stores the row indices of the selected solution
        self.solution = []

        # Total number of constraints
        n_cols = len(matrix[0])
        
        # Create and link all column header nodes horizontally
        for i in range(n_cols):
            col = ColumnNode(i)
            self.columns.append(col)
            col.R = self.root
            col.L = self.root.L
            self.root.L.R = col
            self.root.L = col
            col.U = col.D = col

        # Add nodes to the matrix based on the 1s in the input matrix
        for r, row in enumerate(matrix):
            prev = None
            for c, val in enumerate(row):
                if val:
                    col = self.columns[c]
                    node = DLXNode(r, c)
                    node.C = col
                    col.size += 1
                    
                    # Insert node into column vertically
                    node.D = col
                    node.U = col.U
                    col.U.D = node
                    col.U = node

                    # Link node horizontally with previous in the same row 
                    if prev:
                        node.L = prev
                        node.R = prev.R
                        prev.R.L = node
                        prev.R = node
                    else:
                        node.L = node.R = node
                    prev = node

    # Remove a column and its related rows from the matrix
    def cover(self, col):
        col.R.L = col.L
        col.L.R = col.R
        for row in self.iter_down(col):
            for node in self.iter_right(row):
                node.D.U = node.U
                node.U.D = node.D
                node.C.size -= 1

    # Reinsert a previously covered column and its rows
    def uncover(self, col):
        for row in self.iter_up(col):
            for node in self.iter_left(row):
                node.C.size += 1
                node.D.U = node
                node.U.D = node
        col.R.L = col
        col.L.R = col


    # Recursive search for a valid exact cover solution
    def search(self):
        # Success if all columns are covered 
        if self.root.R == self.root:
            return True

        # Choosing the column with the fewest nodes for minimum branching
        col = get_column_with_least_nodes(self.root)
        if not col:
            return False
        
        self.cover(col)
        
        for row in self.iter_down(col):
            self.solution.append(row.row)
            for node in self.iter_right(row):
                self.cover(node.C)

            # If a complete solution is found 
            if self.search():
                return True

            for node in self.iter_left(row):
                self.uncover(node.C)
            self.solution.pop()
            
        self.uncover(col)
        return False

    # Horizontal and vertical iterators to traverse the matrix
    def iter_right(self, node):
        n = node.R
        while n != node:
            yield n
            n = n.R

    def iter_left(self, node):
        n = node.L
        while n != node:
            yield n
            n = n.L

    def iter_down(self, node):
        n = node.D
        while n != node:
            yield n
            n = n.D

    def iter_up(self, node):
        n = node.U
        while n != node:
            yield n
            n = n.U

# Converts the sudoku board into an exact cover matrix 
def sudoku_to_exact_cover(grid):
    def encode(r, c, d):
        # Encodes the constraints into 4 groups
        return [
            # Cell constraint
            81 * 0 + r * 9 + c,
            # Row digit constraint       
            81 * 1 + r * 9 + d - 1,
            # Column digit constraint  
            81 * 2 + c * 9 + d - 1,
            # Block constraint   
            81 * 3 + ((r//3)*3 + c//3)*9 + d - 1  
        ]

    cover_matrix = []
    # Map of matrix row index 
    row_lookup = {} 

    for r in range(9):
        for c in range(9):
            if grid[r][c] == 0:
                digits = range(1, 10)
            else:
                digits = [grid[r][c]]
            for d in digits:
                # Each row has 324 constraints
                row = [0] * 324
                for idx in encode(r, c, d):
                    row[idx] = 1
                cover_matrix.append(row)
                row_lookup[len(cover_matrix)-1] = (r, c, d)
                
    return cover_matrix, row_lookup

# Main solving function that links everything together
def solve(board):
    # Generate exact cover matrix
    matrix, row_map = sudoku_to_exact_cover(board.grid)
    # Initialise the DLX solver
    dlx = DancingLinks(matrix)
    
    # Attempt to find a solution
    if dlx.search():
        for idx in dlx.solution:
            r, c, d = row_map[idx]
            # Fill the solutions onto the board
            board.grid[r][c] = d
        return True
    return False