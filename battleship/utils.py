from battleship.exceptions import NotEnoughSpace


def check_text_size(output_builder: list[str, ...], height: int, width: int) -> None:
    """
    Checks that the displaying text will fit on the terminal with sizes `height` and `width`.

    :raises NotEnoughSpace:
    """
    max_width: int
    max_height: int
    output_builder: list[str, ...]
    max_height = len(output_builder)
    max_width = max(map(len, output_builder))

    if not (max_height <= height and max_width <= width):
        raise NotEnoughSpace('The terminal is not large enough to display the required information.')
