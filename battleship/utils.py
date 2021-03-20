from typing import Union

from battleship.exceptions import NotEnoughSpace


def check_text_size(output: Union[str, list[str, ...]], height: int, width: int) -> None:
    """
    Checks that the displaying text will fit on the terminal with sizes `height` and `width`.

    :raises NotEnoughSpace:
    """
    max_width: int
    max_height: int
    if isinstance(output, str):
        output = output.split('\n')
    output: list[str, ...]
    max_height = len(output)
    max_width = max(map(len, output))

    if not max_height <= height and max_width <= width:
        raise NotEnoughSpace('The terminal is not large enough to display the required information.')

