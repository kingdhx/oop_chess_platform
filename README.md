# 棋类对战平台课程大作业

本项目实现了五子棋与围棋的双人对战平台，包含命令行版本和 Tkinter 图形界面版本。

## 运行方式

```bash
pip install -r requirements.txt  # 如无特殊环境可直接跳过
export PYTHONPATH=./src
python main.py        # 命令行版本
python gui_main.py    # 图形界面版本
```

Windows PowerShell 可用：

```powershell
$env:PYTHONPATH="./src"
python main.py
python gui_main.py
```

## 已实现功能

- 五子棋双人对战，自动判断五连胜负与平局
- 围棋双人对战，支持提子、虚着、禁入自杀、简单劫争/重复局面限制、终局计分
- 统一命令行指令：开始、重开、落子、虚着、悔棋、认输、保存、读取、显示/隐藏帮助
- JSON 存档与读档
- 后端逻辑与前端交互分离
- 采用工厂、策略化规则封装、命令解析、建造者、单例存档等设计模式
- 提供基础单元测试

## 目录结构

```text
src/chess_platform/
  board.py
  models.py
  game_base.py
  gomoku.py
  go_game.py
  factory.py
  storage.py
  controller.py
  ui_builders.py
  cli.py
  gui.py
tests/test_basic.py
main.py
gui_main.py
```
