from core.fsm import State
from solver.backtracking import solve
from solver.constraint_propagation import solve as constraint_solve
from solver.dlx import solve as dlx_solve
import time
import tkinter as tk


class InputState(State):
    # Logs the entry into the input state
    def enter(self):
        print("Entered Input State")

    # Placeholder message used for debugging errors in the state
    def execute(self):
        print("Awaiting player input...")

    # Logs exit from the input state
    def exit(self):
        print("Exiting Input State")


class ValidationState(State):
    def __init__(self, board, fsm):
        # Reference to the sudoku board
        self.board = board
        # Reference to the FSM manager
        self.fsm = fsm

    def enter(self):
        # Confirmation message for the validation state used for debugging errors
        print("Entered Validation State")

    def execute(self):
        # Check the puzzle validity and update the GUI status 
        valid = self.is_valid_board()
        # Checks to see if the GUI exists
        if hasattr(self.fsm, 'gui'):
            gui = self.fsm.gui
            if valid:
                gui.status_label.config(text="✅ Puzzle is valid", fg="green")
                gui.solve_button.config(state=tk.NORMAL)
            else:
                gui.status_label.config(text="❌ Puzzle is invalid", fg="red")
                gui.solve_button.config(state=tk.DISABLED)

    def exit(self):
        # Exiting validation state used for debugging errors
        print("Exiting Validation State")

    def is_valid_board(self):
        # Validates the whole grid by checking all filled values for conflicts
        for row in range(9):
            for col in range(9):
                num = self.board.grid[row][col]
                if num != 0:
                    # Temporarily clear cell to validate properly
                    self.board.grid[row][col] = 0
                    if not self.board.is_valid(row, col, num):
                        # Restore the grid
                        self.board.grid[row][col] = num  
                        return False
                    self.board.grid[row][col] = num  
        return True
    
    
class SolvingState(State):
    def __init__(self, board, fsm, algorithm="backtracking"):
        self.board = board
        self.fsm = fsm
        # Selected algorithm (backtracking, constraint propagation or DLX)
        self.algorithm = algorithm

    def enter(self):
        print(f"Entered Solving State using {self.algorithm} algorithm...")

    def execute(self):
        print(f"Solving with {self.algorithm}...")
                
        # Start timer for the selected algorithm
        start_time = time.time()
        
        # Dynamically import and run the selected solving algorithm
        if self.algorithm == "backtracking":
            from solver.backtracking import solve as backtrack_solve
            success = backtrack_solve(self.board)
        elif self.algorithm == "constraint_propagation":
            from solver.constraint_propagation import solve as constraint_solve
            success = constraint_solve(self.board)
        elif self.algorithm == "dlx":
            from solver.dlx import solve as dlx_solve
            success = dlx_solve(self.board)
        else:
            print("❌ Algorithm not supported.")
            success = False
        
        # End timer for the selected algorithm
        duration = time.time() - start_time
        print(f"🕒 Execution time: {duration:.5f} seconds")
        
        # Display the execution time of that algorithm in the GUI
        if hasattr(self.fsm, 'gui'):
            self.fsm.gui.timer_label.config(text=f"🕒 Execution time: {duration:.5f} seconds")

        # Transition to WinState if the puzzle is solved else report failure 
        if success:
            print("✅ Sudoku puzzle solved successfully!")
            self.board.display()
            
            from core.states import WinState
            self.fsm.set_state(WinState(self.board))  
            self.fsm.update()
            
        else:
            print("❌ Failed to solve the puzzle.")

    def exit(self):
        print("Exiting Solving State.")
    
        
class WinState(State):
    def __init__(self, board):
        self.board = board

    def enter(self):
        # State entered when the puzzle is solved 
        print("Entered Win State 🎉")

    def execute(self):
        # Checks to see if all cells are filled and valid on sudoku board
        if self.board.is_complete():
            print("🎯 Puzzle is fully and correctly solved!")
        else:
            print("⚠ Puzzle appears incomplete or incorrect.")
        self.board.display()

    def exit(self):
        print("Exiting Win State")
        

class ResetState(State):
    def __init__(self, board, fsm):
        self.board = board
        self.fsm = fsm

    def enter(self):
        # State entered when the board is reset
        print("Entered Reset State 🔄")

    def execute(self):
        # Clear the board by resetting all values to 0
        self.board.grid = [[0 for _ in range(9)] for _ in range(9)]
        print("🔁 Sudoku board has been cleared.")
        self.board.display()
        
        # Return the system to InputState
        from core.states import InputState
        self.fsm.set_state(InputState())
        self.fsm.update()

    def exit(self):
        print("Exiting Reset State")