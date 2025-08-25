# envs/base_env.py
from abc import ABC, abstractmethod
from typing import List, Tuple, Any

class BasePuzzleEnv(ABC):
    """
    Interfaz mínima para puzzles tipo Rubik.
    Single-agent, episodic. Recompensa 1 al resolver, 0 en transición,
    -1 al terminar sin resolver (o reward shaping si lo implementás).
    """

    @abstractmethod
    def reset_to_solved(self) -> None: ...

    @abstractmethod
    def scramble(self, n_moves: int) -> None: ...

    @abstractmethod
    def is_solved(self) -> bool: ...

    @abstractmethod
    def legal_actions(self) -> List[int]: ...

    @abstractmethod
    def step(self, action: int) -> None: ...

    @abstractmethod
    def copy(self) -> "BasePuzzleEnv": ...

    @abstractmethod
    def state_embedding(self) -> "numpy.ndarray":
        """Devuelve un vector/tenor con el estado (p.ej., one-hot 54x6)."""
        ...

    @abstractmethod
    def action_to_move(self, action: int) -> str: ...
