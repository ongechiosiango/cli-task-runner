"""Command-line interface for CLI Task Runner."""

from __future__ import annotations

import argparse

from rich.console import Console

from .config import ConfigError, load_tasks
from .reporter import print_results, print_task_list
from .runner import CycleError, resolve_order, run_tasks

console = Console()


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(
        prog="cli-task-runner",
        description="Define named shell tasks in a JSON file and run them with dependency ordering.",
    )
    sub = parser.add_subparsers(dest="cmd", required=True)

    list_p = sub.add_parser("list", help="List all available tasks.")
    list_p.add_argument("--config", "-c", default="tasks.json",
                        help="Path to the tasks config (default: tasks.json)")

    run_p = sub.add_parser("run", help="Run one or more tasks.")
    run_p.add_argument("task", nargs="+", help="Task name(s) to run.")
    run_p.add_argument("--config", "-c", default="tasks.json",
                       help="Path to the tasks config (default: tasks.json)")
    run_p.add_argument("--continue-on-error", action="store_true",
                       help="Continue running tasks even if one fails.")

    return parser


def main() -> int:
    args = build_parser().parse_args()

    try:
        tasks = load_tasks(args.config)
    except ConfigError as exc:
        console.print(f"[bold red]Config error:[/bold red] {exc}")
        return 1

    if args.cmd == "list":
        print_task_list(tasks)
        return 0

    # args.cmd == "run"
    try:
        order = resolve_order(tasks, args.task)
    except CycleError as exc:
        console.print(f"[bold red]Error:[/bold red] {exc}")
        return 1

    results = run_tasks(tasks, order, stop_on_error=not args.continue_on_error)
    print_results(results)

    return 0 if all(r.success for r in results) else 2


if __name__ == "__main__":
    raise SystemExit(main())
