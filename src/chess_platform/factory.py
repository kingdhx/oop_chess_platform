from __future__ import annotations

from .go_game import GoGame
from .gomoku import GomokuGame


class GameFactory:
    @staticmethod
    def create(game_type: str, size: int):
        normalized = game_type.strip().lower()
        if normalized in {"gomoku", "wuziqi", "五子棋", "1"}:
            return GomokuGame(size)
        if normalized in {"go", "weiqi", "围棋", "2"}:
            return GoGame(size)
        raise ValueError("不支持的游戏类型，请选择 Gomoku/五子棋 或 Go/围棋。")
