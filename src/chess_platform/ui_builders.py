from __future__ import annotations

from abc import ABC, abstractmethod
from dataclasses import dataclass, field
from typing import List


@dataclass
class UIProduct:
    title: str = ""
    components: List[str] = field(default_factory=list)
    help_text: str = ""


class AbstractUIBuilder(ABC):
    def __init__(self):
        self.product = UIProduct()

    @abstractmethod
    def build_title(self) -> None:
        raise NotImplementedError

    @abstractmethod
    def build_components(self) -> None:
        raise NotImplementedError

    @abstractmethod
    def build_help(self) -> None:
        raise NotImplementedError

    def get_result(self) -> UIProduct:
        return self.product


class ConsoleUIBuilder(AbstractUIBuilder):
    def build_title(self) -> None:
        self.product.title = "命令行棋类对战平台"

    def build_components(self) -> None:
        self.product.components = ["棋盘区", "状态区", "命令输入区", "帮助提示区"]

    def build_help(self) -> None:
        self.product.help_text = (
            "start <gomoku/go> <size> | place <row> <col> | pass | undo | resign | save <file> | load <file> | help | hidehelp | quit"
        )


class GUIUIBuilder(AbstractUIBuilder):
    def build_title(self) -> None:
        self.product.title = "图形界面棋类对战平台"

    def build_components(self) -> None:
        self.product.components = ["顶部控制栏", "棋盘画布", "状态栏", "操作按钮区", "日志显示区"]

    def build_help(self) -> None:
        self.product.help_text = "支持鼠标点击落子，按钮操作包括开始、悔棋、虚着、认输、保存、读取、显示帮助。"


class UIDirector:
    def __init__(self, builder: AbstractUIBuilder):
        self.builder = builder

    def construct(self) -> UIProduct:
        self.builder.build_title()
        self.builder.build_components()
        self.builder.build_help()
        return self.builder.get_result()
