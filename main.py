from core.board import SudokuBoard
from core.fsm import FSMManager
from core.states import InputState, ValidationState, SolvingState, ResetState
from solver.backtracking import solve

if __name__ == "__main__":
    # Sample incomplete Sudoku puzzle (0 implies the field is empty)
    sample_grid = [
        [5, 3, 0, 0, 7, 0, 0, 0, 0],
        [6, 0, 0, 1, 9, 5, 0, 0, 0],
        [0, 9, 8, 0, 0, 0, 0, 6, 0],
        [8, 0, 0, 0, 6, 0, 0, 0, 3],
        [4, 0, 0, 8, 0, 3, 0, 0, 1],
        [7, 0, 0, 0, 2, 0, 0, 0, 6],
        [0, 6, 0, 0, 0, 0, 2, 8, 0],
        [0, 0, 0, 4, 1, 9, 0, 0, 5],
        [0, 0, 0, 0, 8, 0, 0, 7, 9]
    ]

    # Initializing the Sudoku board
    board = SudokuBoard(sample_grid)
    print("Initial Sudoku Board:")
    board.display()

    # Initializing the FSM
    fsm = FSMManager()
    
    # Input
    fsm.set_state(InputState())
    fsm.update()
    
    # # Run Backtracking Solver
    # print("\nSolving Sudoku with Backtracking:")
    # if solve(board):
    #     print("Solved Sudoku Board:")
    #     board.display()
    # else:
    #     print("No solution found.")
    
    # Validation
    fsm.set_state(ValidationState(board, fsm))
    fsm.update()
    
    # Solving
    fsm.set_state(SolvingState(board, fsm, algorithm="backtracking"))
    fsm.update()
    
    fsm.set_state(ResetState(board, fsm))
    fsm.update()
