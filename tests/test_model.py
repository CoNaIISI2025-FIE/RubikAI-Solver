import os
import sys
import matplotlib

# Use a non-interactive backend for tests
matplotlib.use("Agg")

sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))
from models import model


class DummyEvent:
    def __init__(self, x, y, axes):
        self.xdata = x
        self.ydata = y
        self.inaxes = axes


def test_on_click_rotates_points_and_colors():
    circle = model.circulos[0]
    initial_colors = circle["colores"].copy()
    initial_points = circle["puntos"].copy()

    event = DummyEvent(circle["centro"][0], circle["centro"][1], model.ax)
    model.on_click(event)

    assert circle["colores"] == initial_colors[-1:] + initial_colors[:-1]
    assert circle["puntos"] == initial_points[-1:] + initial_points[:-1]

