import curses
import argparse
import pickle
from typing import Optional

from battleship.exceptions import QuitSignal, NotEnoughSpace
from battleship.game import Game
from battleship.players import HumanPlayer, RandomPlayer
from battleship.utils import check_text_size

SAVE_FILE_NAME = 'game.save'


def main(screen: curses.window, height, width):
    game: Optional[Game] = None
    while True:
        display_string_builder: list[str, ...] = list()
        display_string_builder.append('###########################')
        display_string_builder.append('#  WELCOME TO BATTLESHIP  #')
        display_string_builder.append('###########################')
        display_string_builder.append('')

        if game and game.winner:
            display_string_builder.append(f'The winner of the last game is {game.winner}!')
            display_string_builder.append('')

        display_string_builder.append('Press n to start new game.')
        display_string_builder.append('Press l to load the game (if exists).')
        display_string_builder.append('Press q to quit the game.')

        screen.clear()
        check_text_size(display_string_builder, *screen.getmaxyx())
        display_string = '\n'.join(display_string_builder)
        screen.addstr(0, 0, display_string)

        input_character = screen.getch()

        if input_character == ord('q'):
            return

        if input_character in (ord('n'), ord('l')):
            if input_character == ord('l'):
                try:
                    with open(SAVE_FILE_NAME, 'rb') as file:
                        game = pickle.load(file)
                except OSError:
                    continue
            else:
                first_player = HumanPlayer('You')
                second_player = RandomPlayer('Robot')
                game = Game(first_player=first_player, second_player=second_player, board_size=(height, width))
            try:
                game.play(screen)
            except QuitSignal as qs:
                if qs.signal_type == QuitSignal.BACK_TO_MAIN_MENU:
                    continue
                if qs.signal_type == QuitSignal.QUIT:
                    return
                if qs.signal_type == QuitSignal.QUIT_AND_SAVE:
                    with open(SAVE_FILE_NAME, 'wb') as file:
                        pickle.dump(game, file, pickle.HIGHEST_PROTOCOL)
                        return


if __name__ == '__main__':
    parser = argparse.ArgumentParser(description="Battleship console game.")
    parser.add_argument('-height', type=int, help='Height of field. 5 or higher.', default=5)
    parser.add_argument('-width', type=int, help='Width of field. 5 or higher.', default=5)
    args = parser.parse_args()
    try:
        curses.wrapper(main, args.height, args.width)
    except NotEnoughSpace as err:
        print('Your terminal is too small to display the game.')
