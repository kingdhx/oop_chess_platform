from __future__ import annotations

from typing import Optional

from .exceptions import GameError, InvalidCommandError
from .factory import GameFactory
from .storage import SaveManager


class GameController:
    def __init__(self):
        self.game = None
        self.save_manager = SaveManager()

    def start_game(self, game_type: str, size: int) -> str:
        self.game = GameFactory.create(game_type, size)
        return f"已开始 {self.game.name}，棋盘大小 {size}x{size}。黑方先行。"

    def execute(self, command_line: str) -> str:
        parts = command_line.strip().split()
        if not parts:
            raise InvalidCommandError("请输入有效指令。")
        cmd = parts[0].lower()

        if cmd == "start":
            if len(parts) != 3:
                raise InvalidCommandError("开始指令格式：start <gomoku/go> <size>")
            return self.start_game(parts[1], int(parts[2]))

        if cmd == "quit":
            return "quit"

        if self.game is None:
            raise InvalidCommandError("当前没有进行中的游戏，请先使用 start 指令开始游戏。")

        if cmd == "place":
            if len(parts) != 3:
                raise InvalidCommandError("落子指令格式：place <row> <col>")
            return self.game.place(int(parts[1]) - 1, int(parts[2]) - 1)
        if cmd == "pass":
            return self.game.pass_turn()
        if cmd == "undo":
            return self.game.undo()
        if cmd == "resign":
            return self.game.resign()
        if cmd == "save":
            if len(parts) != 2:
                raise InvalidCommandError("保存指令格式：save <file>")
            return self.save_manager.save(self.game, parts[1])
        if cmd == "load":
            if len(parts) != 2:
                raise InvalidCommandError("读取指令格式：load <file>")
            self.game = self.save_manager.load(parts[1])
            return f"已从 {parts[1]} 读取局面。"
        if cmd == "help":
            self.game.help_visible = True
            return "已显示帮助提示。"
        if cmd == "hidehelp":
            self.game.help_visible = False
            return "已隐藏帮助提示。"
        if cmd == "status":
            return self.game.get_status()

        raise InvalidCommandError("不合法的指令，请检查输入。")

    def render_board(self) -> str:
        if self.game is None:
            return "当前未开始游戏。\n请输入：start <gomoku/go> <size>"
        header = "   " + " ".join(f"{i+1:2d}" for i in range(self.game.size))
        rows = [header]
        for idx, row in enumerate(self.game.board.grid):
            rows.append(f"{idx+1:2d} " + " ".join(f" {cell.display}" for cell in row))
        return "\n".join(rows)

    def help_text(self) -> str:
        if self.game is None or self.game.help_visible:
            return (
                "可用指令：\n"
                "start <gomoku/go> <size>  开始游戏\n"
                "place <row> <col>         在指定位置落子\n"
                "pass                      围棋虚着\n"
                "undo                      悔棋一步（默认最多 3 次）\n"
                "resign                    投子认负\n"
                "save <file>               保存局面\n"
                "load <file>               读取局面\n"
                "status                    查看状态\n"
                "help / hidehelp           显示或隐藏帮助\n"
                "quit                      退出程序"
            )
        return ""
