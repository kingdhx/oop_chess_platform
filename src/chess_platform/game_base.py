from __future__ import annotations

from abc import ABC, abstractmethod
from typing import List, Optional

from .board import Board
from .exceptions import InvalidMoveError
from .models import GameSnapshot, Move, Stone


class AbstractBoardGame(ABC):
    name = "AbstractGame"
    supports_pass = False

    def __init__(self, size: int, undo_limit: int = 3):
        if not 8 <= size <= 19:
            raise InvalidMoveError("棋盘大小必须在 8 到 19 之间。")
        self.size = size
        self.board = Board(size)
        self.current_player = Stone.BLACK
        self.winner: Optional[Stone] = None
        self.game_over = False
        self.message = "游戏已开始。"
        self.help_visible = True
        self.move_history: List[Move] = []
        self.undo_limit = undo_limit
        self.undo_count = 0

    def toggle_help(self) -> str:
        self.help_visible = not self.help_visible
        return "已显示帮助。" if self.help_visible else "已隐藏帮助。"

    def ensure_active(self) -> None:
        if self.game_over:
            raise InvalidMoveError("当前对局已经结束，请重新开始游戏。")

    def switch_player(self) -> None:
        self.current_player = self.current_player.opponent

    def place(self, row: int, col: int) -> str:
        self.ensure_active()
        if not self.board.is_on_board(row, col):
            raise InvalidMoveError("落子位置超出棋盘范围。")
        if self.board.get(row, col) != Stone.EMPTY:
            raise InvalidMoveError("该位置已有棋子，不能重复落子。")
        msg = self._place_internal(row, col)
        if not self.game_over:
            self.switch_player()
        return msg

    def pass_turn(self) -> str:
        raise InvalidMoveError("当前游戏不支持虚着。")

    def resign(self) -> str:
        self.ensure_active()
        self.game_over = True
        self.winner = self.current_player.opponent
        self.move_history.append(Move(self.current_player, -1, -1, action="resign"))
        return f"{self.current_player.display} 方已认输，{self.winner.display} 方获胜。"

    def undo(self) -> str:
        if not self.move_history:
            raise InvalidMoveError("当前没有可悔的棋步。")
        if self.undo_count >= self.undo_limit:
            raise InvalidMoveError(f"悔棋次数超过限制，当前最多允许悔棋 {self.undo_limit} 次。")
        self._undo_internal()
        self.undo_count += 1
        self.game_over = False
        self.winner = None
        return "已悔棋一步。"

    @abstractmethod
    def _place_internal(self, row: int, col: int) -> str:
        raise NotImplementedError

    @abstractmethod
    def _undo_internal(self) -> None:
        raise NotImplementedError

    @abstractmethod
    def get_status(self) -> str:
        raise NotImplementedError

    @abstractmethod
    def to_snapshot(self) -> GameSnapshot:
        raise NotImplementedError

    @classmethod
    @abstractmethod
    def from_snapshot(cls, snapshot: GameSnapshot) -> "AbstractBoardGame":
        raise NotImplementedError
