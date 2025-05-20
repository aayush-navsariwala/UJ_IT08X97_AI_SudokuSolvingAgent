from gui.sudoku_gui import SudokuGUI
import tkinter as tk
from core.board import SudokuBoard
from core.fsm import FSMManager
from core.states import InputState, ValidationState, SolvingState, WinState, ResetState
from solver.backtracking import solve

if __name__ == "__main__":
    # Create an instance of the sudoku board
    board = SudokuBoard()

    # Initialise the FSM
    fsm = FSMManager()
    
    # Instantiate and assign all of the FSM states
    fsm.input_state = InputState()
    fsm.validation_state = ValidationState(board, fsm)
    fsm.solving_state_class = SolvingState  
    fsm.win_state = WinState(board)
    fsm.reset_state = ResetState(board, fsm)
    
    # Set the initial state of the FSM to input
    fsm.set_state(fsm.input_state)

    # Create the main app window
    root = tk.Tk()
    root.title("Sudoku Solver AI (FSM-Based)")
    root.state('zoomed')  
    
    # Initialise the sudoku GUI with the board and FSM
    app = SudokuGUI(root, board, fsm)
    
    # Lets the FSM reference the GUI so it can update it
    fsm.gui = app
    
    # Run the app
    root.mainloop()