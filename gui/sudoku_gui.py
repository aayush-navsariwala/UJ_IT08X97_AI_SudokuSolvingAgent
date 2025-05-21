import tkinter as tk
from tkinter import messagebox
from tkinter import filedialog
from tkinter import ttk
from utils.image_parser import image_to_grid
from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg
from matplotlib.figure import Figure
import matplotlib.pyplot as plt
import time
# from solver.backtracking import solve as backtrack_solve
# from solver.constraint_propagation import solve as constraint_solve
# from solver.dlx import solve as dlx_solve
import traceback
import mplcursors

class SudokuGUI:
    def __init__(self, root, board, fsm):
        # Configuring the root grid layout for the two main columns of the GUI
        self.root = root
        self.root.grid_columnconfigure(0, weight=0)
        self.root.grid_columnconfigure(1, weight=1)
        self.root.grid_rowconfigure(0, weight=1)

        # Sudoku board model
        self.board = board
        # FSM managing game state
        self.fsm = fsm
        # Stores the uploaded puzzle to be reset
        self.original_grid = None
        # 2D list of entry widgets 
        self.entries = []
        # Stores algorithm timing results
        self.all_results = [] 
        # Tracks the tooltip annotations on the graph
        self.current_annotation = None

        # Main layout frame - unused but stores the other frames on it
        self.main_frame = tk.Frame(self.root)
        self.main_frame.grid(row=0, column=0, sticky="nsew")

        # Frame that holds the 9x9 grid, buttons, status of puzzle and results table
        self.left_frame = tk.Frame(self.root)
        self.left_frame.grid(row=0, column=0, sticky="n", padx=10, pady=10)

        # Frame that holds the matplotlib graph of the 3 algorithms
        self.right_frame = tk.Frame(self.root)
        self.right_frame.grid(row=0, column=1, sticky="n", padx=10, pady=10)

        # Build UI sections
        self.build_grid()
        self.build_buttons()
        self.build_status_bar()
        self.build_graph_section()
        self.build_results_table()
        
        # Disables the validate, solve and reset button until a puzzle is loaded in app
        self.validate_button.config(state=tk.DISABLED)
        self.solve_button.config(state=tk.DISABLED)
        self.reset_button.config(state=tk.DISABLED)


    def build_grid(self):
        # Creates 9x9 entry widgets for the sudoku grid  
        for row in range(9):
            row_entries = []
            for col in range(9):
                # The grid is disabled by default as the user will not be solving the puzzle themselves on the grid
                entry = tk.Entry(self.left_frame, width=2, font=('Arial', 18), justify='center', state='disabled')
                entry.grid(row=row, column=col, padx=2, pady=2)
                row_entries.append(entry)
            self.entries.append(row_entries)


    def build_buttons(self):
        # Creates the buttons and dropdown menu for the algorithm selection
        self.solve_button = None  
        button_frame = tk.Frame(self.root)
        button_frame.grid(row=9, column=0, columnspan=9, pady=10, sticky="w")

        self.validate_button = tk.Button(button_frame, text="Validate", command=self.validate)
        self.validate_button.grid(row=0, column=0, padx=5)

        self.solve_button = tk.Button(button_frame, text="Solve", command=self.solve)
        self.solve_button.grid(row=0, column=1, padx=5)

        self.reset_button = tk.Button(button_frame, text="Reset", command=self.reset)
        self.reset_button.grid(row=0, column=2, padx=5)

        # Upload image and clear graph buttons
        tk.Button(button_frame, text="Upload Image", command=self.upload_image).grid(row=0, column=5, padx=5)
        tk.Button(button_frame, text="Clear Graph", command=self.clear_graph).grid(row=0, column=6, padx=5)
        
        # Algorithm selection dropdown menu for grid solving
        tk.Label(button_frame, text="Algorithm:").grid(row=0, column=3, padx=5)
        self.selected_algorithm = tk.StringVar()
        # Sets the backtracking algorithm as default on the dropdown menu 
        self.selected_algorithm.set("backtracking") 
        self.solve_button = tk.Button(button_frame, text="Solve", command=self.solve)
        self.solve_button.grid(row=0, column=1, padx=5)
        self.algo_menu = tk.OptionMenu(button_frame, self.selected_algorithm, "backtracking", "constraint_propagation", "dlx")
        self.algo_menu.grid(row=0, column=4, padx=5)
        self.algo_menu.config(state=tk.DISABLED)


    def build_status_bar(self):
        # Displays info about the puzzle state, selected algorithm and the timing of that algorithm
        self.status_frame = tk.Frame(self.root)
        self.status_frame.grid(row=10, column=0, columnspan=9, pady=(5, 10), sticky="w")

        # Default label when no puzzle has been uploaded to the system
        self.status_label = tk.Label(self.status_frame, text="🟡 No puzzle loaded", fg="orange", font=("Arial", 10))
        self.status_label.grid()

        # Label when valid puzzle has been uploaded but algorithm has not been selected by the user
        self.algorithm_label = tk.Label(self.status_frame, text="Algorithm: None", font=("Arial", 10))
        self.algorithm_label.grid()

        # Label to show the amount of time taken for the selected algorithm to solve the grid of the uploaded puzzle
        self.timer_label = tk.Label(self.status_frame, text="", font=("Arial", 10))
        self.timer_label.grid()


    def build_graph_section(self):
        # Sets up the matplotlib graph in the right frame of the GUI
        self.graph_frame = tk.Frame(self.right_frame)
        self.graph_frame.grid(row=11, column=0, columnspan=9, pady=10)

        self.figure = Figure(figsize=(7, 5), dpi=100)
        self.ax = self.figure.add_subplot(111)
        
        # Labelling the title of the graph, the 3 algorithm being compared and their respective times 
        self.ax.set_title("Algorithm Comparison")
        self.ax.set_xlabel("Algorithm")
        self.ax.set_ylabel("Time (ms)")

        self.canvas = FigureCanvasTkAgg(self.figure, master=self.right_frame)  
        self.canvas.get_tk_widget().grid()


    def compare_algorithms(self):
        # Automatically runs all 3 algorithms on the uploaded puzzle as long as it is valid
        import time
        from solver.backtracking import solve as bt_solve
        from solver.constraint_propagation import solve as cp_solve
        from solver.dlx import solve as dlx_solve
        from core.board import SudokuBoard
        import copy
        
        # Debugging for constraint propagation import
        print("🧠 Confirming cp_solve is a function:", callable(cp_solve))  
        
        safe_solvers = {
            "Backtracking": bt_solve,
            "Constraint Propagation": cp_solve,
            "DLX": dlx_solve
        }
        
        # Stores the execution time from each algorithm on the uploaded puzzle 
        results = {}
        
        # Limiting DLX runtime for debugging purposes
        MAX_DLX_TIME = 3.0
        
        # Solve the puzzle with each algorithm and measure their times individually
        for name in safe_solvers:
            # New reference for each loop
            algo_func = safe_solvers[name]
            # copied_grid = [row.copy() for row in self.original_grid]
            copied_grid = copy.deepcopy(self.original_grid)
            board_copy = SudokuBoard(grid=copied_grid)

            # Added terminal output for debugging
            print(f"Solving {name}...")
            
            start = time.time()
            success = False
            
            # Using a try block for error handling
            try:
                if name == "DLX":
                    # Try solving and abort if too long
                    temp_start = time.time()
                    success = algo_func(board_copy)
                    elapsed = time.time() - temp_start
                    if elapsed > MAX_DLX_TIME:
                        print("⚠️ DLX timeout exceeded")
                        success = False
                else:
                    # Final recheck to avoid overwriting
                    if not callable(algo_func):
                        print(f"❌ {name} solver was overwritten! Got type: {type(algo_func)}")
                        success = False
                    else:
                        success = algo_func(board_copy)          
            except Exception as e:
                print(f"Error in {name} solver: {e}")
                success = False
            
            end = time.time()
            duration = end - start
            results[name] = duration if success else None
            
            print(f"✅ Done {name} in {round(duration * 1000, 3)} ms")

            # results[name] = end - start if success else None
        
        # Store the results for the graph and table
        self.all_results.append(results)
        self.update_graph_multiple()
        
        # Conversion of times to milliseconds and insert them into the table
        puzzle_name = f"Puzzle {len(self.all_results)}"
        timings_ms = {
            "Puzzle": puzzle_name,
            "Backtracking": round((results["Backtracking"] or 0) * 1000, 3),
            "Constraint Propagation": round((results["Constraint Propagation"] or 0) * 1000, 3),
            "DLX": round((results["DLX"] or 0) * 1000, 3)
        }

        self.results_table.insert("", "end", values=(
            timings_ms["Puzzle"],
            timings_ms["Backtracking"],
            timings_ms["Constraint Propagation"],
            timings_ms["DLX"]
        ))

        # Terminal outputting for debugging 
        print("Raw timings (s):", results)
        print("Converted timings (ms):", list(timings_ms.values())[1:])


    def build_results_table(self):
        # Create a treeview widget to display a table of the puzzle timing results 
        self.results_table = ttk.Treeview(
            self.left_frame, 
            columns=("Puzzle", "Backtracking", "Constraint Propagation", "DLX"), 
            show="headings"
            )
        
        # Defining the headers of the table
        self.results_table.heading("Puzzle", text="Puzzle")
        self.results_table.heading("Backtracking", text="Backtracking (ms)")
        self.results_table.heading("Constraint Propagation", text="Constraint Propagation (ms)")
        self.results_table.heading("DLX", text="DLX (ms)")
    
        # Set the widths of the columns 
        self.results_table.column("Puzzle", width=100)
        self.results_table.column("Backtracking", width=140)
        self.results_table.column("Constraint Propagation", width=190)
        self.results_table.column("DLX", width=100)

        # Placing the table on the left frame using the grid
        self.results_table.grid(row=12, column=0, columnspan=9, padx=10, pady=10)


    def update_graph_multiple(self):
        # Clear the existing plot first and set the title, x-axis and y-axis of the graph
        self.ax.clear()
        self.ax.set_title("Algorithm Comparison Over Multiple Puzzles")
        self.ax.set_xlabel("Algorithm")
        self.ax.set_ylabel("Time (ms)")
        
        # Get the most recent 5 puzzles to display on the graph
        recent_results = self.all_results[-5:]
        base_index = max(0, len(self.all_results) - 5)
        
        # Colour pallette for lines
        color_cycle = plt.cm.get_cmap('tab10').colors
        
        # Fixed order of algorithms on the graph
        algo_names = ["Backtracking", "Constraint Propagation", "DLX"]
        x_values = list(range(len(algo_names)))

        # Extracting the times in ms for the puzzle
        for i, result in enumerate(recent_results):
            times = [
                round(result.get(name, 0) * 1000, 3) if result.get(name) is not None else 0
                for name in algo_names
            ]

            puzzle_num = base_index + i + 1
            
            # Plot line connecting algorithms for the puzzle
            line = self.ax.plot(
                x_values,
                times,
                linestyle='-',
                color=color_cycle[i % len(color_cycle)],
                label=f"Puzzle {puzzle_num}"
            )

            # Overlay scatter markers for hover functionality with cursor on graph
            self.ax.scatter(
                x_values,
                times,
                s=60,  
                color=color_cycle[i % len(color_cycle)],
                alpha=0.3,  
                label=f"Puzzle {puzzle_num} - Timestamp"
            )

        # Calculate the scale of the y-axis based on all values of the graph
        all_times = []
        for result in recent_results:
            all_times.extend([(result.get(name) or 0) * 1000 for name in algo_names])

        
        max_time = max(all_times) if all_times else 1
        self.ax.set_ylim(0, max_time * 1.2)
        
        # Label the x-axis with the algorithm names
        self.ax.set_xticks(x_values)
        self.ax.set_xticklabels(algo_names)
        
        # Place the legend and layout
        self.ax.legend(loc="upper left", bbox_to_anchor=(1.0, 1.0))
        self.figure.tight_layout(rect=[0, 0, 0.85, 1])
        
        # Clear any existing hover effect on the graph
        if self.current_annotation:
            self.current_annotation.set_visible(False)
            self.canvas.draw_idle()
        self.current_annotation = None 
        
        # Draw the updated canvas
        self.canvas.draw()
        
        # Add mplcursors hover tool for the scatter points for each algorithm
        cursor = mplcursors.cursor(self.ax.collections, hover=True)

        def show_tooltip(sel):
            if sel.index is None:
                sel.annotation.set_text("Invalid point")
                return 
            try:
                # Hide the previous tooltip so only one is on the graph 
                if self.current_annotation and self.current_annotation != sel.annotation:
                    self.current_annotation.set_visible(False)
                    self.canvas.draw_idle()
                    
                # Extract all algorithms time info
                algo_index = int(sel.artist.get_offsets()[sel.index][0])
                algo_label = algo_names[algo_index]
                y_val = sel.artist.get_offsets()[sel.index][1]
                puzzle_label = sel.artist.get_label().replace(" - Timestamp", "")
                
                # Format the tooltip text
                sel.annotation.set_text(f"{puzzle_label} - {algo_label}: {y_val:.3f} ms")
                self.current_annotation = sel.annotation
            except Exception as e:
                sel.annotation.set_text("Invalid point")
                print("Tooltip error:", e)

        # Connect the hover function to the cursor
        cursor.connect("add", show_tooltip)
      
        
    def update_graph(self, results):
        # Clear the previous graph
        self.ax.clear()
        self.ax.set_title("Algorithm Comparison")
        self.ax.set_xlabel("Algorithm")
        self.ax.set_ylabel("Time (ms)")

        # Extract values from the results dictionary
        names = list(results.keys())
        times = [round((results[name] or 0) * 1000, 3) for name in names]  

        # Plot basic line graph with one dataset
        self.ax.plot(names, times, marker='o')
        self.figure.tight_layout(rect=[0, 0, 0.85, 1])  
        self.canvas.draw()
        
        # Add hover cursor for a single line graph
        mplcursors.cursor(self.ax.lines, hover=True).connect(
            "add", lambda sel: sel.annotation.set_text(
                f"{sel.artist.get_xdata()[sel.index]}: {sel.artist.get_ydata()[sel.index]:.3f} ms"
            )
        )

      
    def clear_graph(self):
        # Clears the algorithm comparison graph and resets all stored results
        self.all_results.clear()
        mplcursors.cursor(self.ax, hover=True).remove()
        self.ax.clear()
        self.ax.set_title("Algorithm Comparison Over Multiple Puzzles")
        self.ax.set_xlabel("Algorithm")
        self.ax.set_ylabel("Time (ms)")
        self.canvas.draw()


    def validate(self):
        # Called when the user clicks the validate button to see if the current board is valid
        self.update_board_from_ui()
        # Sets the FSM to validation state
        self.fsm.set_state(self.fsm.validation_state)
        self.fsm.update()
        
        # Provide user feedback through popups
        if self.status_label["text"].startswith("✅"):
            messagebox.showinfo("Validation", "✅ The Sudoku puzzle is valid!")
        elif self.status_label["text"].startswith("❌"):
            messagebox.showerror("Validation", "❌ The Sudoku puzzle is invalid.")
    
    # Validates the board manually through upload checking        
    def is_board_valid(self):
        # Temporarily clears each cell to check if re-inserting it would break validity 
        for row in range(9):
            for col in range(9):
                num = self.board.grid[row][col]
                if num != 0:
                    self.board.grid[row][col] = 0
                    if not self.board.is_valid(row, col, num):
                        # Restores the original cells
                        self.board.grid[row][col] = num
                        return False
                    self.board.grid[row][col] = num
        return True

    
    def solve(self):
        # Called when the user clicks the solve button
        self.update_board_from_ui()
        chosen_algo = self.selected_algorithm.get()
        # Update the status bar
        self.algorithm_label.config(text=f"Algorithm: {chosen_algo}")
        # Move the FSM into solving state with the selected algorithm 
        self.fsm.set_state(self.fsm.solving_state_class(self.board, self.fsm, algorithm=chosen_algo))
        self.fsm.update()
        # Update the solution onto the grid
        self.update_ui_from_board()

    
    def reset(self):
        # Called when the user clicks the reset button
        if self.original_grid is None:
            messagebox.showwarning("Reset", "No puzzle has been uploaded yet.")
            return

        # Asks the user whether they want to reset the current puzzle or replace it with another one
        response = messagebox.askquestion(
            "Reset Puzzle",
            "What would you like to do?\n\n"
            "Yes = Replace the puzzle (upload new image)\n"
            "No = Clear the board to its original uploaded state",
            icon='question'
        )

        if response == 'yes':
            # Load a new puzzle from an image
            self.upload_image()
        else:
            # Restore the original grid unsolved
            self.board.grid = [row.copy() for row in self.original_grid]
            self.update_ui_from_board()
            self.solve_button.config(state=tk.NORMAL)
            self.status_label.config(text="🔄 Board reset to original values", fg="blue")


    def update_board_from_ui(self):
        # Push values from the UI grid into the internal board representation
        for row in range(9):
            for col in range(9):
                val = self.entries[row][col].get()
                self.board.grid[row][col] = int(val) if val.isdigit() and 1 <= int(val) <= 9 else 0


    def update_ui_from_board(self):
        # Update the UI entries from the internal board grid
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
        # Loads the puzzle from an image file and displays in on the board
        file_path = filedialog.askopenfilename(
            title="Select Sudoku Image",
            filetypes=[("Image files", "*.jpg *.png *.jpeg *.bmp")]
        )
        if not file_path:
            return
        
        # Labels to give users an update on their uploaded board
        self.status_label.config(text="⏳ Loading puzzle, please wait...", fg="orange")
        self.root.update_idletasks()  

        try:
            # Calls OCR which is an external image parser to extract values from the uploaded board
            grid = image_to_grid(file_path)
            self.original_grid = [row.copy() for row in grid]
            self.board.grid = [row.copy() for row in grid]
            self.update_ui_from_board()
            # Auto-validate after a short delay
            self.root.after(100, self.validate_uploaded_board)
                
        except Exception as e:
            # Show failure popup and disable interactive controls until valid puzzle is uploaded
            self.status_label.config(text="❌ Failed to load puzzle", fg="red")
            self.disable_controls()
            self.root.after(100, lambda: messagebox.showerror("Error", f"Could not read Sudoku image.\n\nReason: {str(e)}"))
            
            
    def validate_uploaded_board(self):
        # Validates the uploaded puzzle and updates the status 
        if self.is_board_valid():
            self.status_label.config(text="✅ Puzzle loaded and valid", fg="green")
            self.solve_button.config(state=tk.NORMAL)
            self.validate_button.config(state=tk.NORMAL)
            self.reset_button.config(state=tk.NORMAL)
            self.algo_menu.config(state=tk.NORMAL)
            # Automatically runs the algorithm comparison for the graph
            self.compare_algorithms()
        else:
            # Disable solving for invalid puzzle 
            self.status_label.config(text="❌ Puzzle loaded but invalid", fg="red")
            self.solve_button.config(state=tk.DISABLED)
            self.validate_button.config(state=tk.NORMAL)
            self.reset_button.config(state=tk.NORMAL)
            self.algo_menu.config(state=tk.NORMAL)
            self.root.after(100, lambda: messagebox.showerror(
                "Validation Error", "❌ The uploaded Sudoku puzzle is invalid."))