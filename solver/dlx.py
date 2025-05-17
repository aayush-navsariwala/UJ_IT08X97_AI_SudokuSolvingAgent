class DLXNode:
    def __init__(self, row=-1, col=-1):
        self.L = self.R = self.U = self.D = self
        self.C = self
        self.row = row
        self.col = col
        
class ColumnNode(DLXNode):
    def __init__(self, name):
        super().__init__()
        self.size = 0
        self.name = name

class DancingLinks:
    def __init__(self, matrix):
        self.root = ColumnNode("root")
        self.columns = []
        self.solution = []

        # Create column headers
        n_cols = len(matrix[0])
        for i in range(n_cols):
            col = ColumnNode(i)
            self.columns.append(col)
            col.R = self.root
            col.L = self.root.L
            self.root.L.R = col
            self.root.L = col
            col.U = col.D = col

        # Add matrix rows
        for r, row in enumerate(matrix):
            prev = None
            for c, val in enumerate(row):
                if val:
                    col = self.columns[c]
                    node = DLXNode(r, c)
                    node.C = col
                    col.size += 1

                    # Vertical links
                    node.D = col
                    node.U = col.U
                    col.U.D = node
                    col.U = node

                    if prev:
                        # Horizontal links
                        node.L = prev
                        node.R = prev.R
                        prev.R.L = node
                        prev.R = node
                    else:
                        node.L = node.R = node
                    prev = node

    def cover(self, col):
        col.R.L = col.L
        col.L.R = col.R
        for row in self.iter_down(col):
            for node in self.iter_right(row):
                node.D.U = node.U
                node.U.D = node.D
                node.C.size -= 1

    def uncover(self, col):
        for row in self.iter_up(col):
            for node in self.iter_left(row):
                node.C.size += 1
                node.D.U = node
                node.U.D = node
        col.R.L = col
        col.L.R = col

    def search(self):
        if self.root.R == self.root:
            return True

        col = min(self.iter_right(self.root), key=lambda c: c.size)
        self.cover(col)
        for row in self.iter_down(col):
            self.solution.append(row.row)
            for node in self.iter_right(row):
                self.cover(node.C)

            if self.search():
                return True

            for node in self.iter_left(row):
                self.uncover(node.C)
            self.solution.pop()
        self.uncover(col)
        return False

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
            
            
            
def sudoku_to_exact_cover(grid):
    def encode(r, c, d):
        return [
            81 * 0 + r * 9 + c,       # Cell constraint
            81 * 1 + r * 9 + d - 1,   # Row constraint
            81 * 2 + c * 9 + d - 1,   # Column constraint
            81 * 3 + ((r//3)*3 + c//3)*9 + d - 1  # Box constraint
        ]

    cover_matrix = []
    row_lookup = {}  # to convert back from row index to (r, c, d)

    for r in range(9):
        for c in range(9):
            if grid[r][c] == 0:
                digits = range(1, 10)
            else:
                digits = [grid[r][c]]
            for d in digits:
                row = [0] * 324
                for idx in encode(r, c, d):
                    row[idx] = 1
                cover_matrix.append(row)
                row_lookup[len(cover_matrix)-1] = (r, c, d)
    return cover_matrix, row_lookup

def solve(board):
    matrix, row_map = sudoku_to_exact_cover(board.grid)
    dlx = DancingLinks(matrix)
    if dlx.search():
        # Apply solution
        for idx in dlx.solution:
            r, c, d = row_map[idx]
            board.grid[r][c] = d
        return True
    return False
