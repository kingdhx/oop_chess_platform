from __future__ import annotations

from collections import deque
from typing import Dict, List, Optional, Set, Tuple

from .board import Board
from .exceptions import InvalidMoveError
from .game_base import AbstractBoardGame
from .models import GameSnapshot, Move, Position, Stone


class GoGame(AbstractBoardGame):
    name = "Go"
    supports_pass = True

    def __init__(self, size: int, undo_limit: int = 3, komi: float = 7.5):
        super().__init__(size, undo_limit)
        self.komi = komi
        self.passes_in_a_row = 0
        self.ko_forbidden: Optional[Position] = None
        self.board_hash_history: List[str] = [self.board.board_hash()]

    def _try_place_and_capture(self, row: int, col: int, player: Stone) -> Tuple[Board, List[Position]]:
        temp = self.board.clone()
        temp.set(row, col, player)
        captured: List[Position] = []
        for nr, nc in temp.neighbors(row, col):
            if temp.get(nr, nc) == player.opponent:
                group = temp.connected_group(nr, nc)
                if not temp.liberties(group):
                    captured.extend(temp.remove_group(group))

        own_group = temp.connected_group(row, col)
        if not temp.liberties(own_group):
            raise InvalidMoveError("该步为自杀，不合法。")
        return temp, captured

    def _place_internal(self, row: int, col: int) -> str:
        if self.ko_forbidden == (row, col):
            raise InvalidMoveError("该位置受到劫争限制，本手不能落子。")

        temp, captured = self._try_place_and_capture(row, col, self.current_player)
        next_hash = temp.board_hash()
        if next_hash in self.board_hash_history:
            raise InvalidMoveError("该步会重复历史局面，不合法。")

        self.board = temp
        self.passes_in_a_row = 0
        self.ko_forbidden = captured[0] if len(captured) == 1 else None
        move = Move(self.current_player, row, col, action="place", captured=captured)
        self.move_history.append(move)
        self.board_hash_history.append(next_hash)

        if captured:
            return f"{self.current_player.display} 方在 ({row + 1}, {col + 1}) 落子，提走 {len(captured)} 子。"
        return f"{self.current_player.display} 方在 ({row + 1}, {col + 1}) 落子。"

    def pass_turn(self) -> str:
        self.ensure_active()
        self.move_history.append(Move(self.current_player, -1, -1, action="pass"))
        self.passes_in_a_row += 1
        self.ko_forbidden = None
        if self.passes_in_a_row >= 2:
            self.game_over = True
            black_score, white_score = self.compute_score()
            if black_score > white_score:
                self.winner = Stone.BLACK
            elif white_score > black_score:
                self.winner = Stone.WHITE
            else:
                self.winner = None
            return f"双方连续虚着，围棋终局。黑方 {black_score:.1f}，白方 {white_score:.1f}。"
        current = self.current_player
        self.switch_player()
        return f"{current.display} 方选择虚着。现在轮到 {self.current_player.display} 方。"

    def _undo_internal(self) -> None:
        last = self.move_history.pop()
        self.current_player = last.player
        self.game_over = False
        self.winner = None
        if last.action == "place":
            self.board.set(last.row, last.col, Stone.EMPTY)
            for r, c in last.captured:
                self.board.set(r, c, last.player.opponent)
            self.passes_in_a_row = 0
            if self.board_hash_history:
                self.board_hash_history.pop()
            self.ko_forbidden = None
        elif last.action == "pass":
            self.passes_in_a_row = max(0, self.passes_in_a_row - 1)
        elif last.action == "resign":
            pass

    def _territory_owner(self, region: Set[Position]) -> Optional[Stone]:
        neighbors: Set[Stone] = set()
        for row, col in region:
            for nr, nc in self.board.neighbors(row, col):
                color = self.board.get(nr, nc)
                if color != Stone.EMPTY:
                    neighbors.add(color)
        if len(neighbors) == 1:
            return next(iter(neighbors))
        return None

    def compute_score(self) -> Tuple[float, float]:
        black = 0.0
        white = self.komi
        visited: Set[Position] = set()

        for r in range(self.size):
            for c in range(self.size):
                cell = self.board.get(r, c)
                if cell == Stone.BLACK:
                    black += 1
                elif cell == Stone.WHITE:
                    white += 1
                elif (r, c) not in visited:
                    region: Set[Position] = set()
                    q = deque([(r, c)])
                    while q:
                        cur = q.popleft()
                        if cur in visited:
                            continue
                        visited.add(cur)
                        region.add(cur)
                        for nxt in self.board.neighbors(*cur):
                            if self.board.get(*nxt) == Stone.EMPTY and nxt not in visited:
                                q.append(nxt)
                    owner = self._territory_owner(region)
                    if owner == Stone.BLACK:
                        black += len(region)
                    elif owner == Stone.WHITE:
                        white += len(region)
        return black, white

    def get_status(self) -> str:
        if self.game_over:
            black_score, white_score = self.compute_score()
            if self.winner is None:
                return f"围棋结束：平局。黑 {black_score:.1f}，白 {white_score:.1f}。"
            return f"围棋结束：{self.winner.display} 方获胜。黑 {black_score:.1f}，白 {white_score:.1f}。"
        return f"围棋进行中，轮到 {self.current_player.display} 方。连续虚着 {self.passes_in_a_row} 次。"

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
            passes_in_a_row=self.passes_in_a_row,
            undo_count=self.undo_count,
            ko_forbidden=self.ko_forbidden,
            board_hash_history=self.board_hash_history,
        )

    @classmethod
    def from_snapshot(cls, snapshot: GameSnapshot) -> "GoGame":
        game = cls(snapshot.size)
        game.board = Board.deserialize(snapshot.board)
        game.current_player = Stone(snapshot.current_player)
        game.winner = Stone(snapshot.winner) if snapshot.winner else None
        game.game_over = snapshot.game_over
        game.message = snapshot.message
        game.help_visible = snapshot.help_visible
        game.move_history = [Move(**move) for move in snapshot.moves]
        game.passes_in_a_row = snapshot.passes_in_a_row
        game.undo_count = snapshot.undo_count
        game.ko_forbidden = tuple(snapshot.ko_forbidden) if snapshot.ko_forbidden else None
        game.board_hash_history = snapshot.board_hash_history or [game.board.board_hash()]
        return game
