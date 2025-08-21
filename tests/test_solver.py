import os
import sys
import pytest

# Ensure the project root is on the import path so ``utils`` can be imported
sys.path.append(os.path.dirname(os.path.dirname(__file__)))
from utils.helpers import rotate_colors


def test_rotate_colors_single_step():
    colors = ['red', 'blue', 'green']
    assert rotate_colors(colors) == ['green', 'red', 'blue']
    # Original list should remain unchanged
    assert colors == ['red', 'blue', 'green']


def test_rotate_colors_multiple_steps():
    colors = ['a', 'b', 'c', 'd']
    assert rotate_colors(colors, 2) == ['c', 'd', 'a', 'b']


def test_rotate_colors_steps_wrap():
    colors = [1, 2, 3]
    # Rotating by a value larger than the list length should wrap around
    assert rotate_colors(colors, 4) == [3, 1, 2]


def test_rotate_colors_empty():
    assert rotate_colors([]) == []
