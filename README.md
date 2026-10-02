# CLI Task Runner

[![CI](https://github.com/ongechiosiango/cli-task-runner/actions/workflows/ci.yml/badge.svg)](https://github.com/ongechiosiango/cli-task-runner/actions/workflows/ci.yml)
[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](LICENSE)
[![Python 3.9+](https://img.shields.io/badge/python-3.9%2B-blue.svg)](https://www.python.org/downloads/)

Define named shell tasks in a JSON file and run them with dependency ordering.

## Features

- Simple JSON config defines named tasks and their shell commands.
- `depends_on` field for explicit dependency ordering.
- Topological sort ensures each task runs exactly once.
- Cycle detection with a clear error.
- `list` subcommand shows all tasks with their commands and dependencies.
- Rich terminal output with a per-task pass/fail report.

## Installation

From source:

    git clone git@github.com:ongechiosiango/cli-task-runner.git
    cd cli-task-runner
    python3 -m venv venv
    source venv/bin/activate
    pip install -e ".[dev]"

## Quick start

Create a `tasks.json`:

    {
      "tasks": {
        "build": {"command": "python -m build"},
        "test":  {"command": "pytest -v", "depends_on": ["build"]}
      }
    }

List tasks:

    cli-task-runner list

Run a task and its dependencies:

    cli-task-runner run test

See docs/usage.md for more.

## Development

    pip install -e ".[dev]"
    pytest -v

## Contributing

See CONTRIBUTING.md.

## License

MIT - see LICENSE.
