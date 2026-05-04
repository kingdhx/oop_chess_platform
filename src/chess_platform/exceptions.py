class GameError(Exception):
    """Base error for game-related exceptions."""


class InvalidCommandError(GameError):
    pass


class InvalidMoveError(GameError):
    pass


class SaveLoadError(GameError):
    pass
