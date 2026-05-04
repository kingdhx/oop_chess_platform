from __future__ import annotations

from typing import List

from .board import Board
from .game_base import AbstractBoardGame
from .models import GameSnapshot, Move, Stone


class GomokuGame(AbstractBoardGame):
    name = "Gomoku"
    supports_pass = False

    def _count_direction(self, row: int, col: int, dr: int, dc: int) -> int:
        color = self.board.get(row, col)
        count = 1
        for sign in (1, -1):
            nr, nc = row + sign * dr, col + sign * dc
            while self.board.is_on_board(nr, nc) and self.board.get(nr, nc) == color:
                count += 1
                nr += sign * dr
                nc += sign * dc
        return count

    def _place_internal(self, row: int, col: int) -> str:
        self.board.set(row, col, self.current_player)
        move = Move(self.current_player, row, col)
        self.move_history.append(move)

        if any(self._count_direction(row, col, dr, dc) >= 5 for dr, dc in ((1, 0), (0, 1), (1, 1), (1, -1))):
            self.game_over = True
            self.winner = self.current_player
            return f"{self.current_player.display} 方连成五子，游戏结束。"

        if self.board.is_full():
            self.game_over = True
            self.winner = None
            return "棋盘已满，双方平局。"

        return f"{self.current_player.display} 方已在 ({row + 1}, {col + 1}) 落子。"

    def _undo_internal(self) -> None:
        move = self.move_history.pop()
        if move.action == "place":
            self.board.set(move.row, move.col, Stone.EMPTY)
            self.current_player = move.player
        elif move.action == "resign":
            self.current_player = move.player

    def get_status(self) -> str:
        if self.game_over:
            if self.winner is None:
                return "五子棋结束：平局。"
            return f"五子棋结束：{self.winner.display} 方获胜。"
        return f"五子棋进行中，轮到 {self.current_player.display} 方。"

    def to_snapshot(self) -> GameSnapshot:
        return GameSnapshot(
            game_type=self.name,
            size=self.size,
            board=self.board.serialize(),
            current_player=self.current_player.value,
            winner=self.winner.value if self.winner else None,
            game_over=self.game_over,
            message=self.message,
            help_visible=self.help_visible,
            moves=[move.__dict__ for move in self.move_history],
            passes_in_a_row=0,
            undo_count=self.undo_count,
            ko_forbidden=None,
            board_hash_history=[],
        )

    @classmethod
    def from_snapshot(cls, snapshot: GameSnapshot) -> "GomokuGame":
        game = cls(snapshot.size)
        game.board = Board.deserialize(snapshot.board)
        game.current_player = Stone(snapshot.current_player)
        game.winner = Stone(snapshot.winner) if snapshot.winner else None
        game.game_over = snapshot.game_over
        game.message = snapshot.message
        game.help_visible = snapshot.help_visible
        game.undo_count = snapshot.undo_count
        game.move_history = [Move(**move) for move in snapshot.moves]
        return game
