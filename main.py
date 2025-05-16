import matplotlib.pyplot as plt
import numpy as np

NUM_CIRCULOS = 2
PUNTOS_POR_CIRCULO = 6
RADIO = 2
ESPACIADO = 6
COLORES = ['red', 'blue', 'green', 'yellow', 'cyan', 'magenta']

circulos = []
for i in range(NUM_CIRCULOS):
    cx = i * ESPACIADO
    cy = 0
    angulos = np.linspace(0, 2 * np.pi, PUNTOS_POR_CIRCULO, endpoint=False)
    puntos = [(cx + RADIO * np.cos(a), cy + RADIO * np.sin(a)) for a in angulos]
    colores = np.random.choice(COLORES, PUNTOS_POR_CIRCULO, replace=False)
    circulos.append({'centro': [cx, cy], 'puntos': puntos, 'colores': list(colores)})

fig, ax = plt.subplots()
ax.set_aspect('equal')
ax.set_xlim(-2, ESPACIADO * NUM_CIRCULOS)
ax.set_ylim(-RADIO * 2.5, RADIO * 2.5)
ax.axis('off')

def dibujar():
    ax.clear()
    ax.set_aspect('equal')
    ax.set_xlim(-2, ESPACIADO * NUM_CIRCULOS)
    ax.set_ylim(-RADIO * 2.5, RADIO * 2.5)
    ax.axis('off')
    for c in circulos:
        cx, cy = c['centro']
        t = np.linspace(0, 2 * np.pi, 100)
        x = cx + RADIO * np.cos(t)
        y = cy + RADIO * np.sin(t)
        ax.plot(x, y, '--', color='gray')
        angulos = np.linspace(0, 2 * np.pi, PUNTOS_POR_CIRCULO, endpoint=False)
        for a, color in zip(angulos, c['colores']):
            px = cx + RADIO * np.cos(a)
            py = cy + RADIO * np.sin(a)
            ax.plot(px, py, 'o', color=color, markersize=12)
    fig.canvas.draw_idle()

def on_click(event):
    if event.inaxes != ax:
        return
    click_x, click_y = event.xdata, event.ydata
    for i, c in enumerate(circulos):
        cx, cy = c['centro']
        dist = np.hypot(click_x - cx, click_y - cy)
        if dist <= RADIO:
            print(f'Clic en círculo {i}, rotando colores...')
            circulos[i]['colores'] = circulos[i]['colores'][-1:] + circulos[i]['colores'][:-1]
            dibujar()
            break

fig.canvas.mpl_connect('button_press_event', on_click)

dibujar()
plt.show()
