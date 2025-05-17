import tkinter as tk
from tkinter import messagebox
from tkinter import filedialog
from utils.image_parser import image_to_grid

class SudokuGUI:
    def __init__(self, root, board, fsm):
        self.root = root
        self.board = board
        self.fsm = fsm
        self.entries = []

        self.build_grid()
        self.build_buttons()

    def build_grid(self):
        for row in range(9):
            row_entries = []
            for col in range(9):
                entry = tk.Entry(self.root, width=2, font=('Arial', 18), justify='center')
                entry.grid(row=row, column=col, padx=2, pady=2)
                row_entries.append(entry)
            self.entries.append(row_entries)

    def build_buttons(self):
        button_frame = tk.Frame(self.root)
        button_frame.grid(row=9, column=0, columnspan=9, pady=10)

        tk.Button(button_frame, text="Validate", command=self.validate).grid(row=0, column=0, padx=5)
        tk.Button(button_frame, text="Solve", command=self.solve).grid(row=0, column=1, padx=5)
        tk.Button(button_frame, text="Reset", command=self.reset).grid(row=0, column=2, padx=5)
        tk.Button(button_frame, text="Upload Image", command=self.upload_image).grid(row=0, column=5, padx=5)
        
        tk.Label(button_frame, text="Algorithm:").grid(row=0, column=3, padx=5)
        self.selected_algorithm = tk.StringVar()
        self.selected_algorithm.set("backtracking")  # default
        algo_menu = tk.OptionMenu(button_frame, self.selected_algorithm, "backtracking", "constraint_propagation", "dlx")
        algo_menu.grid(row=0, column=4, padx=5)

    def validate(self):
        self.update_board_from_ui()
        self.fsm.set_state(self.fsm.validation_state)
        self.fsm.update()

    def solve(self):
        self.update_board_from_ui()
        chosen_algo = self.selected_algorithm.get()
        # Recreate solving state with the selected algorithm
        self.fsm.set_state(self.fsm.solving_state_class(self.board, self.fsm, algorithm=chosen_algo))
        self.fsm.update()
        self.update_ui_from_board()

    def reset(self):
        self.fsm.set_state(self.fsm.reset_state)
        self.fsm.update()
        self.update_ui_from_board()

    def update_board_from_ui(self):
        for row in range(9):
            for col in range(9):
                val = self.entries[row][col].get()
                self.board.grid[row][col] = int(val) if val.isdigit() and 1 <= int(val) <= 9 else 0

    def update_ui_from_board(self):
        for row in range(9):
            for col in range(9):
                val = self.board.grid[row][col]
                self.entries[row][col].delete(0, tk.END)
                if val != 0:
                    self.entries[row][col].insert(0, str(val))
                    
    def upload_image(self):
        file_path = filedialog.askopenfilename(
            title="Select Sudoku Image",
            filetypes=[("Image files", "*.jpg *.png *.jpeg *.bmp")]
        )
        if not file_path:
            return

        try:
            grid = image_to_grid(file_path)
            self.board.grid = grid
            self.update_ui_from_board()
            print("✅ Image loaded and board populated successfully.")
        except Exception as e:
            messagebox.showerror("Error", f"Could not read Sudoku image.\n\n{str(e)}")
