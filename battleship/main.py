import curses
import argparse


def main(screen):
    pass


if __name__ == '__main__':
    parser = argparse.ArgumentParser(description="Battleship console game.")

    curses.wrapper(main)
