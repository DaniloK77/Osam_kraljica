import random
import tkinter as tk

N = 8               # veličina table i broj kraljica
MAX_SIDEWAYS = 100  # dozvoljeni broj uzastopnih sporednih poteza
RUNS = 200          # broj realizacija za statistiku
SQUARE = 72         # veličina jednog polja u pikselima
DELAY_MS = 700      # pauza između dva poteza u animaciji (milisekunde)


def random_state():
    state = []
    for col in range(N):
        state.append(random.randrange(N))
    return state


def attack(state, i, j):
    same_row = state[i] == state[j]
    same_diagonal = abs(state[i] - state[j]) == abs(i - j)
    return same_row or same_diagonal


def h(state):
    count = 0
    for i in range(N):
        for j in range(i + 1, N):
            if attack(state, i, j):
                count += 1
    return count


def is_attacked(state, col):
    for other in range(N):
        if other != col and attack(state, col, other):
            return True
    return False


def move_queen(state, col, row):
    new_state = state.copy()
    new_state[col] = row
    return new_state


def neighbor_costs(state):
    costs = {}
    for col in range(N):
        for row in range(N):
            if row != state[col]:
                costs[(col, row)] = h(move_queen(state, col, row))
    return costs


def hill_climbing(state, max_sideways=MAX_SIDEWAYS):
    path = [state]
    current = h(state)
    sideways = 0

    while current > 0:
        costs = neighbor_costs(state)
        best = min(costs.values())
        if best > current:
            break
        elif best == current:
            sideways += 1
            if sideways > max_sideways:
                break
        else:
            sideways = 0

        best_moves = []
        for move, cost in costs.items():
            if cost == best:
                best_moves.append(move)
        col, row = random.choice(best_moves)
        state = move_queen(state, col, row)
        current = best
        path.append(state)
    return path


def average(numbers):
    return f"{sum(numbers) / len(numbers):.2f}" if numbers else "-"


def statistics(max_sideways):
    solved_moves = []
    failed_moves = []
    for _ in range(RUNS):
        path = hill_climbing(random_state(), max_sideways)
        moves = len(path) - 1
        if h(path[-1]) == 0:
            solved_moves.append(moves)
        else:
            failed_moves.append(moves)
    success_rate = 100 * len(solved_moves) / RUNS
    print(f"Planinarenje sa najviše {max_sideways} sporednih poteza ({RUNS} realizacija)")
    print(f"  uspješnih realizacija:                    "
          f"{len(solved_moves)} / {RUNS} ({success_rate:.1f} %)")
    print(f"  prosječan broj poteza do tačnog rješenja: {average(solved_moves)}")
    print(f"  prosječan broj poteza kod neuspjeha:      {average(failed_moves)}\n")


class Animation:

    def __init__(self, root):
        self.root = root
        root.title("Osam kraljica - planinarenje")
        self.canvas = tk.Canvas(root, width=N * SQUARE, height=N * SQUARE, highlightthickness=0)
        self.canvas.pack(padx=16, pady=(16, 8))
        self.label = tk.Label(root, font="Helvetica 15")
        self.label.pack()
        tk.Label(root, text="Broj na polju: h kada bi se kraljica iz te kolone pomjerila tu.\n"
                            "Zeleno: najbolji potezi. Žuto: posljednji potez. "
                            "Crveno: napadnuta kraljica.").pack(pady=4)
        tk.Button(root, text="Novo pokretanje", command=self.new_run).pack(pady=(4, 16))
        self.job = None
        self.new_run()

    def new_run(self):
        if self.job is not None:
            self.root.after_cancel(self.job)
        self.path = hill_climbing(random_state())
        self.show(0)

    def show(self, step):
        state = self.path[step]
        previous = self.path[step - 1] if step > 0 else state
        last_step = len(self.path) - 1
        self.draw_board(state, previous, show_costs=step < last_step)

        text = f"Potez {step} / {last_step}:  h = {h(state)}"
        if step > 0 and h(state) == h(previous):
            text += "  (sporedni potez)"
        if step == last_step:
            text += "  -  RJEŠENJE" if h(state) == 0 else "  -  zaglavio se, nema rješenja"
        self.label.config(text=text)
        if step < last_step:
            self.job = self.root.after(DELAY_MS, self.show, step + 1)

    def draw_board(self, state, previous, show_costs):
        canvas = self.canvas
        canvas.delete("all")
        costs = neighbor_costs(state) if show_costs else {}
        best = min(costs.values()) if costs else None

        for col in range(N):
            for row in range(N):
                if state[col] == row and previous[col] != row:
                    color = "#f5d132"
                elif previous[col] == row and state[col] != row:
                    color = "#f7ec9e"
                elif (col + row) % 2 == 0:
                    color = "#f0d9b5"
                else:
                    color = "#c9a27e"
                x, y = col * SQUARE, row * SQUARE
                cx, cy = x + SQUARE / 2, y + SQUARE / 2
                canvas.create_rectangle(x, y, x + SQUARE, y + SQUARE, fill=color, width=0)
                if state[col] == row:
                    queen_color = "#b3261e" if is_attacked(state, col) else "#1b1b1b"
                    canvas.create_text(cx, cy, text="♛", font="Helvetica 42", fill=queen_color)
                elif (col, row) in costs and costs[(col, row)] == best:
                    canvas.create_oval(cx - 15, cy - 15, cx + 15, cy + 15, fill="#1e7d32", width=0)
                    canvas.create_text(cx, cy, text=best, fill="white", font="Helvetica 13 bold")
                elif (col, row) in costs:
                    canvas.create_text(cx, cy, text=costs[(col, row)], font="Helvetica 13")


if __name__ == "__main__":
    statistics(max_sideways=0)
    statistics(max_sideways=MAX_SIDEWAYS)
    root = tk.Tk()
    Animation(root)
    root.mainloop()
