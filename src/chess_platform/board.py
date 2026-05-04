from __future__ import annotations

from typing import Iterable, List, Set, Tuple

from .models import Position, Stone


class Board:
    def __init__(self, size: int):
        self.size = size
        self.grid: List[List[Stone]] = [[Stone.EMPTY for _ in range(size)] for _ in range(size)]

    def clone(self) -> "Board":
        new_board = Board(self.size)
        new_board.grid = [row[:] for row in self.grid]
        return new_board

    def is_on_board(self, row: int, col: int) -> bool:
        return 0 <= row < self.size and 0 <= col < self.size

    def get(self, row: int, col: int) -> Stone:
        return self.grid[row][col]

    def set(self, row: int, col: int, value: Stone) -> None:
        self.grid[row][col] = value

    def is_full(self) -> bool:
        return all(cell != Stone.EMPTY for row in self.grid for cell in row)

    def neighbors(self, row: int, col: int) -> Iterable[Position]:
        for dr, dc in ((1, 0), (-1, 0), (0, 1), (0, -1)):
            nr, nc = row + dr, col + dc
            if self.is_on_board(nr, nc):
                yield nr, nc

    def connected_group(self, row: int, col: int) -> Set[Position]:
        color = self.get(row, col)
        if color == Stone.EMPTY:
            return set()
        stack = [(row, col)]
        group: Set[Position] = set()
        while stack:
            current = stack.pop()
            if current in group:
                continue
            group.add(current)
            for nr, nc in self.neighbors(*current):
                if self.get(nr, nc) == color and (nr, nc) not in group:
                    stack.append((nr, nc))
        return group

    def liberties(self, group: Set[Position]) -> Set[Position]:
        result: Set[Position] = set()
        for row, col in group:
            for nr, nc in self.neighbors(row, col):
                if self.get(nr, nc) == Stone.EMPTY:
                    result.add((nr, nc))
        return result

    def remove_group(self, group: Set[Position]) -> List[Position]:
        removed = []
        for row, col in group:
            self.set(row, col, Stone.EMPTY)
            removed.append((row, col))
        return removed

    def serialize(self) -> List[List[str]]:
        return [[cell.value for cell in row] for row in self.grid]

    @classmethod
    def deserialize(cls, data: List[List[str]]) -> "Board":
        board = cls(len(data))
        board.grid = [[Stone(cell) for cell in row] for row in data]
        return board

    def board_hash(self) -> str:
        return "|".join("".join(cell.value for cell in row) for row in self.grid)
