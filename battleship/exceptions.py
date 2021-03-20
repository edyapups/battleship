# Board errors

class BoardError(Exception):
    pass


class MoveError(BoardError):
    pass


class PlacementError(BoardError):
    pass


# Player errors

class PlayerError(Exception):
    pass


class QuitSignal(PlayerError):
    QUIT = 'q'
    QUIT_AND_SAVE = 'qs'
    BACK_TO_MAIN_MENU = 'btmms'

    def __init__(self, *args: object, signal_type: str) -> None:
        super().__init__(*args)
        self.signal_type = signal_type


# Game errors

class GameError(Exception):
    pass


class GameIsEnded(GameError):
    pass
