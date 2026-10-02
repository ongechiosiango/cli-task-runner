"""Format and display task results using rich."""

from __future__ import annotations

from rich.console import Console
from rich.table import Table

from .config import Task
from .runner import TaskResult

console = Console()


def print_task_list(tasks: dict) -> None:
    """Print all available tasks."""
    console.print()
    console.rule("[bold cyan]Available Tasks[/bold cyan]")

    table = Table(show_header=True, header_style="bold magenta")
    table.add_column("Name", style="cyan", no_wrap=True)
    table.add_column("Command", style="green")
    table.add_column("Depends on", style="yellow")
    table.add_column("Description", style="white")

    for task in sorted(tasks.values(), key=lambda t: t.name):
        table.add_row(
            task.name,
            task.command,
            ", ".join(task.depends_on) if task.depends_on else "-",
            task.description or "-",
        )

    console.print(table)


def print_results(results: list) -> None:
    """Print a summary table of task results."""
    console.print()
    console.rule("[bold cyan]Task Run Report[/bold cyan]")

    table = Table(show_header=True, header_style="bold magenta")
    table.add_column("Task", style="cyan", no_wrap=True)
    table.add_column("Status", no_wrap=True)
    table.add_column("Exit code", style="green")
    table.add_column("Duration (s)", style="green")

    for r in results:
        status = "[green]PASS[/green]" if r.success else "[red]FAIL[/red]"
        table.add_row(r.name, status, str(r.returncode), f"{r.duration_s:.3f}")

    console.print(table)

    # Show stderr for any failures
    for r in results:
        if not r.success and r.stderr.strip():
            console.print(f"\n[bold red]stderr from {r.name}:[/bold red]")
            console.print(r.stderr.strip(), style="red")
