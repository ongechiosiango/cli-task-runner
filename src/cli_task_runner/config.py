"""Load and validate a task config from JSON."""

from __future__ import annotations

import json
from dataclasses import dataclass, field
from pathlib import Path


class ConfigError(Exception):
    """Raised when a config file is missing, unreadable, or invalid."""


@dataclass
class Task:
    """A single named task."""

    name: str
    command: str
    description: str = ""
    depends_on: list = field(default_factory=list)


def load_tasks(path: str) -> dict:
    """Load tasks from a JSON file.

    Expected format:
        {
          "tasks": {
            "build": {"command": "make", "description": "Build the project"},
            "test":  {"command": "pytest", "depends_on": ["build"]}
          }
        }

    Returns a dict of {task_name: Task}.
    """
    p = Path(path)
    if not p.exists():
        raise ConfigError(f"Config file not found: {path}")
    if not p.is_file():
        raise ConfigError(f"Not a file: {path}")

    try:
        raw = json.loads(p.read_text(encoding="utf-8"))
    except json.JSONDecodeError as exc:
        raise ConfigError(f"Invalid JSON in {path}: {exc}") from exc
    except OSError as exc:
        raise ConfigError(f"Could not read {path}: {exc}") from exc

    if not isinstance(raw, dict) or "tasks" not in raw:
        raise ConfigError("Config must be a JSON object with a 'tasks' key.")

    raw_tasks = raw["tasks"]
    if not isinstance(raw_tasks, dict) or not raw_tasks:
        raise ConfigError("'tasks' must be a non-empty object.")

    tasks = {}
    for name, spec in raw_tasks.items():
        if not isinstance(spec, dict):
            raise ConfigError(f"Task {name!r} must be an object.")
        if "command" not in spec or not isinstance(spec["command"], str):
            raise ConfigError(f"Task {name!r} is missing a 'command' string.")

        depends_on = spec.get("depends_on", [])
        if not isinstance(depends_on, list) or not all(isinstance(d, str) for d in depends_on):
            raise ConfigError(f"Task {name!r} has invalid 'depends_on'.")

        tasks[name] = Task(
            name=name,
            command=spec["command"],
            description=spec.get("description", ""),
            depends_on=list(depends_on),
        )

    # Validate that all dependencies exist
    for task in tasks.values():
        for dep in task.depends_on:
            if dep not in tasks:
                raise ConfigError(
                    f"Task {task.name!r} depends on unknown task {dep!r}."
                )

    return tasks
