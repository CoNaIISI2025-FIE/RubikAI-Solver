# envs/cube3x3_env.py
import random
import numpy as np
import pycuber as pc
from typing import List
from .base_env import BasePuzzleEnv

ORDER = "URFDLB"
# 18 movimientos estándar
MOVES = [
    "U","U'","U2","D","D'","D2","L","L'","L2",
    "R","R'","R2","F","F'","F2","B","B'","B2"
]
MOVE_TO_IDX = {m:i for i,m in enumerate(MOVES)}

def _face_matrix(cube, f):
    faces = getattr(cube, "faces", None)
    if faces is not None:
        face = faces[f]
        return [[str(face[r][c]) for c in range(3)] for r in range(3)]
    gf = getattr(cube, "get_face", None)
    if gf is not None:
        face = gf(f)
        return [[str(face[r][c]) for c in range(3)] for r in range(3)]
    raise RuntimeError("pycuber no permite leer la cara")

class Cube3x3Env(BasePuzzleEnv):
    """
    Observación: one-hot de 54 stickers × 6 colores = 324 dims.
    El mapeo de color->letra se ancla por los centros.
    """
    def __init__(self):
        self.cube = pc.Cube()

    def reset_to_solved(self) -> None:
        self.cube = pc.Cube()

    def scramble(self, n_moves: int) -> None:
        seq = [random.choice(MOVES) for _ in range(n_moves)]
        self.cube(pc.Formula(" ".join(seq)))

    def is_solved(self) -> bool:
        return str(self.cube) == str(pc.Cube())

    def legal_actions(self) -> List[int]:
        return list(range(len(MOVES)))  # todas legales

    def step(self, action: int) -> None:
        mv = MOVES[action]
        self.cube(pc.Formula(mv))

    def copy(self) -> "Cube3x3Env":
        env = Cube3x3Env()
        # pycuber tiene copy()
        env.cube = self.cube.copy()
        return env

    def _color_to_letter_map(self):
        m = {}
        for f in ORDER:
            mat = _face_matrix(self.cube, f)
            center = mat[1][1]
            m[center] = f
        return m

    def state_embedding(self) -> np.ndarray:
        cmap = self._color_to_letter_map()  # color real -> letra
        planes = []
        for f in ORDER:
            mat = _face_matrix(self.cube, f)
            for r in range(3):
                for c in range(3):
                    letter = cmap[mat[r][c]]  # U,R,F,D,L,B
                    onehot = np.zeros(6, dtype=np.float32)
                    onehot["URFDLB".index(letter)] = 1.0
                    planes.append(onehot)
        arr = np.concatenate(planes, axis=0)  # 324
        return arr

    def action_to_move(self, action: int) -> str:
        return MOVES[action]
