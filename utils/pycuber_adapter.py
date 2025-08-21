import pycuber as pc
ORDER = "URFDLB"

def _map_colors():
    base = pc.Cube()
    return {str(base.faces[f][1][1]): f for f in ORDER}

def scramble_to_facelets(scramble: str) -> str:
    cube = pc.Cube()
    seq = pc.Formula(scramble)
    cube(seq)
    color_to_letter = _map_colors()
    facelets=[]
    for f in ORDER:
        face = cube.faces[f]
        for r in range(3):
            for c in range(3):
                facelets.append(color_to_letter[str(face[r][c])])
    return "".join(facelets)
