from .base_solver import BaseSolver
from utils.scramble_utils import normalize_scramble
from utils.pycuber_adapter import scramble_to_facelets
import kociemba

class Kociemba3x3Solver(BaseSolver):
    def solve(self, scramble: str) -> str:
        return self.solve_from_scramble(scramble)

    def solve_from_scramble(self, scramble: str) -> str:
        s = normalize_scramble(scramble)
        facelets = scramble_to_facelets(s)
        return kociemba.solve(facelets)
