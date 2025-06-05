import tkinter as tk
from tkinter import messagebox
import random
import time
import pygame

# --- FUNZIONI ORIGINALI ---
SYMBOL = "☐"
FLOWER_SYMBOL = "❀"

def add_mines(n_mines, field):
    if n_mines > len(field) * len(field):
        raise Exception("Error: Mines number must be less than matrix cells")
    cont_mines = 0
    mines_pos = []
    while cont_mines < n_mines:
        x = random.randint(0, len(field) - 1)
        y = random.randint(0, len(field) - 1)
        if (x, y) not in mines_pos:
            cont_mines += 1
            mines_pos.append((x, y))
    return mines_pos

def gen_matrix(dim):
    ghost = []
    zero_matrix = []
    for i in range(dim):
        ghost_row = []
        zero_row = []
        for y in range(dim):
            ghost_row.append(SYMBOL)
            zero_row.append(0)
        ghost.append(ghost_row)
        zero_matrix.append(zero_row)
    return ghost, zero_matrix

def adj_coords(x, y, dim):
    adj_list = []
    for i in range(x - 1, x + 2):
        for j in range(y - 1, y + 2):
            if (0 <= i < dim) and (0 <= j < dim) and ((i != x) or (j != y)):
                adj_list.append((i, j))
    return adj_list

def gen_adjpos_mat(m_list, zero):
    for (x, y) in m_list:
        zero[x][y] = -1
        adj_list = adj_coords(x, y, len(zero))
        for (x1, y1) in adj_list:
            if (x1, y1) not in m_list:
                zero[x1][y1] += 1
    return zero

# --- GUI ---
class MinesweeperGUI:
    def __init__(self, root, dim, mines):
        self.root = root
        self.dim = dim
        self.mines_num = mines
        self.flags_left = mines
        self.ghost, self.zero = gen_matrix(dim)
        self.mines = add_mines(mines, self.ghost)
        self.zero = gen_adjpos_mat(self.mines, self.zero)
        self.revealed = set()
        self.flagged = set()
        self.buttons = [[None for _ in range(dim)] for _ in range(dim)]
        self.timer_started = False
        self.start_time = 0
        self.timer_label = tk.Label(root, text="⏱ Tempo: 0 s")
        self.timer_label.grid(row=0, column=0, columnspan=dim//2)
        self.flags_label = tk.Label(root, text=f"🚩 Bandierine: {self.flags_left}")
        self.flags_label.grid(row=0, column=dim//2, columnspan=dim - dim//2)
        self.create_grid()
        self.update_timer()

    def create_grid(self):
        for i in range(self.dim):
            for j in range(self.dim):
                btn = tk.Button(self.root, text=SYMBOL, width=3, height=1)
                btn.grid(row=i + 1, column=j)  # +1 per lasciare spazio alla riga timer/bandierine
                btn.bind("<Button-1>", lambda e, x=i, y=j: self.left_click(x, y))
                btn.bind("<Button-3>", lambda e, x=i, y=j: self.right_click(x, y))
                self.buttons[i][j] = btn

    def left_click(self, x, y):
        if not self.timer_started:
            self.start_time = time.time()
            self.timer_started = True

        if (x, y) in self.flagged or (x, y) in self.revealed:
            return

        self.revealed.add((x, y))
        val = self.zero[x][y]

        if val == -1:
            self.buttons[x][y].config(text="💣", bg="red", disabledforeground="black")
            self.end_game(False)
        elif val == 0:
            self.buttons[x][y].config(text=FLOWER_SYMBOL, state="disabled", disabledforeground="green")
            for (i, j) in adj_coords(x, y, self.dim):
                self.left_click(i, j)
        else:
            self.buttons[x][y].config(text=str(val), state="disabled", disabledforeground="blue")

        self.buttons[x][y].config(relief=tk.SUNKEN)

        if len(self.revealed) == self.dim**2 - self.mines_num:
            self.end_game(True)

    def right_click(self, x, y):
        if (x, y) in self.revealed:
            return

        current_text = self.buttons[x][y]["text"]
        if current_text == "🚩":
            self.buttons[x][y].config(text=SYMBOL)
            self.flags_left += 1
            self.flagged.remove((x, y))
        else:
            if self.flags_left == 0:
                return
            self.buttons[x][y].config(text="🚩")
            self.flags_left -= 1
            self.flagged.add((x, y))

        self.flags_label.config(text=f"🚩 Bandierine: {self.flags_left}")

    def update_timer(self):
        if self.timer_started:
            elapsed = int(time.time() - self.start_time)
            self.timer_label.config(text=f"⏱ Tempo: {elapsed} s")
        self.root.after(1000, self.update_timer)

    def end_game(self, win):
        for (x, y) in self.mines:
            if (x, y) not in self.revealed:
                self.buttons[x][y].config(text="💣", bg="gray", disabledforeground="black")
        msg = "Hai vinto! 🎉" if win else "Hai perso! 💥"
        messagebox.showinfo("Risultato", msg)
        self.root.quit()

# --- MUSIC SETUP ---
def start_music():
    try:
        pygame.mixer.init()
        pygame.mixer.music.load("musica.mp3")
        pygame.mixer.music.play(-1)  # loop infinito
    except Exception as e:
        print("Errore nella riproduzione della musica:", e)

# --- MENU DI SELEZIONE DIFFICOLTÀ ---
def start_menu():
    menu = tk.Tk()
    menu.title("Seleziona difficoltà")

    def start_game(dim, mines):
        menu.destroy()
        root = tk.Tk()
        root.title("Prato Fiorito")
        start_music()
        MinesweeperGUI(root, dim, mines)
        root.mainloop()

    tk.Label(menu, text="Scegli la difficoltà:").pack(pady=10)

    tk.Button(menu, text="Facile (8x8, 10 mine)", width=30,
              command=lambda: start_game(8, 10)).pack(pady=5)
    tk.Button(menu, text="Medio (12x12, 20 mine)", width=30,
              command=lambda: start_game(12, 20)).pack(pady=5)
    tk.Button(menu, text="Difficile (16x16, 40 mine)", width=30,
              command=lambda: start_game(16, 40)).pack(pady=5)

    menu.mainloop()

# --- AVVIO ---
if __name__ == "__main__":
    start_menu()
