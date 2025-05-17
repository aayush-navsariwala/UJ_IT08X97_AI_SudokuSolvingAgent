from core.fsm import State
from solver.backtracking import solve
from solver.constraint_propagation import solve as constraint_solve
from solver.dlx import solve as dlx_solve
import time
import tkinter as tk

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
        valid = self.is_valid_board()
        if hasattr(self.fsm, 'gui'):
            gui = self.fsm.gui
            if valid:
                gui.status_label.config(text="✅ Puzzle is valid", fg="green")
                gui.solve_button.config(state=tk.NORMAL)
            else:
                gui.status_label.config(text="❌ Puzzle is invalid", fg="red")
                gui.solve_button.config(state=tk.DISABLED)

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
        print(f"Solving with {self.algorithm}...")
                
        start_time = time.time()
        
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
            
        duration = time.time() - start_time
        print(f"🕒 Execution time: {duration:.5f} seconds")
        
        if hasattr(self.fsm, 'gui'):
            self.fsm.gui.timer_label.config(text=f"🕒 Execution time: {duration:.5f} seconds")

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
        print("Entered Win State 🎉")

    def execute(self):
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
        print("Entered Reset State 🔄")

    def execute(self):
        # Reset board to all zeros
        self.board.grid = [[0 for _ in range(9)] for _ in range(9)]
        print("🔁 Sudoku board has been cleared.")
        self.board.display()
        
        # Return to InputState
        from core.states import InputState
        self.fsm.set_state(InputState())
        self.fsm.update()

    def exit(self):
        print("Exiting Reset State")