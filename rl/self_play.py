import os, random, time, math
import numpy as np
import torch
import torch.nn.functional as F
from torch.utils.data import Dataset, DataLoader
from typing import List, Tuple
from envs.cube3x3 import Cube3x3Env, MOVES
from models.policy_value_net import PolicyValueNet
from rl.mcts import run_mcts

class Replay(Dataset):
    def __init__(self, capacity=200_000):
        self.capacity = capacity
        self.data: List[Tuple[np.ndarray, np.ndarray, float]] = []

    def push_episode(self, states, pis, z):
        for s, p in zip(states, pis):
            self.data.append((s.astype(np.float32), p.astype(np.float32), float(z)))
        if len(self.data) > self.capacity:
            self.data = self.data[-self.capacity:]

    def __len__(self): return len(self.data)
    def __getitem__(self, i):
        s, p, z = self.data[i]
        return torch.from_numpy(s), torch.from_numpy(p), torch.tensor(z, dtype=torch.float32)

def play_game(net, device, scramble_len, max_steps, n_sims, temperature=1.0):
    env = Cube3x3Env()
    env.scramble(scramble_len)

    states, pis = [], []
    solved = False

    for t in range(max_steps):
        s = env.state_embedding()
        pi = run_mcts(env, net, n_sims=n_sims, device=device)
        # muestreo con temperatura
        if temperature > 0:
            probs = np.power(pi, 1.0 / temperature)
            probs /= probs.sum()
            a = np.random.choice(len(MOVES), p=probs)
        else:
            a = int(np.argmax(pi))
        states.append(s); pis.append(pi)
        env.step(a)
        if env.is_solved():
            solved = True
            break

    z = 1.0 if solved else -1.0
    return states, pis, z, solved

def train_self_play(
    out_path="models/checkpoints/pvnet_3x3.pt",
    device="cpu",
    steps=2_000,
    batch_size=256,
    lr=1e-3,
    sims_per_move=128,
    curriculum=(1, 10),
    max_steps=60,
    eval_every=500
):
    os.makedirs(os.path.dirname(out_path), exist_ok=True)
    state_dim = 324
    n_actions = 18

    net = PolicyValueNet(state_dim, n_actions).to(device)
    opt = torch.optim.Adam(net.parameters(), lr=lr)
    buf = Replay()

    solved_rate_hist = []

    for it in range(1, steps+1):
        # currículo: crece la dificultad con el tiempo
        lo, hi = curriculum
        curr_len = min(hi, lo + (it // 400))  # aumenta cada 400 episodios aprox.
        states, pis, z, solved = play_game(
            net, device,
            scramble_len=random.randint(lo, curr_len),
            max_steps=max_steps,
            n_sims=sims_per_move,
            temperature=1.0 if it < 1000 else 0.5
        )
        buf.push_episode(states, pis, z)

        if solved: solved_rate_hist.append(1)
        else:      solved_rate_hist.append(0)
        if len(solved_rate_hist) > 200: solved_rate_hist = solved_rate_hist[-200:]

        # entrenamiento on-policy simple
        if len(buf) >= batch_size:
            loader = DataLoader(buf, batch_size=batch_size, shuffle=True, drop_last=True)
            s, p_target, z_target = next(iter(loader))
            s = s.to(device).float()
            p_target = p_target.to(device).float()
            z_target = z_target.to(device).float()

            pi_logits, v = net(s)
            policy_loss = -(p_target * torch.log_softmax(pi_logits, dim=-1)).sum(dim=-1).mean()
            value_loss  = F.mse_loss(v, z_target)
            loss = policy_loss + value_loss * 0.5

            opt.zero_grad()
            loss.backward()
            opt.step()

        if it % eval_every == 0:
            sr = (sum(solved_rate_hist)/len(solved_rate_hist)) if solved_rate_hist else 0.0
            print(f"[{it}] solved_rate(últimos {len(solved_rate_hist)}): {sr:.3f}")
            torch.save(net.state_dict(), out_path)

    torch.save(net.state_dict(), out_path)
    print(f"Modelo guardado en: {out_path}")
