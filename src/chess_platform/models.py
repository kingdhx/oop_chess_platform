from __future__ import annotations

from dataclasses import dataclass, field
from enum import Enum
from typing import List, Optional, Tuple

Position = Tuple[int, int]


class Stone(str, Enum):
    EMPTY = "."
    BLACK = "B"
    WHITE = "W"

    @property
    def opponent(self) -> "Stone":
        if self == Stone.BLACK:
            return Stone.WHITE
        if self == Stone.WHITE:
            return Stone.BLACK
        return Stone.EMPTY

    @property
    def display(self) -> str:
        return {Stone.EMPTY: ".", Stone.BLACK: "●", Stone.WHITE: "○"}[self]


@dataclass
class Move:
    player: Stone
    row: int
    col: int
    action: str = "place"  # place/pass/resign
    captured: List[Position] = field(default_factory=list)


@dataclass
class GameSnapshot:
    game_type: str
    size: int
    board: List[List[str]]
    current_player: str
    winner: Optional[str]
    game_over: bool
    message: str
    help_visible: bool
    moves: List[dict]
    passes_in_a_row: int = 0
    undo_count: int = 0
    ko_forbidden: Optional[Position] = None
    board_hash_history: List[str] = field(default_factory=list)
