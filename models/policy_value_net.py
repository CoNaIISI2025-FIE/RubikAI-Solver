# models/policy_value_net.py
import torch
import torch.nn as nn
import torch.nn.functional as F

class PolicyValueNet(nn.Module):
    """
    Entrada: vector estado (por ahora 324 para 3x3).
    Salidas: logits de política (18) + valor escalar en [-1,1].
    """
    def __init__(self, state_dim: int, n_actions: int):
        super().__init__()
        hidden = 512
        self.fc1 = nn.Linear(state_dim, hidden)
        self.fc2 = nn.Linear(hidden, hidden)
        self.pi_head = nn.Linear(hidden, n_actions)
        self.v_head  = nn.Linear(hidden, 1)

    def forward(self, x):
        # x: [B, state_dim]
        h = F.relu(self.fc1(x))
        h = F.relu(self.fc2(h))
        pi_logits = self.pi_head(h)
        v = torch.tanh(self.v_head(h))  # [-1,1]
        return pi_logits, v.squeeze(-1)
