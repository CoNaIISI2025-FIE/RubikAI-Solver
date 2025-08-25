import argparse, sys, os

def run_gui():
    from gui.app import launch_app
    launch_app()

def run_console(args):
    from solver.hybrid_solver import HybridSolver
    kind = args.cube_type
    scramble = args.scramble
    solver = HybridSolver(kind)          # <- en vez de Kociemba directo para 3x3
    print(solver.solve(scramble))


def run_train(args):
    from rl.self_play import train_self_play
    device = "cuda" if args.cuda and os.environ.get("CUDA_VISIBLE_DEVICES","") != "" else "cpu"
    train_self_play(
        out_path=args.out,
        device=device,
        steps=args.steps,
        batch_size=args.batch,
        lr=args.lr,
        sims_per_move=args.sims,
        curriculum=(args.scr_min, args.scr_max),
        max_steps=args.max_steps,
        eval_every=args.eval_every,
    )

def main():
    parser = argparse.ArgumentParser(description="IA Rubik Solver")
    sub = parser.add_subparsers(dest="mode")

    sub.add_parser("gui", help="Lanzar interfaz gráfica")
    cli = sub.add_parser("cli", help="Modo consola")
    cli.add_argument("--cube-type", choices=["3x3","4x4","5x5","Pyraminx","Megaminx"], default="3x3")
    cli.add_argument("--scramble", required=True, help="Ej: 'U R U' R''")

    tr = sub.add_parser("train", help="Entrenar self-play (3x3)")
    tr.add_argument("--steps", type=int, default=2000)
    tr.add_argument("--batch", type=int, default=256)
    tr.add_argument("--lr", type=float, default=1e-3)
    tr.add_argument("--sims", type=int, default=128, help="Simulaciones MCTS por jugada")
    tr.add_argument("--scr-min", type=int, default=1)
    tr.add_argument("--scr-max", type=int, default=10)
    tr.add_argument("--max-steps", type=int, default=60)
    tr.add_argument("--eval-every", type=int, default=500)
    tr.add_argument("--out", default="models/checkpoints/pvnet_3x3.pt")
    tr.add_argument("--cuda", action="store_true")

    args = parser.parse_args()

    if args.mode == "gui" or (args.mode is None and ("DISPLAY" in os.environ or sys.platform.startswith("win"))):
        run_gui()
    elif args.mode == "cli":
        run_console(args)
    elif args.mode == "train":
        run_train(args)
    else:
        parser.print_help()

if __name__ == "__main__":
    main()
