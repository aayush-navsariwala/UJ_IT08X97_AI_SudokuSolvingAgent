from core.fsm import State

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