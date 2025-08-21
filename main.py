import argparse, sys, os

def run_gui():
    from gui.app import launch_app
    launch_app()

def run_console(args):
    from solver.kociemba_solver import Kociemba3x3Solver
    from solver.hybrid_solver import HybridSolver

    kind = args.cube_type
    scramble = args.scramble

    if kind == "3x3":
        solver = Kociemba3x3Solver()
        sol = solver.solve_from_scramble(scramble)
        print("Scramble:", scramble)
        print("Solución:", sol)
        print("Longitud:", len(sol.split()))
    else:
        solver = HybridSolver(kind)
        print(solver.solve(scramble))

def main():
    parser = argparse.ArgumentParser(description="IA Rubik Solver")
    sub = parser.add_subparsers(dest="mode")

    sub.add_parser("gui", help="Lanzar interfaz gráfica")
    cli = sub.add_parser("cli", help="Modo consola")
    cli.add_argument("--cube-type", choices=["3x3","4x4","5x5","Pyraminx","Megaminx"], default="3x3")
    cli.add_argument("--scramble", required=True, help="Ej: 'U R U' R''")

    args = parser.parse_args()

    if args.mode == "gui" or (args.mode is None and ("DISPLAY" in os.environ or sys.platform.startswith("win"))):
        run_gui()
    elif args.mode == "cli":
        run_console(args)
    else:
        parser.print_help()

if __name__ == "__main__":
    main()
