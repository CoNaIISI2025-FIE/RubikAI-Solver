# 🧩 IA para Resolver Cubo de Rubik

Este proyecto implementa una combinación de **Deep Learning** y **heurísticas** para resolver variantes del cubo de Rubik. 
Actualmente incluye un *baseline* funcional para **3×3** mediante el algoritmo de **Kociemba**, una **GUI** con Tkinter y
ganchos (hooks) listos para integrar modelos en **PyTorch** (policy network / RL) y soportar otros cubos (4×4, 5×5, Pyraminx, Megaminx).

> Proyecto académico – Facultad de Ingeniería del Ejército (UNDEF).

---

## 🚀 Tecnologías

- Python 3.x
- PyTorch (`torch`)
- Kociemba (`kociemba`)
- PyCuber (`pycuber`)
- NumPy (`numpy`)
- Tkinter (GUI) — *se instala con el sistema en Linux*
- tqdm, sympy, networkx (utilidades)

---

## 📂 Estructura del Repo

```
ia/
│── main.py
│── requirements.txt
│── README.md
│
├── gui/
│   └── app.py                  # Interfaz gráfica (Tkinter)
│
├── solver/
│   ├── base_solver.py          # Interfaz común de solvers
│   ├── kociemba_solver.py      # Baseline 3×3 con Kociemba
│   └── hybrid_solver.py        # Hook p/ DL + heurísticas (otros cubos)
│
├── utils/
│   ├── scramble_utils.py       # Normalización/validación de scrambles
│   └── pycuber_adapter.py      # Scramble -> facelets (URFDLB) p/ Kociemba
│
├── models/
│   └── policy_net.py           # Esqueleto de red de política (PyTorch)
│
├── data/                       # (opcional) generación de datasets
│   └── generate_data.py
│
└── tests/                      # tests mínimos (opcional)
    ├── test_model.py
    └── test_solver.py
```

---

## ⚙️ Instalación

### 1) Clonar

**SSH (recomendado)**
```bash
git clone git@github.com:TPIARUBIK/ia.git
cd ia
```

**HTTPS**
```bash
git clone https://github.com/TPIARUBIK/ia.git
cd ia
```

### 2) Crear y activar entorno virtual

**Linux / macOS**
```bash
python3 -m venv .venv
source .venv/bin/activate
```

**Windows (PowerShell)**
```powershell
python -m venv .venv
.\.venv\Scripts\Activate.ps1
```

> Verás `(.venv)` al inicio de la línea si quedó activado.

### 3) Dependencias

```bash
python -m pip install --upgrade pip
python -m pip install -r requirements.txt
```

> **Tkinter en Linux/WSL:** se instala con el gestor del sistema, no con pip.  
> Ubuntu/Debian: `sudo apt install python3-tk`

---

## ▶️ Ejecución

### GUI (Interfaz Gráfica)
```bash
python main.py
# o explícito:
python main.py gui
```
- Elegí el tipo de cubo (por ahora 3×3 es el que resuelve).
- Ingresá un *scramble* (ej: `U R2 F U' L2 D F2 R B U2`).
- Presioná **Resolver** para obtener la secuencia.

### CLI (Modo Consola)
```bash
python main.py cli --cube-type 3x3 --scramble "U R U' R'"
```

---

## 🧪 Pruebas Rápidas (opcional)

```bash
pytest -q      # si añadís pytest al requirements
```

---

## 🔧 Notas y Troubleshooting

- **`ModuleNotFoundError: No module named ...`**  
  Asegurate de que el venv esté activado y usá siempre `python -m pip ...`.

- **GUI en WSL:** necesitás **WSLg** (Windows 11) o corré en Windows nativo.  
  Si no tenés entorno gráfico, usá el modo **CLI**.

- **Kociemba requiere facelets URFDLB:** `utils/pycuber_adapter.py` genera el string correcto
  aplicando el *scramble* sobre un cubo resuelto con PyCuber y mapeando colores por centros.

---

## 🧠 Roadmap (sugerido)

- Encoder estado → embedding y *behavior cloning* desde soluciones Kociemba
- DQN/PPO para priorizar movimientos (policy/value)
- **HybridSolver**: Beam Search/MCTS con prior de la policy
- Soporte completo 4×4/5×5/Pyraminx/Megaminx

---

## 👥 Autores

Equipo **TPIARUBIK** – Ingeniería en Informática (UNDEF).

---

## 📄 Licencia

MIT (o la que defina el equipo).
