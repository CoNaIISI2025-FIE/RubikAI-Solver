# gui/app.py
import tkinter as tk
from tkinter import ttk, messagebox
import pycuber as pc

from solver.kociemba_solver import Kociemba3x3Solver
from solver.hybrid_solver import HybridSolver

SUPPORTED = ["3x3", "4x4", "5x5", "Pyraminx", "Megaminx"]

# Colores para dibujar el net (podés ajustarlos)
FACE_COLOR = {
    "U": "#FFFFFF",  # blanco
    "R": "#FF4D4D",  # rojo
    "F": "#00CC66",  # verde
    "D": "#FFFF33",  # amarillo
    "L": "#FF9900",  # naranja
    "B": "#3399FF",  # azul
}

# Orden y disposición del net (U al tope, luego fila L F R B, y D abajo)
ORDER = "U L F R B D"  # para dibujar
# offsets por cara en la grilla (col, fila) de bloques 3x3
FACE_OFFSETS = {
    "U": (3, 0),
    "L": (0, 3),
    "F": (3, 3),
    "R": (6, 3),
    "B": (9, 3),
    "D": (3, 6),
}

CELL = 24   # tamaño de cada sticker (px)
PAD  = 2    # separación entre stickers (px)

def _face_matrix(cube, f):
    """Devuelve la matriz 3x3 de colores de la cara f (soporta variantes de pycuber)."""
    faces = getattr(cube, "faces", None)
    if faces is not None:
        face = faces[f]
        return [[str(face[r][c]) for c in range(3)] for r in range(3)]
    gf = getattr(cube, "get_face", None)
    if gf is not None:
        face = gf(f)
        return [[str(face[r][c]) for c in range(3)] for r in range(3)]
    raise RuntimeError("No se pudo leer la cara del cubo con pycuber.")

def _color_to_letter_map(cube):
    """Mapea color del centro -> letra de cara (U,R,F,D,L,B) para un cubo dado."""
    # Obtenemos letras de cara en el alfabeto de pycuber: U,R,F,D,L,B
    # Para cada cara, tomamos el color del centro, y lo asociamos a su letra
    mapping = {}
    for f in "URFDLB":
        mat = _face_matrix(cube, f)
        center = mat[1][1]
        mapping[center] = f
    return mapping

def _to_face_letter(color_char, color_map):
    """Convierte un char de color de pycuber (ej 'w','y','g','r','b','o') a letra de cara mediante el mapping."""
    # color_char ya es un string (p.ej 'w'), buscamos a qué letra corresponde en este cubo
    return color_map[color_char]

def draw_cube(canvas: tk.Canvas, cube: pc.Cube):
    """
    Dibuja el cubo como un net 2D en un Canvas (solo 3x3).
    """
    canvas.delete("all")
    # Mapeo color->letra (para pintar por letra de centro)
    color_map = _color_to_letter_map(cube)

    for face_letter in ORDER.split():
        off_col, off_row = FACE_OFFSETS[face_letter]
        mat = _face_matrix(cube, face_letter)
        for r in range(3):
            for c in range(3):
                # Convertimos color a letra (según el centro)
                face_of_sticker = _to_face_letter(mat[r][c], color_map)
                fill = FACE_COLOR.get(face_of_sticker, "#999999")

                x0 = (off_col + c) * (CELL + PAD)
                y0 = (off_row + r) * (CELL + PAD)
                x1 = x0 + CELL
                y1 = y0 + CELL

                canvas.create_rectangle(x0, y0, x1, y1, fill=fill, outline="#333333", width=2)

def parse_moves(seq: str):
    """
    Tokeniza secuencia tipo: "U R2 F U' L2 D" -> ["U","R2","F","U'","L2","D"]
    """
    parts = [p for p in seq.replace(",", " ").split() if p]
    return parts

def launch_app():
    root = tk.Tk()
    root.title("IA Rubik Solver")
    # Hacemos espacio horizontal para el canvas del net
    root.geometry("900x480")

    main = ttk.Frame(root, padding=10)
    main.pack(fill="both", expand=True)

    # ---- Panel izquierdo: controles y salida de texto
    left = ttk.Frame(main, padding=5)
    left.pack(side="left", fill="y")

    ttk.Label(left, text="Tipo de cubo:").grid(row=0, column=0, sticky="w")
    cube_type = tk.StringVar(value="3x3")
    cmb = ttk.Combobox(left, textvariable=cube_type, values=SUPPORTED, state="readonly", width=18)
    cmb.grid(row=0, column=1, sticky="w", padx=5)

    ttk.Label(left, text="Scramble:").grid(row=1, column=0, sticky="w", pady=(6, 0))
    scramble_var = tk.StringVar(value="U R2 F U' L2 D")
    ent = ttk.Entry(left, textvariable=scramble_var, width=32)
    ent.grid(row=1, column=1, sticky="w", padx=5, pady=(6, 0))

    out = tk.Text(left, height=20, width=40, state="disabled")
    out.grid(row=3, column=0, columnspan=2, pady=8)

    def log(msg):
        out.configure(state="normal")
        out.insert("end", msg + "\n")
        out.see("end")
        out.configure(state="disabled")

    # ---- Panel derecho: Canvas (visualización del cubo)
    right = ttk.Frame(main, padding=5)
    right.pack(side="left", fill="both", expand=True)

    # Net ocupa (12 columnas x 9 filas) de celdas (ver FACE_OFFSETS).
    canvas_w = (12 * (CELL + PAD))
    canvas_h = (9 * (CELL + PAD))
    cvs = tk.Canvas(right, width=canvas_w, height=canvas_h, bg="#1e1e1e", highlightthickness=0)
    cvs.pack(fill="both", expand=True)

    # Estado del cubo para la animación (3x3)
    cube = pc.Cube()
    anim_moves = []
    anim_idx = 0
    anim_speed_ms = 350  # velocidad de animación (ms entre movimientos)

    def reset_cube():
        nonlocal cube, anim_moves, anim_idx
        cube = pc.Cube()
        anim_moves = []
        anim_idx = 0
        draw_cube(cvs, cube)

    reset_cube()  # dibujar resuelto al inicio

    def apply_scramble():
        """Aplica el scramble actual al cubo y lo dibuja."""
        nonlocal cube
        try:
            cube = pc.Cube()
            seq = pc.Formula(scramble_var.get().strip())
            cube(seq)
            draw_cube(cvs, cube)
            log("[3x3] Scramble aplicado.")
        except Exception as e:
            messagebox.showerror("Error", f"Scramble inválido: {e}")

    def solve():
        """Resuelve (3x3 con kociemba) y muestra la solución."""
        nonlocal anim_moves, anim_idx, cube

        out.configure(state="normal")
        out.delete("1.0", "end")
        out.configure(state="disabled")

        kind = cube_type.get()
        scr = scramble_var.get().strip()
        if not scr:
            messagebox.showwarning("Scramble vacío", "Ingresá un scramble (ej: U R U' R').")
            return

        if kind != "3x3":
            msg = HybridSolver(kind).solve(scr)
            log(msg)
            return

        try:
            # Reset + aplicar scramble (para que lo que se ve coincida)
            cube = pc.Cube()
            cube(pc.Formula(scr))
            draw_cube(cvs, cube)

            # Resolver
            solver = Kociemba3x3Solver()
            sol = solver.solve_from_scramble(scr)
            log(f"[3x3] Scramble: {scr}")
            log(f"[3x3] Solución: {sol}")
            log(f"Movimientos: {len(sol.split())}")

            # Preparar animación
            anim_moves = parse_moves(sol)
            anim_idx = 0
        except Exception as e:
            messagebox.showerror("Error", str(e))

    def step_animation():
        """Aplica un movimiento de la solución y redibuja."""
        nonlocal anim_idx, cube
        if anim_idx >= len(anim_moves):
            return  # terminó
        mv = anim_moves[anim_idx]
        try:
            # Aplicamos la notación directamente con PyCuber
            cube(pc.Formula(mv))
            draw_cube(cvs, cube)
        except Exception as e:
            messagebox.showerror("Animación", f"Movimiento inválido: {mv}\n{e}")
            return
        anim_idx += 1
        # programar el siguiente paso
        if anim_idx < len(anim_moves):
            root.after(anim_speed_ms, step_animation)

    def animate_solution():
        """Lanza la animación completa (si hay solución calculada)."""
        if not anim_moves:
            messagebox.showinfo("Animación", "Primero tocá 'Resolver' para obtener la solución.")
            return
        # Reiniciar al estado scrambled para ver la animación desde el inicio:
        try:
            cube_reset = pc.Cube()
            cube_reset(pc.Formula(scramble_var.get().strip()))
            # reemplazamos el cubo visual por el scrambled
            nonlocal cube, anim_idx
            cube = cube_reset
            anim_idx = 0
            draw_cube(cvs, cube)
            root.after(anim_speed_ms, step_animation)
        except Exception as e:
            messagebox.showerror("Animación", f"No pude reiniciar al scramble: {e}")

    # Botones
    row = 2
    ttk.Button(left, text="Aplicar Scramble", command=apply_scramble).grid(row=row, column=0, pady=6, sticky="w")
    ttk.Button(left, text="Resolver", command=solve).grid(row=row, column=1, pady=6, sticky="w")
    row += 1
    ttk.Button(left, text="Animar Solución", command=animate_solution).grid(row=row, column=0, pady=6, sticky="w")
    ttk.Button(left, text="Reiniciar Cubo", command=reset_cube).grid(row=row, column=1, pady=6, sticky="w")
    row += 1
    ttk.Button(left, text="Salir", command=root.destroy).grid(row=row, column=0, columnspan=2, pady=6)

    root.mainloop()
