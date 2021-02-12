import curses
import argparse

from battleship.game import Game
from battleship.players import HumanPlayer, RandomPlayer
from battleship.board import Board


def main(screen, n, m):
    game = Game(Board(screen, n, m), HumanPlayer(), RandomPlayer())
    game.play()


if __name__ == '__main__':
    parser = argparse.ArgumentParser(description="Battleship console game.")
    parser.add_argument('-n', type=int, help='Number of lines per field. 5 or higher.', default=5)
    parser.add_argument('-m', type=int, help='Number of columns per field. 5 or higher.', default=5)
    args = parser.parse_args()
    curses.wrapper(main, args.n, args.m)
