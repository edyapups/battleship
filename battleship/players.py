import curses
import logging
from abc import ABC, abstractmethod
from random import choice
from typing import Optional


class AbstractPlayer(ABC):

    def __init__(self, name: Optional[str] = None) -> None:
        self.name = name

    def __str__(self) -> str:
        return self.name if self.name else 'Nameless'

    @abstractmethod
    def move(self,
             screen: Optional[curses.window],
             open_board: tuple[tuple[bool, ...], ...],
             hidden_board: tuple[tuple[Optional[bool], ...], ...],
             message: Optional[str]):
        raise NotImplementedError('`move()` must be implemented.')


class HumanPlayer(AbstractPlayer):
    SHIP_MAP = {
        True: 'O',
        False: 'X',
        None: '.'
    }

    @staticmethod
    def _get_indents(block_size, number_length) -> tuple[int, int]:
        size_minus_length = block_size - number_length
        row_height_indents = (size_minus_length // 2, size_minus_length // 2 + size_minus_length % 2)
        return row_height_indents

    def draw_board(self, board: tuple[tuple[Optional[bool], ...], ...]) -> tuple[list[str, ...], int, int]:
        rows = len(board)
        row_height = len(str(rows))
        board_height = 2 + rows

        columns = len(board[0])
        column_width = len(str(columns))
        if column_width > 1:
            column_width += 2
        board_width = row_height + 1 + column_width * columns

        logging.basicConfig(level=logging.INFO)

        str_board_rows: list[str, ...] = list()
        string_parts: list[str, ...] = list()

        string_parts.append(' ' * (row_height + 1))
        for column in range(1, columns + 1):
            indents = self._get_indents(column_width, len(str(column)))
            string_parts.append(' ' * indents[0])
            string_parts.append(str(column))
            string_parts.append(' ' * indents[1])

        str_board_rows.append(''.join(string_parts))
        str_board_rows.append(' ' * (row_height + 1) + '_' * (column_width * columns))

        string_parts.clear()

        for row in range(1, rows + 1):
            row_number_string = str(row)
            row_number_length = len(row_number_string)

            string_parts.append((row_height - row_number_length) * ' ')
            string_parts.append(row_number_string + '|')
            cell_indents = self._get_indents(column_width, 1)
            for column in range(1, columns + 1):
                string_parts.append(' ' * cell_indents[0])
                string_parts.append(self.SHIP_MAP[board[row - 1][column - 1]])
                string_parts.append(' ' * cell_indents[1])

            str_board_rows.append(''.join(string_parts))
            string_parts.clear()

        return str_board_rows, board_height, board_width

    def move(self, screen, open_board: tuple[tuple[bool, ...], ...],
             hidden_board: tuple[tuple[Optional[bool], ...], ...], message: Optional[str]):
        while True:
            screen.clear()
            drawn_open_board_rows, drawn_board_height, drawn_board_width = self.draw_board(open_board)
            drawn_hidden_board_rows, _, _ = self.draw_board(hidden_board)
            screen_height, screen_width = screen.getmaxyx()
            current_x = 0

            if screen_width >= drawn_board_width * 2 + 1:
                board = '\n'.join((' '.join(it) for it in zip(drawn_open_board_rows, drawn_hidden_board_rows)))

            screen.getch()
#             TODO Доделать


class RandomPlayer(AbstractPlayer):
    def move(self, screen, open_board: tuple[tuple[bool, ...], ...],
             hidden_board: tuple[tuple[Optional[bool], ...], ...], message: Optional[str]):
        choices: list[tuple[int, int], ...] = list()
        height = len(hidden_board)
        width = len(hidden_board[0]) * len(str(len(hidden_board[0])))
        for row_num in range(height):
            for column_num in range(width):
                if hidden_board[row_num][column_num] is None:
                    choices.append((column_num, row_num))
        chosen = choice(choices)
        return chosen
