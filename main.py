from gui.sudoku_gui import SudokuGUI
import tkinter as tk
from core.board import SudokuBoard
from core.fsm import FSMManager
from core.states import InputState, ValidationState, SolvingState, WinState, ResetState
from solver.backtracking import solve

if __name__ == "__main__":
    board = SudokuBoard()

    # Initializing the FSM
    fsm = FSMManager()
    
    # Define the states and attach them to the FSM
    fsm.input_state = InputState()
    fsm.validation_state = ValidationState(board, fsm)
    fsm.solving_state_class = SolvingState  
    fsm.win_state = WinState(board)
    fsm.reset_state = ResetState(board, fsm)
    
    fsm.set_state(fsm.input_state)

    # Launch GUI
    root = tk.Tk()
    root.title("Sudoku Solver AI (FSM-Based)")
    app = SudokuGUI(root, board, fsm)
    fsm.gui = app
    root.mainloop()