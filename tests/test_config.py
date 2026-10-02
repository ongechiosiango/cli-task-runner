"""Tests for the config loader."""

import json

import pytest

from cli_task_runner.config import ConfigError, load_tasks


def _write(tmp_path, data):
    p = tmp_path / "tasks.json"
    p.write_text(json.dumps(data))
    return str(p)


def test_load_valid(tmp_path):
    path = _write(tmp_path, {
        "tasks": {
            "build": {"command": "echo build"},
            "test": {"command": "echo test", "depends_on": ["build"]},
        }
    })
    tasks = load_tasks(path)
    assert set(tasks.keys()) == {"build", "test"}
    assert tasks["test"].depends_on == ["build"]


def test_load_missing_file(tmp_path):
    with pytest.raises(ConfigError, match="not found"):
        load_tasks(str(tmp_path / "nope.json"))


def test_load_invalid_json(tmp_path):
    p = tmp_path / "bad.json"
    p.write_text("{not json")
    with pytest.raises(ConfigError, match="Invalid JSON"):
        load_tasks(str(p))


def test_load_missing_tasks_key(tmp_path):
    path = _write(tmp_path, {"foo": "bar"})
    with pytest.raises(ConfigError, match="'tasks' key"):
        load_tasks(path)


def test_load_task_missing_command(tmp_path):
    path = _write(tmp_path, {"tasks": {"x": {"description": "no cmd"}}})
    with pytest.raises(ConfigError, match="missing a 'command'"):
        load_tasks(path)


def test_load_unknown_dependency(tmp_path):
    path = _write(tmp_path, {
        "tasks": {"a": {"command": "echo a", "depends_on": ["nope"]}}
    })
    with pytest.raises(ConfigError, match="unknown task"):
        load_tasks(path)
