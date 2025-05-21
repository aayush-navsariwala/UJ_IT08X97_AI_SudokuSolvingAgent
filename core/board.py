class SudokuBoard:
    def __init__(self, grid=None):
        # Initialise the sudoku board
        # If no grid is given, create a 9x9 grid filled with empty cells
        self.grid = grid if grid else [[0 for _ in range(9)] for _ in range(9)]

    # Check if placing a number at (row, col) is valid according to the game rules
    def is_valid(self, row, col, num):
        
        # Checks to see if the number is already in the same row 
        if num in self.grid[row]:
            return False
        
        # Checks to see if the number is already in the same column
        for i in range(9):
            if self.grid[i][col] == num:
                return False
            
        # Checks to see if the number is already in the same 3x3 box
        start_row, start_col = 3 * (row // 3), 3 * (col // 3)
        for i in range(start_row, start_row + 3):
            for j in range(start_col, start_col + 3):
                if self.grid[i][j] == num:
                    return False
        # If all checks are passed, the number placement is valid
        return True
    
    # Checks if the board is completely filled
    def is_complete(self):
        return all(all(cell !=0 for cell in row) for row in self.grid)

    # Prints the current state of the board to the terminal
    def display(self):
        for row in self.grid:
            print(row)
