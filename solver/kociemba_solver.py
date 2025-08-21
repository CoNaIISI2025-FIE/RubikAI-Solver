# solver/kociemba_solver.py
import kociemba
import pycuber as pc

ORDER = "URFDLB"

def _face_matrix(cube, f):
    """
    Devuelve una matriz 3x3 de 'colores' para la cara f (U,R,F,D,L,B),
    compatible con diferentes versiones de pycuber.
    """
    # 1) Intento con .faces[f][r][c]
    faces = getattr(cube, "faces", None)
    if faces is not None:
        face = faces[f]
        return [[str(face[r][c]) for c in range(3)] for r in range(3)]

    # 2) Fallback: get_face('U') etc.
    gf = getattr(cube, "get_face", None)
    if gf is not None:
        face = gf(f)
        return [[str(face[r][c]) for c in range(3)] for r in range(3)]

    raise RuntimeError("No se pudo acceder a la cara del cubo (pycuber incompatible).")

def _color_to_letter_map(cube):
    """
    Mapea el color del centro de cada cara -> letra de cara (U,R,F,D,L,B).
    Así el string de 54 facelets queda en el alfabeto que exige kociemba.
    """
    m = {}
    for f in ORDER:
        mat = _face_matrix(cube, f)
        center = mat[1][1]  # color del centro
        m[center] = f
    return m

def scramble_to_facelets(scramble: str) -> str:
    """
    Aplica el scramble sobre un cubo resuelto y devuelve los 54 facelets
    en orden URFDLB que requiere kociemba.solve().
    """
    cube = pc.Cube()
    seq = pc.Formula(scramble)  # aplica U/D/L/R/F/B con ',2
    cube(seq)

    color_map = _color_to_letter_map(cube)
    facelets = []
    for f in ORDER:
        mat = _face_matrix(cube, f)
        for r in range(3):
            for c in range(3):
                facelets.append(color_map[mat[r][c]])
    return "".join(facelets)

class Kociemba3x3Solver:
    def __init__(self):
        pass

    def solve(self, scramble: str) -> str:
        return self.solve_from_scramble(scramble)

    def solve_from_scramble(self, scramble: str) -> str:
        facelets = scramble_to_facelets(scramble)
        return kociemba.solve(facelets)
