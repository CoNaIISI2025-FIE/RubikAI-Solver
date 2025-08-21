# gui/viewer3d.py
import pyglet
# fuerza perfil "compatibility" 2.1 para que funcionen glMatrixMode & cia
pyglet.options['gl_profile'] = 'compatibility'
pyglet.options['gl_version'] = '2.1'
pyglet.options['vsync'] = True

from pyglet.window import key
# Usamos PyOpenGL en lugar de pyglet.gl para las funciones de OpenGL
from OpenGL.GL import (
    glEnable, glClearColor, glClear, glMatrixMode, glLoadIdentity,
    glRotatef, glBegin, glEnd, glVertex3f, glColor3f, GL_COLOR_BUFFER_BIT,
    GL_DEPTH_BUFFER_BIT, GL_DEPTH_TEST, GL_PROJECTION, GL_MODELVIEW, GL_QUADS
)
from OpenGL.GLU import gluPerspective, gluLookAt
import pycuber as pc

COLORS = {
    "U": (1.0, 1.0, 1.0),
    "R": (1.0, 0.2, 0.2),
    "F": (0.0, 0.8, 0.4),
    "D": (1.0, 1.0, 0.2),
    "L": (1.0, 0.6, 0.0),
    "B": (0.2, 0.6, 1.0),
}
ORDER_FACELETS = "URFDLB"

class Cube3DWindow(pyglet.window.Window):
    def __init__(self, state_letters, moves=None, speed=0.6):
        super().__init__(width=900, height=640, caption="Rubik 3D Viewer", resizable=True, vsync=True)
        glEnable(GL_DEPTH_TEST)
        glClearColor(0.12, 0.12, 0.12, 1.0)

        self.rot_x = -25.0
        self.rot_y = -35.0

        self.cube = pc.Cube()
        self.state_letters = state_letters  # net inicial (letras por sticker)
        self.moves = moves or []
        self.speed = speed
        self.move_idx = 0

        pyglet.clock.schedule_interval(self.on_update, 1/60)

    def on_draw(self):
        self.clear()
        glClear(GL_COLOR_BUFFER_BIT | GL_DEPTH_BUFFER_BIT)

        # Proyección
        glMatrixMode(GL_PROJECTION)
        glLoadIdentity()
        aspect = self.width / float(max(1, self.height))
        gluPerspective(45.0, aspect, 0.1, 100.0)

        # Vista
        glMatrixMode(GL_MODELVIEW)
        glLoadIdentity()
        gluLookAt(0, 0, 8.5, 0, 0, 0, 0, 1, 0)

        glRotatef(self.rot_x, 1, 0, 0)
        glRotatef(self.rot_y, 0, 1, 0)

        self._draw_cube()

    def on_update(self, dt):  # no-op, pero mantiene el loop activo
        pass

    def on_mouse_drag(self, x, y, dx, dy, buttons, modifiers):
        self.rot_y += dx * 0.4
        self.rot_x -= dy * 0.4

    def on_key_press(self, symbol, modifiers):
        if symbol == key.ESCAPE:
            self.close()
        elif symbol == key.SPACE and self.moves:
            self.move_idx = 0
            pyglet.clock.schedule_interval(self._play_step, self.speed)

    def _play_step(self, dt):
        if self.move_idx >= len(self.moves):
            pyglet.clock.unschedule(self._play_step)
            return
        mv = self.moves[self.move_idx]
        try:
            self.cube(pc.Formula(mv))
        except Exception:
            pyglet.clock.unschedule(self._play_step)
            return
        self.move_idx += 1

    # ---------- helpers ----------
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

    def _letters_from_cube(self):
        cmap = {}
        for f in ORDER_FACELETS:
            m = self._mat(self.cube, f)
            cmap[m[1][1]] = f
        letters = {}
        for f in ORDER_FACELETS:
            m = self._mat(self.cube, f)
            letters[f] = [[cmap[m[r][c]] for c in range(3)] for r in range(3)]
        return letters

    def _draw_cube(self):
        # Si ya aplicamos pasos, usamos el estado real del pc.Cube.
        letters = self._letters_from_cube() if self.move_idx > 0 else self.state_letters

        size = 1.8
        cell = size / 3.0

        # U (y+)
        self._draw_face(letters["U"], origin=(-size/2,  size/2, 0), right=( cell,0,0), down=(0,0, cell))
        # D (y-)
        self._draw_face(letters["D"], origin=(-size/2, -size/2, 0), right=( cell,0,0), down=(0,0,-cell))
        # F (z+)
        self._draw_face(letters["F"], origin=(-size/2, 0,  size/2), right=( cell,0,0), down=(0,-cell,0))
        # B (z-)
        self._draw_face(letters["B"], origin=( size/2, 0, -size/2), right=(-cell,0,0), down=(0,-cell,0))
        # R (x+)
        self._draw_face(letters["R"], origin=( size/2, 0,  size/2), right=(0,0,-cell), down=(0,-cell,0))
        # L (x-)
        self._draw_face(letters["L"], origin=(-size/2, 0, -size/2), right=(0,0, cell), down=(0,-cell,0))

    def _draw_face(self, mat, origin, right, down):
        ox, oy, oz = origin
        rx, ry, rz = right
        dx, dy, dz = down
        gap = 0.06  # marco entre stickers

        glBegin(GL_QUADS)
        for r in range(3):
            for c in range(3):
                letter = mat[r][c]
                cr, cg, cb = COLORS.get(letter, (0.6, 0.6, 0.6))

                # esquinas del quad sin gap
                x0 = ox + rx*c + dx*r;     y0 = oy + ry*c + dy*r;     z0 = oz + rz*c + dz*r
                x1 = x0 + rx;              y1 = y0 + ry;              z1 = z0 + rz
                x2 = x0 + rx + dx;         y2 = y0 + ry + dy;         z2 = z0 + rz + dz
                x3 = x0 + dx;              y3 = y0 + dy;              z3 = z0 + dz

                # encoger hacia el centro para separar stickers
                def lerp(a, b, t): return (a[0]+(b[0]-a[0])*t, a[1]+(b[1]-a[1])*t, a[2]+(b[2]-a[2])*t)
                p0 = lerp((x0,y0,z0), (x2,y2,z2), gap)
                p1 = lerp((x1,y1,z1), (x3,y3,z3), gap)
                p2 = lerp((x2,y2,z2), (x0,y0,z0), gap)
                p3 = lerp((x3,y3,z3), (x1,y1,z1), gap)

                glColor3f(cr, cg, cb)
                glVertex3f(*p0); glVertex3f(*p1); glVertex3f(*p2); glVertex3f(*p3)
        glEnd()

def show_cube_3d(state_letters, moves=None, speed=0.6):
    win = Cube3DWindow(state_letters, moves=moves, speed=speed)
    pyglet.app.run()
