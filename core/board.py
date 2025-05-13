class SudokuBoard:
    def __init__(self, grid=None):
        self.grid = grid if grid else [[0 for _ in range(9)] for _ in range(9)]

    def is_valid(self, row, col, num):
        # Row check
        if num in self.grid[row]:
            return False
        
        # Column check
        for i in range(9):
            if self.grid[i][col] == num:
                return False
            
        # 3x3 Box check
        start_row, start_col = 3 * (row // 3), 3 * (col // 3)
        for i in range(start_row, start_row + 3):
            for j in range(start_col, start_col + 3):
                if self.grid[i][j] == num:
                    return False
        return True
    
    def is_complete(self):
        return all(all(cell !=0 for cell in row) for row in self.grid)

    def display(self):
        for row in self.grid:
            print(row)
