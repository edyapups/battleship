from random import randrange
from typing import Callable, Optional

from battleship.exceptions import BoardError, PlacementError, MoveError


class Board:
    def __init__(self, height, width):
        """
        :raises BoardError:
        """
        if height < 5 or width < 5:
            raise BoardError('The height and width of the board '
                             'must be greater than 5')
        self._height = height
        self._width = width
        self._shoot_map: list[list[Optional[bool], ...], ...] = [[None] * width for _ in range(height)]
        self._shoot_count = 0
        self._ship_area = 0
        self._board = [[False] * width for _ in range(height)]
        self._generate_board()

    def make_move(self, column: int, row: int) -> bool:
        """
        Applies a move to the cell at `column` and `row`.

        :raises MoveError:
        """
        if column < 0 or row < 0:
            raise MoveError('Move coordinates must be non-negative numbers.')
        if column >= self._width or row >= self._height:
            raise MoveError('Move coordinates are out of bound.')

        if self._shoot_map[row][column] is not None:
            raise MoveError('This cell has already been shot.')

        if self._board[row][column]:
            self._shoot_count += 1
            self._shoot_map[row][column] = True
            return True
        else:
            self._shoot_map[row][column] = False
            return False

    @property
    def all_ships_destroyed(self):
        """
        Returns True if all ships are destroyed and False otherwise.
        """
        return self._shoot_count == self._ship_area

    @property
    def public_board(self) -> tuple[tuple[Optional[bool], ...], ...]:
        """
        Returns information about the cells to which there were moves.
        """
        return tuple(tuple(it) for it in self._shoot_map)

    @property
    def private_board(self) -> tuple[tuple[bool, ...], ...]:
        """
        Returns private information about the cells of this board.
        """
        return tuple(tuple(it) for it in self._board)

    def _calc_max_ships_area(self):
        """
        Calculates the maximum allowable area that ships can occupy.
        """
        return (self._width * self._height) // 5

    def _calc_ships_distribution(self, available_area: int) -> tuple[int, ...]:
        """
        Calculates the distribution of ships by their size based on available area.
        """
        max_size = 0
        area = 0
        while area + area + max_size <= available_area:
            area += area + max_size
            max_size += 1
        max_size -= 1
        self._ship_area = area
        return tuple(range(max_size, 0, -1))

    def _generate_board(self):
        """
        Fills the board with ships in random positions.
        The ships can touch each other.
        """
        ships_area = self._calc_max_ships_area()
        ships_distribution = self._calc_ships_distribution(ships_area)

        for ship_size in range(len(ships_distribution), 0, -1):
            counter = 0
            while counter < ships_distribution[ship_size - 1]:
                column = randrange(self._width)
                row = randrange(self._height)
                rotate = bool(randrange(2))
                try:
                    self._place_ship(ship_size, column, row, rotate)
                except PlacementError:
                    continue

                counter += 1

    def _check_cell_is_empty(self, column: int, row: int):
        """
        Checks for the ship in the cell at `column` and `row`. If the ship is present, it raises an exception.

        :raises PlacementError:
        """
        if self._board[row][column]:
            raise PlacementError('The desired area is not empty.')

    def _fill_cell(self, column: int, row: int):
        """
        Marks the cell at `column` and `row` as occupied by a ship.
        """
        self._board[row][column] = True

    def _place_ship(self, ship_size: int, column: int, row: int, rotate: bool = False):
        """
        Inserts a ship of size `ship_size` with start at `column` and `row`.
        :param rotate: If the argument is True, then the ship will be located along the row-axis.

        :raises PlacementError:
        """
        if (not rotate and (column + ship_size - 1 >= self._width) or
                rotate and (row + ship_size - 1 >= self._height)):
            raise PlacementError('The ship is out of bounds of the board.')

        def apply_function_on_ship_area(func: Callable[[int, int], None]):
            """
            Applies the function to all cells where the ship should be.
            """
            for shift in range(ship_size):
                shifted_column = (column + shift) if not rotate else column
                shifted_row = (row + shift) if rotate else row
                func(shifted_column, shifted_row)

        apply_function_on_ship_area(self._check_cell_is_empty)
        apply_function_on_ship_area(self._fill_cell)
