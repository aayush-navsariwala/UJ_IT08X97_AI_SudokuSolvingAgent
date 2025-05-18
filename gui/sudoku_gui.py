import tkinter as tk
from tkinter import messagebox
from tkinter import filedialog
from utils.image_parser import image_to_grid
from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg
from matplotlib.figure import Figure
import matplotlib.pyplot as plt
import time
from solver.backtracking import solve as backtrack_solve
from solver.constraint_propagation import solve as constraint_solve
from solver.dlx import solve as dlx_solve
import traceback
import mplcursors

class SudokuGUI:
    def __init__(self, root, board, fsm):
        self.root = root
        self.board = board
        self.fsm = fsm
        self.original_grid = None  
        self.entries = []
        self.all_results = [] 
        self.current_annotation = None

        self.main_frame = tk.Frame(self.root)
        self.main_frame.pack(fill=tk.BOTH, expand=True)

        self.left_frame = tk.Frame(self.main_frame)
        self.left_frame.pack(side=tk.LEFT, padx=20, pady=20)

        self.right_frame = tk.Frame(self.main_frame, width=600)
        self.right_frame.pack(side=tk.RIGHT, padx=20, pady=20)

        self.build_grid()
        self.build_buttons()
        self.build_status_bar()
        self.build_graph_section()
        
        self.validate_button.config(state=tk.DISABLED)
        self.solve_button.config(state=tk.DISABLED)
        self.reset_button.config(state=tk.DISABLED)


    def build_grid(self):
        for row in range(9):
            row_entries = []
            for col in range(9):
                entry = tk.Entry(self.left_frame, width=2, font=('Arial', 18), justify='center', state='disabled')
                entry.grid(row=row, column=col, padx=2, pady=2)
                row_entries.append(entry)
            self.entries.append(row_entries)

    def build_buttons(self):
        self.solve_button = None  
        button_frame = tk.Frame(self.root)
        button_frame.pack(pady=10)

        self.validate_button = tk.Button(button_frame, text="Validate", command=self.validate)
        self.validate_button.grid(row=0, column=0, padx=5)

        self.solve_button = tk.Button(button_frame, text="Solve", command=self.solve)
        self.solve_button.grid(row=0, column=1, padx=5)

        self.reset_button = tk.Button(button_frame, text="Reset", command=self.reset)
        self.reset_button.grid(row=0, column=2, padx=5)

        tk.Button(button_frame, text="Upload Image", command=self.upload_image).grid(row=0, column=5, padx=5)
        tk.Button(button_frame, text="Clear Graph", command=self.clear_graph).grid(row=0, column=6, padx=5)
        
        tk.Label(button_frame, text="Algorithm:").grid(row=0, column=3, padx=5)
        self.selected_algorithm = tk.StringVar()
        self.selected_algorithm.set("backtracking")  # default
        self.solve_button = tk.Button(button_frame, text="Solve", command=self.solve)
        self.solve_button.grid(row=0, column=1, padx=5)
        self.algo_menu = tk.OptionMenu(button_frame, self.selected_algorithm, "backtracking", "constraint_propagation", "dlx")
        self.algo_menu.grid(row=0, column=4, padx=5)
        self.algo_menu.config(state=tk.DISABLED)

        
    def build_status_bar(self):
        self.status_frame = tk.Frame(self.root)
        self.status_frame.pack(pady=5)

        self.status_label = tk.Label(self.status_frame, text="🟡 No puzzle loaded", fg="orange", font=("Arial", 10))
        self.status_label.pack()

        self.algorithm_label = tk.Label(self.status_frame, text="Algorithm: None", font=("Arial", 10))
        self.algorithm_label.pack()

        self.timer_label = tk.Label(self.status_frame, text="", font=("Arial", 10))
        self.timer_label.pack()

    def build_graph_section(self):
        self.graph_frame = tk.Frame(self.right_frame)
        self.graph_frame.grid(row=11, column=0, columnspan=9, pady=10)

        self.figure = Figure(figsize=(7, 5), dpi=100)
        self.ax = self.figure.add_subplot(111)
        self.ax.set_title("Algorithm Comparison")
        self.ax.set_xlabel("Algorithm")
        self.ax.set_ylabel("Time (ms)")

        self.canvas = FigureCanvasTkAgg(self.figure, master=self.graph_frame)
        self.canvas.get_tk_widget().pack()

    def compare_algorithms(self):
        from solver.backtracking import solve as backtrack_solve
        from solver.constraint_propagation import solve as constraint_solve
        from solver.dlx import solve as dlx_solve
        from core.board import SudokuBoard
        
        algorithms = {
            "Backtracking": backtrack_solve,
            "Constraint Propagation": constraint_solve,
            "DLX": dlx_solve
        }
        
        results = {}
        
        for name, algo_func in algorithms.items():
            copied_grid = [row.copy() for row in self.original_grid]
            board_copy = SudokuBoard(grid=copied_grid)

            start = time.time()
            success = algo_func(board_copy)
            end = time.time()

            results[name] = end - start if success else None

        self.all_results.append(results)
        self.update_graph_multiple()
        print("Raw timings (s):", results)
        print("Converted timings (ms):", [round((results[k] or 0) * 1000, 3) for k in results])


    def update_graph_multiple(self):
        self.ax.clear()
        self.ax.set_title("Algorithm Comparison Over Multiple Puzzles")
        self.ax.set_xlabel("Algorithm")
        self.ax.set_ylabel("Time (ms)")
        
        recent_results = self.all_results[-5:]
        base_index = max(0, len(self.all_results) - 5)
        
        color_cycle = plt.cm.get_cmap('tab10').colors
        
        algo_names = ["Backtracking", "Constraint Propagation", "DLX"]
        x_values = list(range(len(algo_names)))

        for i, result in enumerate(recent_results):
            times = [round((result.get(name) or 0) * 1000, 3) for name in algo_names]
            puzzle_num = base_index + i + 1
            line = self.ax.plot(
                x_values,
                times,
                linestyle='-',
                color=color_cycle[i % len(color_cycle)],
                label=f"Puzzle {puzzle_num}"
            )

            self.ax.scatter(
                x_values,
                times,
                s=60,  
                color=color_cycle[i % len(color_cycle)],
                alpha=0.3,  
                label=f"Puzzle {puzzle_num} - Timestamp"
            )

        all_times = []
        for result in recent_results:
            all_times.extend([(result.get(name) or 0) * 1000 for name in algo_names])

        max_time = max(all_times) if all_times else 1
        self.ax.set_ylim(0, max_time * 1.2)
        self.ax.set_xticks(x_values)
        self.ax.set_xticklabels(algo_names)
        self.ax.legend(loc="upper left", bbox_to_anchor=(1.0, 1.0))
        self.figure.tight_layout(rect=[0, 0, 0.85, 1])
        
        if self.current_annotation:
            self.current_annotation.set_visible(False)
            self.canvas.draw_idle()

        self.current_annotation = None 
        
        self.canvas.draw()
        
        cursor = mplcursors.cursor(self.ax.collections, hover=True)

        def show_tooltip(sel):
            if sel.index is None:
                sel.annotation.set_text("Invalid point")
                return 
            try:
                if self.current_annotation and self.current_annotation != sel.annotation:
                    self.current_annotation.set_visible(False)
                    self.canvas.draw_idle()
                    
                algo_index = int(sel.artist.get_offsets()[sel.index][0])
                algo_label = algo_names[algo_index]
                y_val = sel.artist.get_offsets()[sel.index][1]
                puzzle_label = sel.artist.get_label().replace(" - Timestamp", "")
                sel.annotation.set_text(f"{puzzle_label} - {algo_label}: {y_val:.3f} ms")
                
                self.current_annotation = sel.annotation
            except Exception as e:
                sel.annotation.set_text("Invalid point")
                print("Tooltip error:", e)

        cursor.connect("add", show_tooltip)
        
    def update_graph(self, results):
        self.ax.clear()
        self.ax.set_title("Algorithm Comparison")
        self.ax.set_xlabel("Algorithm")
        self.ax.set_ylabel("Time (ms)")

        names = list(results.keys())
        times = [round((results[name] or 0) * 1000, 3) for name in names]  

        self.ax.plot(names, times, marker='o')
        self.figure.tight_layout(rect=[0, 0, 0.85, 1])  
        self.canvas.draw()
        
        mplcursors.cursor(self.ax.lines, hover=True).connect(
            "add", lambda sel: sel.annotation.set_text(
                f"{sel.artist.get_xdata()[sel.index]}: {sel.artist.get_ydata()[sel.index]:.3f} ms"
            )
        )

        
    def clear_graph(self):
        self.all_results.clear()
        mplcursors.cursor(self.ax, hover=True).remove()
        self.ax.clear()
        self.ax.set_title("Algorithm Comparison Over Multiple Puzzles")
        self.ax.set_xlabel("Algorithm")
        self.ax.set_ylabel("Time (ms)")
        self.canvas.draw()


    def validate(self):
        self.update_board_from_ui()
        self.fsm.set_state(self.fsm.validation_state)
        self.fsm.update()
        
        # GUI-controlled feedback
        if self.status_label["text"].startswith("✅"):
            messagebox.showinfo("Validation", "✅ The Sudoku puzzle is valid!")
        elif self.status_label["text"].startswith("❌"):
            messagebox.showerror("Validation", "❌ The Sudoku puzzle is invalid.")
            
    def is_board_valid(self):
        # Reuse same logic from ValidationState
        for row in range(9):
            for col in range(9):
                num = self.board.grid[row][col]
                if num != 0:
                    self.board.grid[row][col] = 0
                    if not self.board.is_valid(row, col, num):
                        self.board.grid[row][col] = num
                        return False
                    self.board.grid[row][col] = num
        return True

        
    def solve(self):
        self.update_board_from_ui()
        chosen_algo = self.selected_algorithm.get()
        # Recreate solving state with the selected algorithm
        self.algorithm_label.config(text=f"Algorithm: {chosen_algo}")
        self.fsm.set_state(self.fsm.solving_state_class(self.board, self.fsm, algorithm=chosen_algo))
        self.fsm.update()
        self.update_ui_from_board()

    def reset(self):
        if self.original_grid is None:
            messagebox.showwarning("Reset", "No puzzle has been uploaded yet.")
            return

        response = messagebox.askquestion(
            "Reset Puzzle",
            "What would you like to do?\n\n"
            "Yes = Replace the puzzle (upload new image)\n"
            "No = Clear the board to its original uploaded state",
            icon='question'
        )

        if response == 'yes':
            self.upload_image()
        else:
            self.board.grid = [row.copy() for row in self.original_grid]
            self.update_ui_from_board()
            self.solve_button.config(state=tk.NORMAL)
            self.status_label.config(text="🔄 Board reset to original values", fg="blue")

    def update_board_from_ui(self):
        for row in range(9):
            for col in range(9):
                val = self.entries[row][col].get()
                self.board.grid[row][col] = int(val) if val.isdigit() and 1 <= int(val) <= 9 else 0

    def update_ui_from_board(self):
        for row in range(9):
            for col in range(9):
                entry = self.entries[row][col]
                entry.config(state='normal')
                entry.delete(0, tk.END)
                val = self.board.grid[row][col]
                if val != 0:
                    entry.insert(0, str(val))
                entry.config(state='disabled')
                    
    def upload_image(self):
        file_path = filedialog.askopenfilename(
            title="Select Sudoku Image",
            filetypes=[("Image files", "*.jpg *.png *.jpeg *.bmp")]
        )
        if not file_path:
            return
        
        # Show loading status immediately
        self.status_label.config(text="⏳ Loading puzzle, please wait...", fg="orange")
        self.root.update_idletasks()  

        try:
            grid = image_to_grid(file_path)
            self.original_grid = [row.copy() for row in grid]
            self.board.grid = [row.copy() for row in grid]
            self.update_ui_from_board()
            
            self.root.after(100, self.validate_uploaded_board)
                
        except Exception as e:
            self.status_label.config(text="❌ Failed to load puzzle", fg="red")
            self.disable_controls()
            self.root.after(100, lambda: messagebox.showerror("Error", f"Could not read Sudoku image.\n\nReason: {str(e)}"))
            
    def validate_uploaded_board(self):
        if self.is_board_valid():
            self.status_label.config(text="✅ Puzzle loaded and valid", fg="green")
            self.solve_button.config(state=tk.NORMAL)
            
            self.validate_button.config(state=tk.NORMAL)
            self.reset_button.config(state=tk.NORMAL)
            self.algo_menu.config(state=tk.NORMAL)
            
            self.compare_algorithms()
        else:
            self.status_label.config(text="❌ Puzzle loaded but invalid", fg="red")
            self.solve_button.config(state=tk.DISABLED)
            self.validate_button.config(state=tk.NORMAL)
            self.reset_button.config(state=tk.NORMAL)
            self.algo_menu.config(state=tk.NORMAL)

            self.root.after(100, lambda: messagebox.showerror(
                "Validation Error", "❌ The uploaded Sudoku puzzle is invalid."))




