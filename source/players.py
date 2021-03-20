import curses
import logging
from abc import ABC, abstractmethod
from itertools import cycle
from random import choice
from typing import Optional

from source.exceptions import QuitSignal
from source.utils import check_text_size


class AbstractPlayer(ABC):

    def __init__(self, name: Optional[str] = None) -> None:
        self.name = name

    def __str__(self) -> str:
        return self.name if self.name else 'Nameless'

    @abstractmethod
    def move(self,
             screen: Optional[curses.window],
             player_board: tuple[tuple[bool, ...], ...],
             player_hit_board: tuple[tuple[Optional[bool], ...], ...],
             enemy_hit_board: tuple[tuple[Optional[bool], ...], ...],
             message: Optional[str]) -> tuple[int, int]:
        raise NotImplementedError('`move()` must be implemented.')


class HumanPlayer(AbstractPlayer):
    SHIP_MAP = {
        True: 'O',
        False: '*',
        None: '.'
    }

    @staticmethod
    def _get_indents(block_size, number_length) -> tuple[int, int]:
        size_minus_length = block_size - number_length
        row_height_indents = (size_minus_length // 2, size_minus_length // 2 + size_minus_length % 2)
        return row_height_indents

    def get_board_builder(self, board: tuple[tuple[Optional[bool], ...], ...]) -> tuple[list[str, ...], int, int]:
        rows = len(board)
        row_height = len(str(rows))
        board_height = 2 + rows

        columns = len(board[0])
        column_width = len(str(columns))
        if column_width > 1:
            column_width += 2
        board_width = row_height + 1 + column_width * columns

        str_board_rows: list[str, ...] = list()
        string_parts: list[str, ...] = list()

        # Building column numbers.
        string_parts.append(' ' * (row_height + 1))
        for column in range(1, columns + 1):
            indents = self._get_indents(column_width, len(str(column)))
            string_parts.append(' ' * indents[0])
            string_parts.append(str(column))
            string_parts.append(' ' * indents[1])
        str_board_rows.append(''.join(string_parts))
        string_parts.clear()

        str_board_rows.append(' ' * (row_height + 1) + '_' * (column_width * columns))

        # Building rows.
        for row in range(1, rows + 1):
            row_number_string = str(row)
            row_number_length = len(row_number_string)

            # Building row number.
            string_parts.append((row_height - row_number_length) * ' ')
            string_parts.append(row_number_string + '|')

            # Building cells in the row.
            cell_indents = self._get_indents(column_width, 1)
            for column in range(1, columns + 1):
                string_parts.append(' ' * cell_indents[0])
                string_parts.append(self.SHIP_MAP[board[row - 1][column - 1]])
                string_parts.append(' ' * cell_indents[1])

            str_board_rows.append(''.join(string_parts))
            string_parts.clear()

        return str_board_rows, board_height, board_width

    def move(self, screen, player_board, player_hit_board, enemy_hit_board, message):
        """
        Displays information about the state of the boards and allows player to enter coordinates for the move.

        :raises QuitSignal:
        """
        input_column: int = 0
        input_row: int = 0
        enters: int = 0

        while True:
            screen.clear()
            display_string_builder: list[str, ...] = list()

            # Getting builders for all boards.
            player_board_builder, _, board_width = self.get_board_builder(player_board)
            player_hit_board_builder, _, _ = self.get_board_builder(player_hit_board)
            enemy_hit_board_builder, _, _ = self.get_board_builder(enemy_hit_board)

            # Building namings for board groups.
            indents = self._get_indents(board_width * 2 + 1, 3)
            display_string_builder.append(' ' * indents[0] + 'You' + ' ' * indents[1] + ' | ' + 'Enemy')

            # Building parallel board displaying.
            board_builder: list[str, ...] = [''.join(it) for it in zip(player_board_builder,
                                                                       cycle((' ',)),
                                                                       player_hit_board_builder,
                                                                       cycle((' | ',)),
                                                                       enemy_hit_board_builder)]
            display_string_builder.extend(board_builder)
            display_string_builder.append('')

            if message:
                display_string_builder.append(message)
                display_string_builder.append('')

            display_string_builder.append('Enter move coordinates:')
            display_string_builder.append(f'Column: {input_column}' + ('<' if enters == 0 else ''))
            display_string_builder.append(f'Row: {input_row}' + ('<' if enters == 1 else ''))
            display_string_builder.append('')

            display_string_builder.append('Press s to save the game and quit the game.')
            display_string_builder.append('Press q to quit the game without saving.')
            display_string_builder.append('Press m to quit to the main menu without saving.')

            # Displaying data.
            check_text_size(display_string_builder, *screen.getmaxyx())
            display_string = '\n'.join(display_string_builder)
            screen.addstr(0, 0, display_string)

            c = screen.getch()

            if c == ord('q'):
                raise QuitSignal(signal_type=QuitSignal.QUIT)
            if c == ord('m'):
                raise QuitSignal(signal_type=QuitSignal.BACK_TO_MAIN_MENU)
            if c == ord('s'):
                raise QuitSignal(signal_type=QuitSignal.QUIT_AND_SAVE)
            if c in (ord(it) for it in '0123456789'):
                digit = int(chr(c))
                if enters == 0:
                    input_column = input_column * 10 + digit
                else:
                    input_row = input_row * 10 + digit

            # What to do if the user entered ENTER.
            if c == 10:
                enters += 1
                if enters == 2:
                    if input_column == 0 or input_row == 0:
                        input_column = 0
                        input_row = 0
                        enters = 0
                        message = 'Move coordinates must be greater than zero.'
                        continue
                    return input_column - 1, input_row - 1

            # What to do if the user entered BACKSPACE.
            if c == 127:
                if enters == 0:
                    input_column //= 10
                else:
                    input_row //= 10


class RandomPlayer(AbstractPlayer):
    def move(self, screen, player_board, player_hit_board, enemy_hit_board, message):
        """
        Selects one of the non-shot cells.
        """
        choices: list[tuple[int, int], ...] = list()
        height = len(enemy_hit_board)
        width = len(enemy_hit_board[0])
        for row_num in range(height):
            for column_num in range(width):
                if enemy_hit_board[row_num][column_num] is None:
                    choices.append((column_num, row_num))
        chosen = choice(choices)
        return chosen
