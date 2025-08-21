# solver/kociemba_solver.py
import kociemba
import pycuber as pc

ORDER = "URFDLB"

def _face_matrix(cube, f):
    faces = getattr(cube, "faces", None)
    if faces is not None:
        face = faces[f]
        return [[str(face[r][c]) for c in range(3)] for r in range(3)]
    gf = getattr(cube, "get_face", None)
    if gf is not None:
        face = gf(f)
        return [[str(face[r][c]) for c in range(3)] for r in range(3)]
    raise RuntimeError("No se pudo acceder a la cara del cubo con pycuber.")

def _color_to_letter_map(cube):
    m = {}
    for f in ORDER:
        mat = _face_matrix(cube, f)
        center = mat[1][1]
        m[center] = f
    return m

def scramble_to_facelets(scramble: str) -> str:
    cube = pc.Cube()
    cube(pc.Formula(scramble))
    cmap = _color_to_letter_map(cube)
    facelets = []
    for f in ORDER:
        mat = _face_matrix(cube, f)
        for r in range(3):
            for c in range(3):
                facelets.append(cmap[mat[r][c]])
    return "".join(facelets)

class Kociemba3x3Solver:
    def solve(self, scramble: str) -> str:
        return self.solve_from_scramble(scramble)

    def solve_from_scramble(self, scramble: str) -> str:
        facelets = scramble_to_facelets(scramble)
        return kociemba.solve(facelets)

    def solve_from_facelets(self, facelets: str) -> str:
        """String de 54 facelets en orden URFDLB (kociemba)."""
        return kociemba.solve(facelets)
