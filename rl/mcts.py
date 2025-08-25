import math
import numpy as np
import torch
from typing import Dict

class Node:
    def __init__(self, prior: float):
        self.P = prior
        self.N = 0
        self.W = 0.0
        self.Q = 0.0
        self.children: Dict[int, "Node"] = {}
        self.is_expanded = False

def run_mcts(env, net, n_sims=200, c_puct=1.5, device="cpu"):
    """
    MCTS estilo AlphaZero para 1 jugador.
    Devuelve distribución pi sobre acciones (visitas normalizadas).
    """
    root = Node(prior=1.0)

    def expand(node, env_copy):
        with torch.no_grad():
            s = torch.from_numpy(env_copy.state_embedding()).float().to(device).unsqueeze(0)
            logits, v = net(s)
            p = torch.softmax(logits, dim=-1)[0].cpu().numpy()  # [A]
        for a in env_copy.legal_actions():
            node.children[a] = Node(prior=float(p[a]))
        node.is_expanded = True
        return float(v.item())

    def simulate(node, env_copy, depth=0):
        if env_copy.is_solved():
            # recompensa 1 al resolver
            return 1.0
        if depth > 100:  # seguridad
            return -1.0

        if not node.is_expanded:
            v = expand(node, env_copy)
            return v

        # PUCT
        total_N = sum(ch.N for ch in node.children.values()) + 1
        best_score, best_a = -1e9, None
        for a, ch in node.children.items():
            U = c_puct * ch.P * math.sqrt(total_N) / (1 + ch.N)
            score = ch.Q + U
            if score > best_score:
                best_score, best_a = score, a

        # avanzar
        next_env = env_copy.copy()
        next_env.step(best_a)

        v = simulate(node.children[best_a], next_env, depth+1)

        # backup
        ch = node.children[best_a]
        ch.N += 1
        ch.W += v
        ch.Q = ch.W / ch.N
        return v

    for _ in range(n_sims):
        simulate(root, env.copy())

    visits = np.zeros(len(env.legal_actions()), dtype=np.float32)
    for a, ch in root.children.items():
        visits[a] = ch.N
    if visits.sum() == 0:
        visits += 1.0
    pi = visits / visits.sum()
    return pi
