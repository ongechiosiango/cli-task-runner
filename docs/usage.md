# Usage Guide

## Config format

Tasks are defined in a JSON file (default: `tasks.json`):

    {
      "tasks": {
        "build": {
          "command": "python -m build",
          "description": "Build the distribution"
        },
        "test": {
          "command": "pytest -v",
          "depends_on": ["build"]
        }
      }
    }

## List tasks

    cli-task-runner list

## Run a single task

    cli-task-runner run test

## Run multiple tasks

    cli-task-runner run build test

Dependencies are resolved automatically, and each task runs only once even
if multiple requested tasks share a dependency.

## Custom config path

    cli-task-runner run test --config ./ci/tasks.json

## Continue past failures

    cli-task-runner run build test --continue-on-error

## Exit codes

- `0` — all tasks succeeded
- `1` — config error or dependency cycle
- `2` — one or more tasks failed
