import re
MOVE = r"(U|D|L|R|F|B)(2|'|)?"
TOKEN = re.compile(MOVE)

def normalize_scramble(s: str) -> str:
    s = s.replace(",", " ").strip()
    parts = [p for p in s.split(" ") if p]
    for p in parts:
        if not TOKEN.fullmatch(p):
            raise ValueError(f"Movimiento inválido: {p}")
    return " ".join(parts)
