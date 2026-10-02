"""Execute tasks with dependency ordering."""

from __future__ import annotations

import subprocess
import time
from dataclasses import dataclass, field


class CycleError(Exception):
    """Raised when the dependency graph contains a cycle."""


@dataclass
class TaskResult:
    """The result of running one task."""

    name: str
    command: str
    returncode: int
    duration_s: float
    stdout: str = ""
    stderr: str = ""

    @property
    def success(self) -> bool:
        return self.returncode == 0


def resolve_order(tasks: dict, requested: list) -> list:
    """Return a topologically sorted list of task names.

    Includes each requested task and all of its transitive dependencies.
    Raises CycleError if a cycle is detected.
    """
    order = []
    visited = set()
    visiting = set()

    def visit(name: str):
        if name in visited:
            return
        if name in visiting:
            raise CycleError(f"Dependency cycle detected at {name!r}")
        visiting.add(name)

        task = tasks.get(name)
        if task is None:
            raise CycleError(f"Unknown task: {name!r}")
        for dep in task.depends_on:
            visit(dep)

        visiting.remove(name)
        visited.add(name)
        order.append(name)

    for name in requested:
        visit(name)

    return order


def run_tasks(tasks: dict, order: list, stop_on_error: bool = True) -> list:
    """Run tasks in the given order, returning a list of TaskResult.

    If stop_on_error is True, stop after the first failure.
    """
    results = []
    for name in order:
        task = tasks[name]
        start = time.perf_counter()
        try:
            proc = subprocess.run(
                task.command,
                shell=True,
                capture_output=True,
                text=True,
            )
            duration = time.perf_counter() - start
            result = TaskResult(
                name=name,
                command=task.command,
                returncode=proc.returncode,
                duration_s=duration,
                stdout=proc.stdout,
                stderr=proc.stderr,
            )
        except OSError as exc:
            duration = time.perf_counter() - start
            result = TaskResult(
                name=name,
                command=task.command,
                returncode=-1,
                duration_s=duration,
                stderr=str(exc),
            )

        results.append(result)
        if not result.success and stop_on_error:
            break

    return results
