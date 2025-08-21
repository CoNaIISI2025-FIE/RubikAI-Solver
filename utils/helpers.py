"""Utility helpers for the Rubik's cube project.

Currently only contains a small helper to rotate a list of colours.
"""
from typing import Iterable, List, Sequence, TypeVar

T = TypeVar("T")

def rotate_colors(colors: Sequence[T], steps: int = 1) -> List[T]:
    """Return a new list with ``colors`` rotated by ``steps`` positions.

    Parameters
    ----------
    colors:
        Sequence of elements to rotate. The original sequence is not modified.
    steps:
        Number of positions to rotate. Positive numbers rotate to the right.

    Examples
    --------
    >>> rotate_colors(["red", "blue", "green"])
    ['green', 'red', 'blue']
    >>> rotate_colors([1, 2, 3, 4], 2)
    [3, 4, 1, 2]
    """
    if not colors:
        return []

    n = len(colors)
    steps %= n
    if steps == 0:
        return list(colors)

    return list(colors[-steps:]) + list(colors[:-steps])
