import torch.nn as nn
import torch

class PolicyNet(nn.Module):
    def __init__(self, state_dim=256, n_actions=18):
        super().__init__()
        self.net = nn.Sequential(
            nn.Linear(state_dim,256), nn.ReLU(),
            nn.Linear(256,256), nn.ReLU(),
            nn.Linear(256,n_actions)
        )

    def forward(self,x):
        return self.net(x)

def sample_action(policy, state_embed):
    with torch.no_grad():
        logits = policy(state_embed.unsqueeze(0))
        prob = torch.softmax(logits,dim=-1)[0]
        return torch.multinomial(prob,1).item()
