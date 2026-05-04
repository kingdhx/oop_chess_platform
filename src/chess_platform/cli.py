from __future__ import annotations

from .controller import GameController
from .exceptions import GameError
from .ui_builders import ConsoleUIBuilder, UIDirector


class ConsoleClient:
    def __init__(self):
        self.controller = GameController()
        product = UIDirector(ConsoleUIBuilder()).construct()
        self.title = product.title

    def run(self) -> None:
        print(f"=== {self.title} ===")
        print("输入 help 查看提示。")
        while True:
            print()
            print(self.controller.render_board())
            help_text = self.controller.help_text()
            if help_text:
                print(help_text)
            command = input("\n请输入指令：").strip()
            try:
                result = self.controller.execute(command)
                if result == "quit":
                    print("程序已退出。")
                    break
                print(result)
                if self.controller.game is not None:
                    print(self.controller.game.get_status())
            except GameError as exc:
                print(f"错误：{exc}")
            except Exception as exc:
                print(f"系统异常：{exc}")
