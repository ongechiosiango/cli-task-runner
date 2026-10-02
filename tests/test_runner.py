"""Tests for the task runner."""

import pytest

from cli_task_runner.config import Task
from cli_task_runner.runner import (
    CycleError,
    resolve_order,
    run_tasks,
)


def _t(name, deps=None):
    return Task(name=name, command=f"echo {name}", depends_on=deps or [])


def test_resolve_order_linear():
    tasks = {
        "a": _t("a"),
        "b": _t("b", ["a"]),
        "c": _t("c", ["b"]),
    }
    order = resolve_order(tasks, ["c"])
    assert order == ["a", "b", "c"]


def test_resolve_order_diamond():
    tasks = {
        "a": _t("a"),
        "b": _t("b", ["a"]),
        "c": _t("c", ["a"]),
        "d": _t("d", ["b", "c"]),
    }
    order = resolve_order(tasks, ["d"])
    # a must be before b and c; d must be last
    assert order.index("a") < order.index("b")
    assert order.index("a") < order.index("c")
    assert order[-1] == "d"


def test_resolve_order_cycle():
    tasks = {
        "a": _t("a", ["b"]),
        "b": _t("b", ["a"]),
    }
    with pytest.raises(CycleError, match="cycle"):
        resolve_order(tasks, ["a"])


def test_resolve_order_unknown():
    with pytest.raises(CycleError, match="Unknown"):
        resolve_order({}, ["nope"])


def test_run_tasks_success():
    tasks = {
        "ok": Task(name="ok", command="true"),
    }
    results = run_tasks(tasks, ["ok"])
    assert len(results) == 1
    assert results[0].success is True
    assert results[0].returncode == 0


def test_run_tasks_failure_stops_by_default():
    tasks = {
        "bad": Task(name="bad", command="false"),
        "after": Task(name="after", command="true"),
    }
    results = run_tasks(tasks, ["bad", "after"], stop_on_error=True)
    assert len(results) == 1
    assert results[0].success is False


def test_run_tasks_continue_on_error():
    tasks = {
        "bad": Task(name="bad", command="false"),
        "after": Task(name="after", command="true"),
    }
    results = run_tasks(tasks, ["bad", "after"], stop_on_error=False)
    assert len(results) == 2
    assert results[0].success is False
    assert results[1].success is True
