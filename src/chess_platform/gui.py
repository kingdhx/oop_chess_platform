from __future__ import annotations

import tkinter as tk
from tkinter import filedialog, messagebox, scrolledtext, ttk

from .controller import GameController
from .exceptions import GameError
from .models import Stone
from .ui_builders import GUIUIBuilder, UIDirector


class GameGUI:
    CELL_SIZE = 28
    PADDING = 30

    def __init__(self):
        self.controller = GameController()
        product = UIDirector(GUIUIBuilder()).construct()
        self.root = tk.Tk()
        self.root.title(product.title)
        self.current_size = 9
        self.current_type = tk.StringVar(value="gomoku")
        self.help_visible = tk.BooleanVar(value=True)

        self._build_layout(product.help_text)
        self._draw_empty_board(self.current_size)

    def _build_layout(self, help_text: str) -> None:
        top = ttk.Frame(self.root, padding=8)
        top.pack(fill=tk.X)

        ttk.Label(top, text="游戏类型").pack(side=tk.LEFT)
        ttk.Combobox(top, textvariable=self.current_type, values=["gomoku", "go"], width=10, state="readonly").pack(side=tk.LEFT, padx=5)
        ttk.Label(top, text="棋盘大小").pack(side=tk.LEFT)
        self.size_spin = tk.Spinbox(top, from_=8, to=19, width=5)
        self.size_spin.delete(0, tk.END)
        self.size_spin.insert(0, "9")
        self.size_spin.pack(side=tk.LEFT, padx=5)
        ttk.Button(top, text="开始/重开", command=self.start_game).pack(side=tk.LEFT, padx=5)
        ttk.Button(top, text="悔棋", command=lambda: self.safe_action("undo")).pack(side=tk.LEFT, padx=5)
        ttk.Button(top, text="虚着", command=lambda: self.safe_action("pass")).pack(side=tk.LEFT, padx=5)
        ttk.Button(top, text="认输", command=lambda: self.safe_action("resign")).pack(side=tk.LEFT, padx=5)
        ttk.Button(top, text="保存", command=self.save_game).pack(side=tk.LEFT, padx=5)
        ttk.Button(top, text="读取", command=self.load_game).pack(side=tk.LEFT, padx=5)
        ttk.Checkbutton(top, text="显示帮助", variable=self.help_visible, command=self.toggle_help).pack(side=tk.LEFT, padx=8)

        body = ttk.Frame(self.root, padding=8)
        body.pack(fill=tk.BOTH, expand=True)

        self.canvas = tk.Canvas(body, width=600, height=600, bg="#d9b46b")
        self.canvas.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)
        self.canvas.bind("<Button-1>", self.on_canvas_click)

        right = ttk.Frame(body)
        right.pack(side=tk.RIGHT, fill=tk.BOTH)
        self.status_var = tk.StringVar(value="请先开始游戏。")
        ttk.Label(right, textvariable=self.status_var, wraplength=280).pack(fill=tk.X, pady=4)
        self.help_label = ttk.Label(right, text=help_text, wraplength=280, justify=tk.LEFT)
        self.help_label.pack(fill=tk.X, pady=4)
        self.log = scrolledtext.ScrolledText(right, width=36, height=24, state="disabled")
        self.log.pack(fill=tk.BOTH, expand=True)

    def log_message(self, text: str) -> None:
        self.log.configure(state="normal")
        self.log.insert(tk.END, text + "\n")
        self.log.see(tk.END)
        self.log.configure(state="disabled")

    def toggle_help(self) -> None:
        if self.help_visible.get():
            self.help_label.pack(fill=tk.X, pady=4)
        else:
            self.help_label.pack_forget()

    def _draw_empty_board(self, size: int) -> None:
        self.canvas.delete("all")
        canvas_size = self.PADDING * 2 + self.CELL_SIZE * (size - 1)
        self.canvas.config(width=canvas_size, height=canvas_size)
        for i in range(size):
            x0 = self.PADDING + i * self.CELL_SIZE
            self.canvas.create_line(self.PADDING, x0, self.PADDING + self.CELL_SIZE * (size - 1), x0)
            self.canvas.create_line(x0, self.PADDING, x0, self.PADDING + self.CELL_SIZE * (size - 1))

    def redraw(self) -> None:
        if self.controller.game is None:
            return
        game = self.controller.game
        self._draw_empty_board(game.size)
        for r in range(game.size):
            for c in range(game.size):
                stone = game.board.get(r, c)
                if stone == Stone.EMPTY:
                    continue
                x = self.PADDING + c * self.CELL_SIZE
                y = self.PADDING + r * self.CELL_SIZE
                radius = self.CELL_SIZE // 2 - 2
                fill = "black" if stone == Stone.BLACK else "white"
                self.canvas.create_oval(x - radius, y - radius, x + radius, y + radius, fill=fill)
        self.status_var.set(game.get_status())

    def start_game(self) -> None:
        try:
            size = int(self.size_spin.get())
            result = self.controller.start_game(self.current_type.get(), size)
            self.log_message(result)
            self.redraw()
        except Exception as exc:
            messagebox.showerror("错误", str(exc))

    def safe_action(self, command: str) -> None:
        try:
            result = self.controller.execute(command)
            if result != "quit":
                self.log_message(result)
            self.redraw()
        except GameError as exc:
            messagebox.showwarning("提示", str(exc))

    def on_canvas_click(self, event) -> None:
        if self.controller.game is None:
            messagebox.showinfo("提示", "请先开始游戏。")
            return
        col = round((event.x - self.PADDING) / self.CELL_SIZE)
        row = round((event.y - self.PADDING) / self.CELL_SIZE)
        if not self.controller.game.board.is_on_board(row, col):
            return
        try:
            # GUI 统一通过 Controller 下发指令。正常情况下，game.place() 内部会自动换手。
            # 这里保留一个保护判断：如果执行落子后玩家没有变化，则补一次换手，
            # 避免不同入口调用导致 GUI 中一直显示同一方落子。
            before_player = self.controller.game.current_player
            result = self.controller.execute(f"place {row + 1} {col + 1}")
            if (
                self.controller.game is not None
                and not self.controller.game.game_over
                and self.controller.game.current_player == before_player
            ):
                self.controller.game.switch_player()
            self.log_message(result)
            self.redraw()
        except GameError as exc:
            messagebox.showwarning("落子失败", str(exc))

    def save_game(self) -> None:
        if self.controller.game is None:
            messagebox.showinfo("提示", "当前没有可保存的局面。")
            return
        file_path = filedialog.asksaveasfilename(defaultextension=".json", filetypes=[("JSON", "*.json")])
        if not file_path:
            return
        try:
            message = self.controller.save_manager.save(self.controller.game, file_path)
            self.log_message(message)
        except GameError as exc:
            messagebox.showerror("保存失败", str(exc))

    def load_game(self) -> None:
        file_path = filedialog.askopenfilename(filetypes=[("JSON", "*.json")])
        if not file_path:
            return
        try:
            self.controller.game = self.controller.save_manager.load(file_path)
            self.log_message(f"已读取局面：{file_path}")
            self.redraw()
        except GameError as exc:
            messagebox.showerror("读取失败", str(exc))

    def run(self) -> None:
        self.root.mainloop()
