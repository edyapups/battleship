from itertools import cycle
from typing import Optional, Dict

from battleship.exceptions import MoveError, GameIsEnded
from battleship.players import AbstractPlayer
from battleship.board import Board


class Game:
    def __init__(self, first_player, second_player, board_size):
        self._players = [first_player, second_player]
        self._boards: Dict[AbstractPlayer, Board] = {player: Board(*board_size) for player in self._players}
        self._players_cycle = cycle(self._players)
        self._current_player = next(self._players_cycle)
        self._next_player = next(self._players_cycle)
        self._winner: Optional[AbstractPlayer] = None

    def play(self, screen) -> AbstractPlayer:
        if self._winner:
            raise GameIsEnded(f'This game is already over, {self._winner} is the winner.')

        message = None
        while True:
            try:
                is_coup = self._make_step(screen=screen, message=message)
            except MoveError as e:
                message = str(e)
                continue

            if is_coup:
                if self._boards[self._next_player].all_ships_destroyed:
                    self._winner = self._current_player
                    return self._winner
                message = 'You hit the target!'
                continue

            message = None
            self._rotate_player()

    @property
    def winner(self):
        return self._winner

    def _rotate_player(self):
        self._current_player = self._next_player
        self._next_player = next(self._players_cycle)

    def _make_step(self, screen, message: Optional[str] = None) -> bool:
        private_board = self._boards[self._current_player].private_board
        public_board = self._boards[self._next_player].public_board

        move_coords = self._current_player.move(screen, private_board, public_board, message)
        is_coup = self._boards[self._next_player].make_move(*move_coords)

        return is_coup
