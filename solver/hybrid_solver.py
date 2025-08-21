from .base_solver import BaseSolver

class HybridSolver(BaseSolver):
    def __init__(self, kind: str):
        self.kind = kind

    def solve(self, scramble: str) -> str:
        return (f"Solver híbrido para {self.kind} aún no implementado.\n"
                f"Listo para integrar DL y heurísticas.")
