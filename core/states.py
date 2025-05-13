from core.fsm import State
from solver.backtracking import solve

class InputState(State):
    def enter(self):
        print("Entered Input State")

    def execute(self):
        print("Awaiting player input...")

    def exit(self):
        print("Exiting Input State")

        
class ValidationState(State):
    def __init__(self, board, fsm):
        self.board = board
        self.fsm = fsm

    def enter(self):
        print("Entered Validation State")

    def execute(self):
        if self.is_valid_board():
            print("✅ Puzzle is valid.")
            # Later: Transition to solving state
        else:
            print("❌ Puzzle is invalid. Please check your input.")
            # Later: Transition back to InputState

    def exit(self):
        print("Exiting Validation State")

    def is_valid_board(self):
        for row in range(9):
            for col in range(9):
                num = self.board.grid[row][col]
                if num != 0:
                    # Temporarily clear cell to validate properly
                    self.board.grid[row][col] = 0
                    if not self.board.is_valid(row, col, num):
                        self.board.grid[row][col] = num  # Restore
                        return False
                    self.board.grid[row][col] = num  # Restore
        return True
    
class SolvingState(State):
    def __init__(self, board, fsm, algorithm="backtracking"):
        self.board = board
        self.fsm = fsm
        self.algorithm = algorithm

    def enter(self):
        print(f"Entered Solving State using {self.algorithm} algorithm...")

    def execute(self):
        if self.algorithm == "backtracking":
            success = solve(self.board)
        else:
            print("❌ Algorithm not supported yet.")
            success = False

        if success:
            print("✅ Sudoku puzzle solved successfully!")
            self.board.display()
        else:
            print("❌ Failed to solve the puzzle.")

    def exit(self):
        print("Exiting Solving State.")