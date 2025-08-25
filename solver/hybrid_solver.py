# solver/hybrid_solver.py
from .base_solver import BaseSolver
from typing import List
import os, torch
from envs.cube3x3 import Cube3x3Env, MOVES
from rl.mcts import run_mcts
from models.policy_value_net import PolicyValueNet
from solver.kociemba_solver import Kociemba3x3Solver

CKPT_3x3 = os.path.join("models", "checkpoints", "pvnet_3x3.pt")

class HybridSolver(BaseSolver):
    def __init__(self, kind: str):
        self.kind = kind

    def _solve_3x3_with_net(self, scramble: str, sims=256, max_steps=120, device="cpu"):
        # preparar entorno desde scramble
        env = Cube3x3Env()
        # Aplicar scramble en PyCuber, parseo simple
        import pycuber as pc
        env.cube = pc.Cube()
        env.cube(pc.Formula(scramble))

        # cargar red
        net = PolicyValueNet(324, 18).to(device)
        if os.path.exists(CKPT_3x3):
            net.load_state_dict(torch.load(CKPT_3x3, map_location=device))
            net.eval()
        else:
            return None  # sin modelo todavía

        plan: List[str] = []
        for _ in range(max_steps):
            if env.is_solved(): break
            pi = run_mcts(env, net, n_sims=sims, device=device)
            action = int(pi.argmax())
            plan.append(env.action_to_move(action))
            env.step(action)
        if env.is_solved():
            return " ".join(plan)
        return None

    def solve(self, scramble: str) -> str:
        if self.kind == "3x3":
            sol = self._solve_3x3_with_net(scramble)
            if sol:
                return f"[DL+MCTS] Solución encontrada ({len(sol.split())}): {sol}"
            # fallback
            try:
                ks = Kociemba3x3Solver()
                return "[Fallback Kociemba] " + ks.solve_from_scramble(scramble)
            except Exception as e:
                return f"No fue posible resolver con DL ni con Kociemba: {e}"

        # Otros puzzles: dejar listo el gancho
        return (f"Solver self-play para {self.kind} aún no implementado.\n"
                f"Implementá envs/<puzzle>_env.py y cargá un modelo entrenado.")
