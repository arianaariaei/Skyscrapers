import tkinter as tk
from tkinter import ttk, messagebox
from typing import List, Tuple, Optional
import time
from ttkthemes import ThemedTk
import customtkinter as ctk


class SkyscrapersPuzzle:
    def __init__(self, size: int, top: List[int], right: List[int], bottom: List[int], left: List[int]):
        self.size = size
        self.top = top
        self.right = right
        self.bottom = bottom
        self.left = left
        self.board = [[0 for _ in range(size)] for _ in range(size)]
        self.nodes_explored = 0

    def is_valid_placement(self, row: int, col: int, value: int) -> bool:
        # Check row and column for duplicates
        for i in range(self.size):
            if self.board[row][i] == value or self.board[i][col] == value:
                return False

        # Temporarily place the value to check constraints
        old_value = self.board[row][col]
        self.board[row][col] = value

        # Check row constraints if row is complete
        if all(self.board[row][i] != 0 for i in range(self.size)):
            visible_left = self.count_visible_buildings([self.board[row][i] for i in range(self.size)])
            visible_right = self.count_visible_buildings([self.board[row][i] for i in range(self.size)][::-1])
            if visible_left != self.left[row] or visible_right != self.right[row]:
                self.board[row][col] = old_value
                return False

        # Check column constraints if column is complete
        if all(self.board[i][col] != 0 for i in range(self.size)):
            column = [self.board[i][col] for i in range(self.size)]
            visible_top = self.count_visible_buildings(column)
            visible_bottom = self.count_visible_buildings(column[::-1])
            if visible_top != self.top[col] or visible_bottom != self.bottom[col]:
                self.board[row][col] = old_value
                return False

        # Reset the cell and return true if all checks pass
        self.board[row][col] = old_value
        return True

    def count_visible_buildings(self, line: List[int]) -> int:
        if 0 in line:  # Don't count if line contains empty cells
            return 0

        visible = 1  # First building is always visible
        max_height = line[0]

        for height in line[1:]:
            if height > max_height:
                visible += 1
                max_height = height

        return visible

    def get_mrv_variable(self) -> Optional[Tuple[int, int]]:
        min_values = float('inf')
        mrv_pos = None

        for i in range(self.size):
            for j in range(self.size):
                if self.board[i][j] == 0:
                    valid_values = sum(1 for value in range(1, self.size + 1)
                                       if self.is_valid_placement(i, j, value))
                    if valid_values < min_values and valid_values > 0:
                        min_values = valid_values
                        mrv_pos = (i, j)

        return mrv_pos

    def solve(self) -> bool:
        self.nodes_explored += 1

        # Find the next empty position using MRV
        pos = self.get_mrv_variable()
        if not pos:
            # If no empty positions, check if the solution is valid
            return self.is_solution_valid()

        row, col = pos
        # Try values in random order to avoid getting stuck in patterns
        for value in range(1, self.size + 1):
            if self.is_valid_placement(row, col, value):
                self.board[row][col] = value
                if self.solve():
                    return True
                self.board[row][col] = 0

        return False

    def is_solution_valid(self) -> bool:
        # Check if all rows and columns satisfy the constraints
        for i in range(self.size):
            # Check rows
            row = [self.board[i][j] for j in range(self.size)]
            if (self.count_visible_buildings(row) != self.left[i] or
                    self.count_visible_buildings(row[::-1]) != self.right[i]):
                return False

            # Check columns
            col = [self.board[j][i] for j in range(self.size)]
            if (self.count_visible_buildings(col) != self.top[i] or
                    self.count_visible_buildings(col[::-1]) != self.bottom[i]):
                return False

        return True


class ModernSkyscraperGUI:
    def __init__(self, root):
        self.root = root
        self.root.title("Skyscrapers Puzzle Solver")
        self.size = 5

        # Set color scheme
        self.colors = {
            'bg': '#1a1a2e',
            'card': '#16213e',
            'accent': '#7b2cbf',
            'accent_light': '#9d4edd',
            'text': '#e2e2e2',
            'grid_lines': '#2a2a4a'
        }

        # Configure window
        window_width = 800
        window_height = 900
        screen_width = root.winfo_screenwidth()
        screen_height = root.winfo_screenheight()
        center_x = int(screen_width / 2 - window_width / 2)
        center_y = int(screen_height / 2 - window_height / 2)
        self.root.geometry(f'{window_width}x{window_height}+{center_x}+{center_y}')
        self.root.configure(bg=self.colors['bg'])
        self.root.resizable(False, False)

        # Create the main container
        self.create_main_frame()
        self.create_title()
        self.create_board_frame()
        self.create_board_widgets()
        self.create_control_buttons()
        self.create_status_bar()

    def create_main_frame(self):
        """Create the main container frame"""
        self.main_frame = ctk.CTkFrame(
            self.root,
            fg_color=self.colors['bg'],
            corner_radius=0
        )
        self.main_frame.pack(expand=True, fill='both', padx=20, pady=20)

    def create_title(self):
        """Create the title section"""
        title_frame = ctk.CTkFrame(
            self.main_frame,
            fg_color=self.colors['bg'],
            corner_radius=0
        )
        title_frame.pack(pady=(0, 20))

        ctk.CTkLabel(
            title_frame,
            text="Skyscrapers",
            font=('Helvetica', 40, 'bold'),
            text_color=self.colors['accent_light']
        ).pack()

        ctk.CTkLabel(
            title_frame,
            text="Puzzle Solver",
            font=('Helvetica', 24),
            text_color=self.colors['text']
        ).pack()

    def create_board_frame(self):
        """Create the frame that will contain the puzzle board"""
        self.board_frame = ctk.CTkFrame(
            self.main_frame,
            fg_color=self.colors['card'],
            corner_radius=15,
            border_width=2,
            border_color=self.colors['grid_lines']
        )
        self.board_frame.pack(padx=20, pady=20)

    def create_board_widgets(self):
        """Create the puzzle board with constraints"""
        self.top_constraints = []
        self.bottom_constraints = []
        self.left_constraints = []
        self.right_constraints = []
        self.board_entries = []

        # Grid container
        grid_frame = ctk.CTkFrame(
            self.board_frame,
            fg_color=self.colors['card'],
            corner_radius=15
        )
        grid_frame.pack(padx=20, pady=20)

        # Top constraints
        for i in range(self.size):
            entry = ctk.CTkEntry(
                grid_frame,
                width=50,
                height=50,
                corner_radius=10,
                fg_color=self.colors['bg'],
                text_color=self.colors['accent_light'],
                font=('Helvetica', 18),
                justify='center'
            )
            entry.grid(row=0, column=i + 1, padx=5, pady=5)
            self.top_constraints.append(entry)

        # Main board with left and right constraints
        for i in range(self.size):
            # Left constraints
            left_entry = ctk.CTkEntry(
                grid_frame,
                width=50,
                height=50,
                corner_radius=10,
                fg_color=self.colors['bg'],
                text_color=self.colors['accent_light'],
                font=('Helvetica', 18),
                justify='center'
            )
            left_entry.grid(row=i + 1, column=0, padx=5, pady=5)
            self.left_constraints.append(left_entry)

            # Board entries
            row_entries = []
            for j in range(self.size):
                entry = ctk.CTkEntry(
                    grid_frame,
                    width=50,
                    height=50,
                    corner_radius=10,
                    fg_color=self.colors['bg'],
                    text_color=self.colors['text'],
                    font=('Helvetica', 20, 'bold'),
                    justify='center'
                )
                entry.grid(row=i + 1, column=j + 1, padx=5, pady=5)
                entry.configure(state='readonly')
                row_entries.append(entry)
            self.board_entries.append(row_entries)

            # Right constraints
            right_entry = ctk.CTkEntry(
                grid_frame,
                width=50,
                height=50,
                corner_radius=10,
                fg_color=self.colors['bg'],
                text_color=self.colors['accent_light'],
                font=('Helvetica', 18),
                justify='center'
            )
            right_entry.grid(row=i + 1, column=self.size + 1, padx=5, pady=5)
            self.right_constraints.append(right_entry)

        # Bottom constraints
        for i in range(self.size):
            entry = ctk.CTkEntry(
                grid_frame,
                width=50,
                height=50,
                corner_radius=10,
                fg_color=self.colors['bg'],
                text_color=self.colors['accent_light'],
                font=('Helvetica', 18),
                justify='center'
            )
            entry.grid(row=self.size + 1, column=i + 1, padx=5, pady=5)
            self.bottom_constraints.append(entry)

    def create_control_buttons(self):
        """Create the control buttons"""
        button_frame = ctk.CTkFrame(
            self.main_frame,
            fg_color=self.colors['bg'],
            corner_radius=0
        )
        button_frame.pack(pady=20)

        # Solve button
        ctk.CTkButton(
            button_frame,
            text="Solve Puzzle",
            command=self.solve_puzzle,
            font=('Helvetica', 18, 'bold'),
            fg_color=self.colors['accent'],
            hover_color=self.colors['accent_light'],
            corner_radius=15,
            width=200,
            height=50
        ).pack(side='left', padx=10)

        # Clear button
        ctk.CTkButton(
            button_frame,
            text="Clear Board",
            command=self.clear_board,
            font=('Helvetica', 18),
            fg_color=self.colors['card'],
            hover_color=self.colors['grid_lines'],
            corner_radius=15,
            width=150,
            height=50
        ).pack(side='left', padx=10)

        # Example button
        ctk.CTkButton(
            button_frame,
            text="Load Example",
            command=self.load_example,
            font=('Helvetica', 18),
            fg_color=self.colors['card'],
            hover_color=self.colors['grid_lines'],
            corner_radius=15,
            width=150,
            height=50
        ).pack(side='left', padx=10)

    def create_status_bar(self):
        """Create the status bar"""
        self.status_var = tk.StringVar()
        self.status_var.set("Ready to solve...")

        status_frame = ctk.CTkFrame(
            self.main_frame,
            fg_color=self.colors['bg'],
            corner_radius=0
        )
        status_frame.pack(pady=10)

        ctk.CTkLabel(
            status_frame,
            textvariable=self.status_var,
            font=('Helvetica', 14),
            text_color=self.colors['text']
        ).pack()

    def get_constraints(self) -> Optional[Tuple[List[int], List[int], List[int], List[int]]]:
        """Get and validate constraints from the input fields"""
        try:
            top = [int(entry.get()) for entry in self.top_constraints]
            right = [int(entry.get()) for entry in self.right_constraints]
            bottom = [int(entry.get()) for entry in self.bottom_constraints]
            left = [int(entry.get()) for entry in self.left_constraints]

            # Validate that all values are between 1 and size
            for values in [top, right, bottom, left]:
                if not all(1 <= x <= self.size for x in values):
                    raise ValueError
                if len(values) != self.size:
                    raise ValueError

            return top, right, bottom, left
        except ValueError:
            messagebox.showerror("Error", f"Please enter valid constraints (numbers 1-{self.size})")
            return None

    def update_board_display(self, board: List[List[int]]):
        """Update the display with the solved board"""
        for i in range(self.size):
            for j in range(self.size):
                entry = self.board_entries[i][j]
                entry.configure(state='normal')
                entry.delete(0, 'end')
                if board[i][j] != 0:
                    entry.insert(0, str(board[i][j]))
                entry.configure(state='readonly')

    def clear_board(self):
        """Clear all entries and reset the board"""
        # Clear constraints
        for entries in [self.top_constraints, self.right_constraints,
                        self.bottom_constraints, self.left_constraints]:
            for entry in entries:
                entry.delete(0, 'end')

        # Clear board
        for row in self.board_entries:
            for entry in row:
                entry.configure(state='normal')
                entry.delete(0, 'end')
                entry.configure(state='readonly')

        # Reset status
        self.status_var.set("Board cleared. Ready to solve...")

    def load_example(self):
        """Load an example puzzle"""
        example = {
            'top': [3, 2, 1, 3, 2],
            'right': [2, 3, 2, 1, 4],
            'bottom': [1, 2, 3, 2, 2],
            'left': [2, 2, 3, 2, 1]
        }

        self.clear_board()

        # Fill in the example values
        for i, val in enumerate(example['top']):
            self.top_constraints[i].insert(0, str(val))
        for i, val in enumerate(example['right']):
            self.right_constraints[i].insert(0, str(val))
        for i, val in enumerate(example['bottom']):
            self.bottom_constraints[i].insert(0, str(val))
        for i, val in enumerate(example['left']):
            self.left_constraints[i].insert(0, str(val))

        self.status_var.set("Example puzzle loaded. Ready to solve...")

    def solve_puzzle(self):
        """Solve the puzzle and display the solution"""
        self.status_var.set("Solving puzzle...")
        self.root.update()

        constraints = self.get_constraints()
        if not constraints:
            self.status_var.set("Invalid constraints. Please try again.")
            return

        top, right, bottom, left = constraints
        puzzle = SkyscrapersPuzzle(self.size, top, right, bottom, left)

        start_time = time.time()
        if puzzle.solve():
            end_time = time.time()
            self.update_board_display(puzzle.board)
            solve_time = end_time - start_time
            self.status_var.set(f"Solved in {solve_time:.3f} seconds! Explored {puzzle.nodes_explored} nodes.")
            messagebox.showinfo(
                "Success",
                f"Solution found!\nTime: {solve_time:.3f} seconds\n"
                f"Nodes explored: {puzzle.nodes_explored}"
            )
        else:
            self.status_var.set("No solution exists for this puzzle!")
            messagebox.showerror("Error", "No solution exists for this puzzle!")


def main():
    # Set CustomTkinter appearance
    ctk.set_appearance_mode("dark")
    ctk.set_default_color_theme("blue")

    # Create the root window
    root = ctk.CTk()
    app = ModernSkyscraperGUI(root)
    root.mainloop()


if __name__ == "__main__":
    main()
