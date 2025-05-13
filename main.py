import core.board
from gui.sudoku_gui import launch_gui
from core.fsm import FSMManager

if __name__ == "__main__":
    board = core.board.SudokuBoard()
    fsm = FSMManager()
    launch_gui(board, fsm)