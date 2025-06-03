import tkinter as tk
from tkinter import messagebox
import random
import time

# Sentence class helps represent AI knowledge about cells and how many mines they contain
class Sentence:
    def __init__(self, cells, count):
        self.cells = set(cells)  # Set of cells
        self.count = count       # Number of mines in these cells

    def __eq__(self, other):
        return self.cells == other.cells and self.count == other.count

    def __str__(self):
        return f"{self.cells} = {self.count}"

# AI class for smart gameplay logic
class MinesweeperAI:
    def __init__(self, size):
        self.size = size
        self.mines = set()
        self.safes = set()
        self.moves = set()
        self.knowledge = []

    def mark_mine(self, cell):
        self.mines.add(cell)
        for sentence in self.knowledge:
            if cell in sentence.cells:
                sentence.cells.remove(cell)
                sentence.count -= 1

    def mark_safe(self, cell):
        self.safes.add(cell)
        for sentence in self.knowledge:
            if cell in sentence.cells:
                sentence.cells.remove(cell)

    def add_knowledge(self, cell, count):
        self.moves.add(cell)
        self.mark_safe(cell)

        # Get neighbors
        neighbors = set()
        for dx in range(-1, 2):
            for dy in range(-1, 2):
                if dx == 0 and dy == 0:
                    continue
                nx, ny = cell[0] + dx, cell[1] + dy
                if 0 <= nx < self.size and 0 <= ny < self.size:
                    if (nx, ny) not in self.safes and (nx, ny) not in self.mines:
                        neighbors.add((nx, ny))
                    elif (nx, ny) in self.mines:
                        count -= 1

        if neighbors:
            self.knowledge.append(Sentence(neighbors, count))

        self.update_knowledge()

    def update_knowledge(self):
        changed = True
        while changed:
            changed = False
            safes = set()
            mines = set()

            for sentence in self.knowledge:
                if sentence.count == 0:
                    safes |= sentence.cells
                elif len(sentence.cells) == sentence.count:
                    mines |= sentence.cells

            if safes:
                changed = True
                for cell in safes:
                    if cell not in self.safes:
                        self.mark_safe(cell)

            if mines:
                changed = True
                for cell in mines:
                    if cell not in self.mines:
                        self.mark_mine(cell)

            self.knowledge = [s for s in self.knowledge if s.cells]

            # Subset logic for inference
            new_sentences = []
            for s1 in self.knowledge:
                for s2 in self.knowledge:
                    if s1 != s2 and s1.cells.issubset(s2.cells):
                        diff_cells = s2.cells - s1.cells
                        diff_count = s2.count - s1.count
                        new_sentence = Sentence(diff_cells, diff_count)
                        if new_sentence not in self.knowledge and new_sentence not in new_sentences:
                            if len(new_sentence.cells) > 0:
                                new_sentences.append(new_sentence)
            if new_sentences:
                changed = True
                self.knowledge.extend(new_sentences)

    def next_move(self):
        for cell in self.safes:
            if cell not in self.moves:
                return cell
        return None

    def moves_left(self):
        return [cell for cell in self.safes if cell not in self.moves]

# Main GUI Game Class
class Minesweeper:
    def __init__(self, root):
        self.root = root
        self.root.title("Minesweeper with Smart AI")
        self.create_setup()

    def create_setup(self):
        # Ask for size and mine count
        self.size = int(input("Enter grid size (e.g. 8): "))
        self.mines = int(input("Enter number of mines: "))
        self.reset_game()

    def reset_game(self):
        # Reset state
        self.frame = tk.Frame(self.root)
        self.frame.pack()
        self.buttons = {}
        self.board = [[0 for _ in range(self.size)] for _ in range(self.size)]
        self.revealed = set()
        self.flags = set()
        self.ai = MinesweeperAI(self.size)
        self.start_time = time.time()

        # Place mines
        positions = set()
        while len(positions) < self.mines:
            x, y = random.randint(0, self.size-1), random.randint(0, self.size-1)
            positions.add((x, y))

        for (x, y) in positions:
            self.board[x][y] = -1

        # Calculate numbers
        for x in range(self.size):
            for y in range(self.size):
                if self.board[x][y] == -1:
                    continue
                count = 0
                for dx in [-1, 0, 1]:
                    for dy in [-1, 0, 1]:
                        if dx == 0 and dy == 0:
                            continue
                        nx, ny = x + dx, y + dy
                        if 0 <= nx < self.size and 0 <= ny < self.size:
                            if self.board[nx][ny] == -1:
                                count += 1
                self.board[x][y] = count

        # Create buttons
        for x in range(self.size):
            for y in range(self.size):
                btn = tk.Button(self.frame, width=3, height=1,
                                command=lambda x=x, y=y: self.click(x, y))
                btn.bind("<Button-3>", lambda e, x=x, y=y: self.flag(x, y))
                btn.grid(row=x, column=y)
                self.buttons[(x, y)] = btn

        # AI Button
        self.ai_btn = tk.Button(self.root, text="AI Move", command=self.run_ai_until_done)
        self.ai_btn.pack()

        # Reset Button
        restart_btn = tk.Button(self.root, text="Play Again", command=self.restart)
        restart_btn.pack()

    def click(self, x, y):
        # Skip if flagged
        if (x, y) in self.flags:
            return

        # Mine hit
        if self.board[x][y] == -1:
            self.buttons[(x, y)].config(text="M", bg="red")
            messagebox.showerror("Game Over", "You hit a mine!")
            return

        # Reveal cell
        self.reveal(x, y)
        self.check_win()

    def flag(self, x, y):
        # Toggle flag on right click
        btn = self.buttons[(x, y)]
        if btn["text"] == " " and len(self.flags) < self.mines:
            btn.config(text="F", bg="yellow")
            self.flags.add((x, y))
        elif btn["text"] == "F":
            btn.config(text=" ", bg="SystemButtonFace")
            self.flags.remove((x, y))

    def reveal(self, x, y):
        if (x, y) in self.revealed:
            return

        self.revealed.add((x, y))
        btn = self.buttons[(x, y)]
        value = self.board[x][y]
        btn.config(text=str(value), bg="lightgray")

        self.ai.add_knowledge((x, y), value)

        # Auto-reveal surrounding if empty
        if value == 0:
            for dx in [-1, 0, 1]:
                for dy in [-1, 0, 1]:
                    if dx == 0 and dy == 0:
                        continue
                    nx, ny = x + dx, y + dy
                    if 0 <= nx < self.size and 0 <= ny < self.size:
                        self.reveal(nx, ny)

    def ai_move(self):
        move = self.ai.next_move()
        if move:
            self.click(*move)
        else:
            messagebox.showinfo("AI", "No safe moves left. Might need to guess.")
        self.check_win()

    def run_ai_until_done(self):
        while True:
            move = self.ai.next_move()
            if move:
                self.click(*move)
                self.root.update()
                time.sleep(0.05)  # Small delay for animation
            else:
                break
        self.check_win()

    def check_win(self):
        if len(self.revealed) == self.size * self.size - self.mines:
            elapsed = round(time.time() - self.start_time, 2)
            messagebox.showinfo("Victory!", f"You win in {elapsed} seconds!")

    def restart(self):
        self.frame.destroy()
        for widget in self.root.winfo_children():
            if isinstance(widget, tk.Button):
                widget.destroy()
        self.reset_game()

# Start the game
if __name__ == '__main__':
    root = tk.Tk()
    game = Minesweeper(root)
    root.mainloop()
