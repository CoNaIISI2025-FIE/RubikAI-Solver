# gui/viewer3d.py
import math
import pyglet
from pyglet.gl import *
import pycuber as pc

# Colores por letra de cara
COLORS = {
    "U": (1.0, 1.0, 1.0),   # blanco
    "R": (1.0, 0.2, 0.2),   # rojo
    "F": (0.0, 0.8, 0.4),   # verde
    "D": (1.0, 1.0, 0.2),   # amarillo
    "L": (1.0, 0.6, 0.0),   # naranja
    "B": (0.2, 0.6, 1.0),   # azul
}

ORDER_FACELETS = "URFDLB"

def letters_to_state_matrix(letters):
    # letters: dict {'U': [[...3],...3], 'R':...} -> devolvemos igual
    return letters

def apply_move_to_letters(letters, mv):
    """Aplicar movimiento usando PyCuber y reconvertir a letters (más simple que manejar permutaciones a mano)."""
    cube = pc.Cube()
    # Cargar estado desde letters:
    # Tomamos el estado resuelto y “pintamos” aplicando inverso de solución hasta matchear,
    # pero eso es complejo; más fácil: mantener un pc.Cube() vivo afuera y no usar esta función.
    # Aquí no la usamos activamente; animamos con pc.Cube en el viewer (mejor).
    pass

class Cube3DWindow(pyglet.window.Window):
    def __init__(self, state_letters, moves=None, speed=0.6):
        super().__init__(width=900, height=640, caption="Rubik 3D Viewer", resizable=True)
        glEnable(GL_DEPTH_TEST)
        glClearColor(0.12, 0.12, 0.12, 1.0)

        self.rot_x = -25
        self.rot_y = -35
        self.dragging = False
        self.last_mouse = (0, 0)

        # Guardamos un pc.Cube() y lo seteamos al estado indicado por letters invirtiendo la solución:
        self.cube = pc.Cube()
        # Creamos una solución “inversa” para llevar cubo resuelto -> estado dado:
        # 1) Resolver letters (usamos kociemba en app y traemos moves list desde allí),
        #    acá solo reproducimos la animación de moves sobre un cubo “scrambled”.
        # Para simplificar: app nos pasa 'moves' y antes de abrir 3D ya deja self.cube en estado scrambled.
        self.moves = moves or []
        self.speed = speed
        self.move_idx = 0

        self.state_letters = state_letters  # solo para primer frame
        pyglet.clock.schedule_interval(self.update, 1/60)

    def on_draw(self):
        self.clear()
        # Proyección
        glMatrixMode(GL_PROJECTION)
        glLoadIdentity()
        aspect = self.width / float(max(1, self.height))
        gluPerspective(45.0, aspect, 0.1, 100.0)

        # Vista
        glMatrixMode(GL_MODELVIEW)
        glLoadIdentity()
        gluLookAt(0, 0, 8.5,   0, 0, 0,   0, 1, 0)
        glRotatef(self.rot_x, 1, 0, 0)
        glRotatef(self.rot_y, 0, 1, 0)

        # Dibujar cubo como 6 caras con 3x3 stickers
        self.draw_cube()

    def on_mouse_drag(self, x, y, dx, dy, buttons, modifiers):
        self.rot_y += dx * 0.4
        self.rot_x -= dy * 0.4

    def update(self, dt):
        pass  # animación se puede lanzar desde tecla

    def on_key_press(self, symbol, modifiers):
        # Espacio: animar solución
        if symbol == pyglet.window.key.SPACE and self.moves:
            self.move_idx = 0
            pyglet.clock.schedule_interval(self.play_step, self.speed)

    def play_step(self, dt):
        if self.move_idx >= len(self.moves):
            pyglet.clock.unschedule(self.play_step)
            return
        mv = self.moves[self.move_idx]
        try:
            self.cube(pc.Formula(mv))
        except Exception:
            pyglet.clock.unschedule(self.play_step)
            return
        self.move_idx += 1

    # ------- helpers de dibujo -------
    def draw_cube(self):
        # Si ya aplicamos movimientos sobre pc.Cube(), usamos sus colores reales;
        # si no, dibujamos según state_letters inicial (primer frame)
        letters = self._letters_from_cube() if self.move_idx > 0 else self.state_letters

        # net 3D: dibujamos cada cara como 3x3 quads en su plano 3D
        gap = 0.02
        size = 1.8
        cell = size / 3.0

        # U (y+)
        self._draw_face(letters["U"], origin=(-size/2, size/2, 0), right=(cell, 0, 0), down=(0, 0, cell), normal=(0, -1, 0), face="U")
        # D (y-)
        self._draw_face(letters["D"], origin=(-size/2, -size/2, 0), right=(cell, 0, 0), down=(0, 0, -cell), normal=(0, 1, 0), face="D")
        # F (z+)
        self._draw_face(letters["F"], origin=(-size/2, 0, size/2), right=(cell, 0, 0), down=(0, -cell, 0), normal=(0, 0, -1), face="F")
        # B (z-)
        self._draw_face(letters["B"], origin=(size/2, 0, -size/2), right=(-cell, 0, 0), down=(0, -cell, 0), normal=(0, 0, 1), face="B")
        # R (x+)
        self._draw_face(letters["R"], origin=(size/2, 0, size/2), right=(0, 0, -cell), down=(0, -cell, 0), normal=(-1, 0, 0), face="R")
        # L (x-)
        self._draw_face(letters["L"], origin=(-size/2, 0, -size/2), right=(0, 0, cell), down=(0, -cell, 0), normal=(1, 0, 0), face="L")

    def _letters_from_cube(self):
        # map color -> letter by centers
        cmap = {}
        for f in ORDER_FACELETS:
            mat = self._mat(self.cube, f)
            cmap[mat[1][1]] = f
        letters = {}
        for f in ORDER_FACELETS:
            mat = self._mat(self.cube, f)
            letters[f] = [[cmap[mat[r][c]] for c in range(3)] for r in range(3)]
        return letters

    def _mat(self, cube, f):
        faces = getattr(cube, "faces", None)
        if faces is not None:
            face = faces[f]
            return [[str(face[r][c]) for c in range(3)] for r in range(3)]
        gf = getattr(cube, "get_face", None)
        if gf is not None:
            face = gf(f)
            return [[str(face[r][c]) for c in range(3)] for r in range(3)]
        raise RuntimeError("pycuber no permite leer la cara")

    def _draw_face(self, mat, origin, right, down, normal, face):
        # mat: 3x3 letras de esa cara
        ox, oy, oz = origin
        rx, ry, rz = right
        dx, dy, dz = down
        gap = 0.03

        glBegin(GL_QUADS)
        for r in range(3):
            for c in range(3):
                letter = mat[r][c]
                cr, cg, cb = COLORS.get(letter, (0.6, 0.6, 0.6))

                x0 = ox + rx * c + dx * r
                y0 = oy + ry * c + dy * r
                z0 = oz + rz * c + dz * r

                x1 = x0 + rx
                y1 = y0 + ry
                z1 = z0 + rz

                x2 = x0 + dx + rx
                y2 = y0 + dy + ry
                z2 = z0 + dz + rz

                x3 = x0 + dx
                y3 = y0 + dy
                z3 = z0 + dz

                # encoger un poco para “marcos” entre stickers
                def lerp(a, b, t):
                    return (a[0]+(b[0]-a[0])*t, a[1]+(b[1]-a[1])*t, a[2]+(b[2]-a[2])*t)
                p0 = lerp((x0,y0,z0), (x2,y2,z2), gap)
                p1 = lerp((x1,y1,z1), (x3,y3,z3), gap)
                p2 = lerp((x2,y2,z2), (x0,y0,z0), gap)
                p3 = lerp((x3,y3,z3), (x1,y1,z1), gap)

                glColor3f(cr, cg, cb)
                glVertex3f(*p0); glVertex3f(*p1); glVertex3f(*p2); glVertex3f(*p3)
        glEnd()

def show_cube_3d(state_letters, moves=None, speed=0.6):
    # Creamos ventana y la iniciamos. El usuario puede presionar ESPACIO para animar.
    win = Cube3DWindow(state_letters, moves=moves, speed=speed)
    pyglet.app.run()
