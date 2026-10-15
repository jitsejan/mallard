"""Shared commands. CI runs the same ones."""

from invoke.context import Context
from invoke.tasks import task


@task
def format(c: Context) -> None:
    c.run("ruff check --fix .")
    c.run("ruff format .")


@task
def lint(c: Context) -> None:
    c.run("ruff check .")
    c.run("ruff format --check .")
    c.run("mypy")


@task
def test(c: Context) -> None:
    c.run("pytest")


@task(pre=[lint, test], default=True)
def check(c: Context) -> None:
    """Everything CI runs."""
