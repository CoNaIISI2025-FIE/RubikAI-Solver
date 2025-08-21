# gui/app.py
import tkinter as tk
from tkinter import ttk, messagebox
import pycuber as pc

from solver.kociemba_solver import Kociemba3x3Solver
from solver.hybrid_solver import HybridSolver
from gui.viewer3d import show_cube_3d  # nuevo

SUPPORTED = ["3x3", "4x4", "5x5", "Pyraminx", "Megaminx"]

FACE_COLOR = {
    "U": "#FFFFFF",
    "R": "#FF4D4D",
    "F": "#00CC66",
    "D": "#FFFF33",
    "L": "#FF9900",
    "B": "#3399FF",
}
ORDER_DRAW = "U L F R B D"
ORDER_FACELETS = "URFDLB"
FACE_OFFSETS = {"U": (3,0), "L": (0,3), "F": (3,3), "R": (6,3), "B": (9,3), "D": (3,6)}
CELL, PAD = 26, 2

def parse_moves(seq): return [p for p in seq.replace(",", " ").split() if p]
def invert_moves(moves):
    out=[]
    for m in moves[::-1]:
        if m.endswith("2"): out.append(m)
        elif m.endswith("'"): out.append(m[:-1])
        else: out.append(m+"'")
    return out

def _mat_py(cube, f):
    faces = getattr(cube, "faces", None)
    if faces is not None:
        face = faces[f]
        return [[str(face[r][c]) for c in range(3)] for r in range(3)]
    gf = getattr(cube, "get_face", None)
    if gf is not None:
        face = gf(f)
        return [[str(face[r][c]) for c in range(3)] for r in range(3)]
    raise RuntimeError("pycuber no permite leer la cara.")

def draw_state(canvas, letters):
    canvas.delete("all")
    for face in ORDER_DRAW.split():
        oc, orow = FACE_OFFSETS[face]
        mat = letters[face]
        for r in range(3):
            for c in range(3):
                fill = FACE_COLOR.get(mat[r][c], "#999")
                x0 = (oc+c)*(CELL+PAD); y0 = (orow+r)*(CELL+PAD)
                x1 = x0+CELL; y1 = y0+CELL
                canvas.create_rectangle(x0,y0,x1,y1, fill=fill, outline="#333", width=2)

def solved_letters():
    return {f:[[f]*3 for _ in range(3)] for f in ORDER_FACELETS}

def pycuber_to_letters(cube):
    cmap={}
    for f in ORDER_FACELETS:
        m=_mat_py(cube,f); cmap[m[1][1]]=f
    letters={}
    for f in ORDER_FACELETS:
        m=_mat_py(cube,f)
        letters[f]=[[cmap[m[r][c]] for c in range(3)] for r in range(3)]
    return letters

def letters_to_facelets(letters):
    s=[]
    for f in ORDER_FACELETS:
        m=letters[f]
        for r in range(3):
            for c in range(3): s.append(m[r][c])
    return "".join(s)

def hit_test(x,y):
    for face in ORDER_DRAW.split():
        oc, orow = FACE_OFFSETS[face]
        for r in range(3):
            for c in range(3):
                x0=(oc+c)*(CELL+PAD); y0=(orow+r)*(CELL+PAD)
                x1=x0+CELL; y1=y0+CELL
                if x0<=x<=x1 and y0<=y<=y1: return face,r,c
    return None

def launch_app():
    root = tk.Tk()
    root.title("IA Rubik Solver")
    root.geometry("1000x560")

    main = ttk.Frame(root, padding=10); main.pack(fill="both", expand=True)

    # ---- Panel izquierdo ----
    left = ttk.Frame(main, padding=5); left.pack(side="left", fill="y")

    ttk.Label(left, text="Tipo de cubo:").grid(row=0, column=0, sticky="w")
    cube_type = tk.StringVar(value="3x3")
    ttk.Combobox(left, textvariable=cube_type, values=SUPPORTED, state="readonly", width=14)\
        .grid(row=0, column=1, sticky="w", padx=5)

    ttk.Label(left, text="Scramble:").grid(row=1, column=0, sticky="w")
    scramble_var = tk.StringVar(value="U R2 F U' L2 D")
    ttk.Entry(left, textvariable=scramble_var, width=28)\
        .grid(row=1, column=1, sticky="w", padx=5, pady=4)

    edit_mode = tk.BooleanVar(value=False)
    ttk.Checkbutton(left, text="Modo edición (pintar)", variable=edit_mode)\
        .grid(row=2, column=0, columnspan=2, sticky="w", pady=(6,2))

    paint_letter = tk.StringVar(value="U")
    ttk.Label(left, text="Pintar con:").grid(row=3, column=0, sticky="w", pady=(4,0))
    pal = ttk.Frame(left); pal.grid(row=3, column=1, sticky="w")
    for i,f in enumerate(ORDER_FACELETS):
        tk.Radiobutton(pal, text=f, value=f, variable=paint_letter,
                       bg=FACE_COLOR[f], fg="black", indicatoron=False,
                       width=3, relief="raised").grid(row=0, column=i, padx=2)

    out = tk.Text(left, height=18, width=44, state="disabled")
    out.grid(row=6, column=0, columnspan=2, pady=8)
    def log(msg):
        out.config(state="normal"); out.insert("end", msg+"\n"); out.see("end"); out.config(state="disabled")

    # ---- Canvas derecha ----
    right = ttk.Frame(main, padding=5); right.pack(side="left", fill="both", expand=True)
    canvas_w=(12*(CELL+PAD)); canvas_h=(9*(CELL+PAD))
    cvs = tk.Canvas(right, width=canvas_w, height=canvas_h, bg="#1e1e1e", highlightthickness=0)
    cvs.pack(fill="both", expand=True)

    # ---- Estado / animación ----
    manual = solved_letters()
    cube = pc.Cube()
    anim_moves=[]; anim_idx=0; anim_speed_ms=300

    # historial por color (para límite 9 y “despintar el último”)
    paint_history = {f: [] for f in ORDER_FACELETS}

    def refresh():
        if edit_mode.get(): draw_state(cvs, manual)
        else: draw_state(cvs, pycuber_to_letters(cube))

    def count_color(letter):
        return sum(1 for f in ORDER_FACELETS for r in range(3) for c in range(3) if manual[f][r][c]==letter)

    def remove_from_history(letter, pos):
        if pos in paint_history[letter]: paint_history[letter].remove(pos)

    def set_sticker(face,r,c,new_letter):
        old = manual[face][r][c]
        if old == new_letter: return
        remove_from_history(old, (face,r,c))

        if count_color(new_letter) >= 9:
            if paint_history[new_letter]:
                lf,lr,lc = paint_history[new_letter].pop()
                manual[lf][lr][lc] = lf  # vuelve a letra base de su cara
            else:
                return
        manual[face][r][c]=new_letter
        paint_history[new_letter].append((face,r,c))

    def reset_all():
        nonlocal manual,cube,anim_moves,anim_idx
        manual=solved_letters(); cube=pc.Cube(); anim_moves=[]; anim_idx=0
        for k in paint_history: paint_history[k].clear()
        refresh()

    def on_click(ev):
        if not edit_mode.get(): return
        hit=hit_test(ev.x, ev.y)
        if not hit: return
        f,r,c=hit
        set_sticker(f,r,c,paint_letter.get())
        draw_state(cvs, manual)

    cvs.bind("<Button-1>", on_click)

    def apply_scramble():
        kind=cube_type.get()
        if kind!="3x3":
            log(f"Solver híbrido para {kind} aún no implementado.\nListo para integrar DL y heurísticas.")
            return
        nonlocal cube
        try:
            cube=pc.Cube(); cube(pc.Formula(scramble_var.get().strip()))
            refresh(); log("[3x3] Scramble aplicado.")
        except Exception as e:
            messagebox.showerror("Scramble", str(e))

    def facelets_current():
        if edit_mode.get():
            # validar 9 por color
            counts={f:0 for f in ORDER_FACELETS}
            for f in ORDER_FACELETS:
                for r in range(3):
                    for c in range(3):
                        counts[manual[f][r][c]]+=1
            if any(v!=9 for v in counts.values()):
                raise ValueError(f"Estado inválido (colores != 9): {counts}")
            return letters_to_facelets(manual)
        else:
            return letters_to_facelets(pycuber_to_letters(cube))

    def solve():
        nonlocal anim_moves, anim_idx, cube
        out.config(state="normal"); out.delete("1.0","end"); out.config(state="disabled")
        kind=cube_type.get()
        if kind!="3x3":
            log(HybridSolver(kind).solve(scramble_var.get().strip())); return
        try:
            facelets=facelets_current()
            solver=Kociemba3x3Solver()
            sol=solver.solve_from_facelets(facelets)
            moves=parse_moves(sol); log(f"[3x3] Solución: {sol}"); log(f"Movimientos: {len(moves)}")

            # preparar animación: partir del estado scrambled (inverso de moves)
            inv=invert_moves(moves)
            cube=pc.Cube()
            if inv: cube(pc.Formula(" ".join(inv)))
            refresh()
            anim_moves[:]=moves; anim_idx=0
        except Exception as e:
            messagebox.showerror("Resolver", str(e))

    def step_animation():
        nonlocal anim_idx,cube
        if anim_idx>=len(anim_moves): return
        mv=anim_moves[anim_idx]
        try: cube(pc.Formula(mv)); refresh()
        except Exception as e:
            messagebox.showerror("Animación", f"Movimiento inválido: {mv}\n{e}"); return
        anim_idx+=1
        if anim_idx<len(anim_moves): root.after(anim_speed_ms, step_animation)

    def animate_solution():
        if not anim_moves:
            messagebox.showinfo("Animación","Primero tocá 'Resolver'."); return
        nonlocal anim_idx,cube
        inv=invert_moves(anim_moves); cube=pc.Cube()
        if inv: cube(pc.Formula(" ".join(inv)))
        refresh(); anim_idx=0; root.after(anim_speed_ms, step_animation)

    def open_3d():
        """Abrir el viewer 3D con el estado 'scrambled' y la solución (si existe)."""
        try:
            # estado a mostrar en 3D: el “scrambled” actual (depende del modo)
            if edit_mode.get():
                state_letters = manual
                # si hay solución: moves = solución; el viewer reproduce con ESPACIO
                moves = anim_moves[:] if anim_moves else []
            else:
                state_letters = pycuber_to_letters(cube)
                moves = anim_moves[:] if anim_moves else []
            show_cube_3d(state_letters, moves=moves, speed=0.5)
        except Exception as e:
            messagebox.showerror("3D", str(e))

    # Botones
    ttk.Button(left, text="Aplicar Scramble", command=apply_scramble)\
        .grid(row=4, column=0, pady=6, sticky="w")
    ttk.Button(left, text="Resolver", command=solve)\
        .grid(row=4, column=1, pady=6, sticky="w")

    ttk.Button(left, text="Animar solución", command=animate_solution)\
        .grid(row=5, column=0, pady=6, sticky="w")
    ttk.Button(left, text="Siguiente paso", command=step_animation)\
        .grid(row=5, column=1, pady=6, sticky="w")

    ttk.Button(left, text="Ver en 3D (ESPACIO = play)", command=open_3d)\
        .grid(row=7, column=0, columnspan=2, pady=6)

    ttk.Button(left, text="Reiniciar cubo", command=reset_all)\
        .grid(row=8, column=0, columnspan=2, pady=6)

    refresh()
    root.mainloop()
