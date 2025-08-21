import tkinter as tk
from tkinter import ttk, messagebox
from solver.kociemba_solver import Kociemba3x3Solver
from solver.hybrid_solver import HybridSolver

SUPPORTED = ["3x3","4x4","5x5","Pyraminx","Megaminx"]

def launch_app():
    root = tk.Tk()
    root.title("IA Rubik Solver")
    root.geometry("600x400")

    frm = ttk.Frame(root, padding=10)
    frm.pack(fill="both", expand=True)

    ttk.Label(frm, text="Tipo de cubo:").grid(row=0, column=0, sticky="w")
    cube_type = tk.StringVar(value="3x3")
    cmb = ttk.Combobox(frm, textvariable=cube_type, values=SUPPORTED, state="readonly")
    cmb.grid(row=0, column=1, padx=5, pady=5)

    ttk.Label(frm, text="Scramble:").grid(row=1, column=0, sticky="w")
    scramble_var = tk.StringVar(value="U R2 F U' L2 D")
    ent = ttk.Entry(frm, textvariable=scramble_var, width=50)
    ent.grid(row=1, column=1, padx=5, pady=5)

    out = tk.Text(frm, height=15, width=70, state="disabled")
    out.grid(row=2, column=0, columnspan=2, pady=10)

    def show(msg):
        out.configure(state="normal")
        out.insert("end", msg + "\n")
        out.see("end")
        out.configure(state="disabled")

    def solve():
        out.configure(state="normal")
        out.delete("1.0","end")
        out.configure(state="disabled")
        kind, scr = cube_type.get(), scramble_var.get()
        try:
            if kind=="3x3":
                sol = Kociemba3x3Solver().solve_from_scramble(scr)
                show(f"[3x3] Scramble: {scr}")
                show(f"[3x3] Solución: {sol}")
                show(f"Movimientos: {len(sol.split())}")
            else:
                res = HybridSolver(kind).solve(scr)
                show(res)
        except Exception as e:
            messagebox.showerror("Error", str(e))

    ttk.Button(frm,text="Resolver",command=solve).grid(row=3, column=0, pady=5)
    ttk.Button(frm,text="Salir",command=root.destroy).grid(row=3, column=1, pady=5)
    root.mainloop()
