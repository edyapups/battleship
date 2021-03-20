import curses
import argparse
import pickle
from typing import Optional

from battleship.exceptions import QuitSignal
from battleship.game import Game
from battleship.players import HumanPlayer, RandomPlayer


SAVE_FILE_NAME = 'game.save'

# TODO Сделать документацию ко всему проекту.

def main(screen: curses.window, height, width):
    game: Optional[Game] = None
    while True:
        welcome_str = '###########################\n' \
                      '#  WELCOME TO BATTLESHIP  #\n' \
                      '###########################\n\n'
        winner_str = ''

        instructions_str = 'Press n to start new game.\n'\
                           'Press l to load the game (if exists).\n' \
                           'Press q to quit the game.\n'

        if game and game.winner:
            winner_str = f'The winner of the last game is {game.winner}!\n'

        screen.clear()
        screen.addstr(0, 0, welcome_str + winner_str + instructions_str)

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
    curses.wrapper(main, args.height, args.width)