from __future__ import annotations

import json
from dataclasses import asdict
from pathlib import Path

from .exceptions import SaveLoadError
from .factory import GameFactory
from .go_game import GoGame
from .gomoku import GomokuGame
from .models import GameSnapshot


class SaveManager:
    _instance = None

    def __new__(cls):
        if cls._instance is None:
            cls._instance = super().__new__(cls)
        return cls._instance

    def save(self, game, file_path: str) -> str:
        path = Path(file_path)
        try:
            path.parent.mkdir(parents=True, exist_ok=True)
            snapshot = game.to_snapshot()
            path.write_text(json.dumps(asdict(snapshot), ensure_ascii=False, indent=2), encoding="utf-8")
            return f"局面已保存到 {path}"
        except Exception as exc:
            raise SaveLoadError(f"保存局面失败：{exc}") from exc

    def load(self, file_path: str):
        path = Path(file_path)
        try:
            data = json.loads(path.read_text(encoding="utf-8"))
            snapshot = GameSnapshot(**data)
        except Exception as exc:
            raise SaveLoadError(f"读取局面失败：{exc}") from exc

        if snapshot.game_type == "Gomoku":
            return GomokuGame.from_snapshot(snapshot)
        if snapshot.game_type == "Go":
            return GoGame.from_snapshot(snapshot)
        raise SaveLoadError("存档中的游戏类型不合法。")
